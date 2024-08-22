# main.py
import os
import itertools
import concurrent.futures

from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from lamatidb.interfaces.query_interface import QueryInterface
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.settings_manager import SettingsManager
from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface

from serverfastapi import models, schemas

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

crud = models.crud

# Retry configuration: retries up to 2 times with a wait of 1 second between retries
retry_decorator = retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(1),
    retry=(retry_if_exception_type(OperationalError)),
)

# Dependency for FastAPI to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):

    global tidb_interface
    global get_db
    global index
    global index_fulltext
    global metadata_indexes
    global index_metadata_keys
    global SessionLocal

    # Set global settings
    SettingsManager.set_global_settings()

    # Database and vector table names
    DB_NAME = "scibert_alldata_pico"
    VECTOR_TABLE_NAME = 'scibert_alldata'

    # Initialize Cloud-based TiDB interface and set up the Vectorstore and datastore
    tidb_interface = DatabaseInterface(db_type='tidb', db_name='datastore')

    # Initialize Local MySQL interface and set up the database for operations
    mysql_interface = DatabaseInterface(db_type='mysql', db_name='operations', force_recreate_db=True)
    mysql_interface.setup_database()

    # Create engine, session, and base
    engine = mysql_interface.engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    models.Base.metadata.create_all(bind=engine)

    # Load or create the index
    index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
    index_interface.load_index_from_vector_store()
    index = index_interface.get_index()

    index_interface_fulltext = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+'_fulltext')
    index_interface_fulltext.load_index_from_vector_store()
    index_fulltext = index_interface.get_index()

    # Load PICO indexes
    elements = ['p', 'i', 'c', 'o']
    combinations = []
    for r in range(1, len(elements) + 1):
        combinations += list(itertools.combinations(elements, r))

    metadata_indexes = {}
    index_metadata_keys = []

    # Function to load the index for a given combination
    def load_index(combination):
        key = ''.join(combination)
        index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+f"_{key}")
        index_interface.load_index_from_vector_store()
        return key, index_interface.get_index()

    # Using ThreadPoolExecutor to run the tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks to the executor
        futures = {executor.submit(load_index, comb): comb for comb in combinations}

        # As each task completes, store the result
        for future in concurrent.futures.as_completed(futures):
            key, metadata_index = future.result()
            metadata_indexes[key] = metadata_index
            index_metadata_keys.append(key)

    # CHAT_WITH_DATA_DB = "test"
    # CHAT_WITH_DATA_VECTOR_TABLE_NAME = "Ben_full_docs_v3"
    # CHAT_WITH_DATA_EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"
    # cwd_index_interface = IndexInterface(CHAT_WITH_DATA_DB,CHAT_WITH_DATA_VECTOR_TABLE_NAME,embedding_model_name=CHAT_WITH_DATA_EMBEDDING_MODEL)
    # cwd_index_interface.load_index_from_vector_store()
    # cwd_index = cwd_index_interface.get_index()

    yield  # After this point, the application is running and serving requests

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/projects/{project_id}/search/")
@retry_decorator
def create_query_and_search(project_id: int, query: schemas.QueryCreate, db: Session = Depends(get_db)):
    db_query = crud.create_query(db, query=query)

    query_interface = QueryInterface(index)
    query_interface.configure_retriever(similarity_top_k=None)
    source_nodes = query_interface.retriever.retrieve(query.query_text)
    # query_interface.inspect_similarity_scores(source_nodes) #for debug

    # Find if the documentId has PDF available
    query = "SELECT documentId FROM datastore.DocumentFull"
    fulldoc_result = tidb_interface.fetch_data_from_db(query)
    doc_ids = [x[0] for x in fulldoc_result]
    for source_node in source_nodes:
        source_node.metadata['has_pdf'] = source_node.metadata['source'] in doc_ids

    db_results = crud.create_results(db, source_nodes, db_query)

    # Mock a few with status Screened
    db_results[0].funnel_stage = "Screened"
    db_results[1].funnel_stage = "Screened"
    db_results[2].funnel_stage = "Screened"
    db_results[3].funnel_stage = "Screened"

    db_results[3].is_archived = True
    db_results[8].is_archived = True
    db_results[9].is_archived = True
    db_results[13].is_archived = True

    db.commit()

    return {
        "query": db_query,
        "results": db_results
    }

@app.patch("/projects/{project_id}/documents/{document_ids}/status/{status}")
@retry_decorator
def update_document_status(project_id: int, document_ids, status: str, db: Session = Depends(get_db)):
    # Split the document_ids string into a list of integers
    try:
        document_id_list = [doc_id for doc_id in document_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    # Query to fetch the documents by their IDs
    documents = db.query(models.Result).filter(models.Result.source_id.in_(document_id_list)).all()

    if not documents:
        raise HTTPException(status_code=404, detail="Documents not found")

    # Update the status of each document
    for document in documents:
        document.funnel_stage = status

    db.commit()

    return {"message": "Status updated successfully", "document_ids": document_ids, "new_status": status}

@app.get("/projects/{project_id}/get_status/{status}")
@retry_decorator
def get_status(project_id: int, status: str, archived: bool, db: Session = Depends(get_db)):
    # Changes revert to original...
    query = db.query(models.Result).filter(models.Result.funnel_stage == status)

    if not archived:
        query = query.filter(models.Result.is_archived == False)
                             
    filtered_records = query.all()

    # Query to count the number of documents in each funnel stage, considering the archived parameter
    funnel_count_query = (
        db.query(models.Result.funnel_stage, models.Result.is_archived, func.count(models.Result.funnel_stage))
        .group_by(models.Result.funnel_stage, models.Result.is_archived)
    )

    # Initialize the dictionary with all funnel stages from the enum
    funnel_count_dict = {stage.value: {"archived": 0, "active": 0} for stage in schemas.FunnelEnum}

    # Update the dictionary with actual counts from the query
    for stage, is_reviewed, count in funnel_count_query:
        stage_clean = stage.split('.')[-1]
        key = "archived" if is_reviewed else "active"
        funnel_count_dict[stage_clean][key] = count

    return {
        "status": status,
        "records": filtered_records,
        "funnel_count": funnel_count_dict
    }


@app.post("/projects/{project_id}/semantic_search/")
@retry_decorator
def create_query_and_semantic_search(
    project_id: int, 
    query: schemas.QueryCreate, 
    fields: List[str] = ["All Fields"], 
    source_ids: List[int] = [], 
    db: Session = Depends(get_db)
):

    metadata_mapper = {
        'Patient': 'p',
        'Intervention': 'i',
        'Comparison': 'c',
        'Outcome': 'o'
        }

    # Make sure source_ids is a list of strings
    source_ids = [str(source_id) for source_id in source_ids]
    filters = []

    # Set index to filter
    field = fields[0] # At the moment, just one field is supported
    if field == "Full Document":
        semantic_index = index_fulltext
    elif field != "All Fields":
        index_name = metadata_mapper.get(field, None)
        semantic_index = metadata_indexes.get(index_name)
    else:
        semantic_index = index
    
    if source_ids:
        filters.append({"key": "source", "value": source_ids, "operator": "in"})

    # Initialize the query interface with your index
    query_interface = QueryInterface(semantic_index)
    query_interface.configure_retriever(similarity_top_k=None, metadata_filters=filters)
    retrieved_nodes = query_interface.retriever.retrieve(query.query_text)
    filtered_nodes = query_interface.filter_by_similarity_score(retrieved_nodes, 0.5)
    # query_interface.inspect_similarity_scores(filtered_nodes) #for debug

    # Extract source_ids from the filtered results
    source_ids = [int(node.metadata['source']) for node in filtered_nodes if 'source' in node.metadata]

    # Return the list of source_ids
    return {"source_ids": source_ids} # for some reason need to pass ints to front-end...

@app.post("/projects/{project_id}/chat/document/{document_id}")
def start_streamlit_session(document_id):
    from lamatidb.interfaces.run_streamlit import run
    run("16626815")
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.environ['FASTAPI_HOST'], port=int(os.environ['FASTAPI_PORT']), reload=True)

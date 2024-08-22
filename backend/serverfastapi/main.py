# main.py
import os
import random
import itertools
import concurrent.futures

from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager

from serverfastapi import models, schemas
from serverfastapi.database import get_db, engine

from lamatidb.interfaces.query_interface import QueryInterface
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.settings_manager import SettingsManager

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy.exc import OperationalError

crud = models.crud

# Retry configuration: retries up to 2 times with a wait of 1 second between retries
retry_decorator = retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(1),
    retry=(retry_if_exception_type(OperationalError)),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set global settings
    SettingsManager.set_global_settings()
    models.Base.metadata.create_all(bind=engine)

    # Database and vector table names
    DB_NAME = "scibert_alldata_pico"
    VECTOR_TABLE_NAME = 'scibert_alldata'

    # Load or create the index
    global index
    index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
    index_interface.load_index_from_vector_store()
    index = index_interface.get_index()

    # Load PICO indexes
    elements = ['p', 'i', 'c', 'o']
    combinations = []
    for r in range(1, len(elements) + 1):
        combinations += list(itertools.combinations(elements, r))

    global metadata_indexes
    global index_metadata_keys
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

@app.post("/projects/{project_id}/search/")
@retry_decorator
def create_query_and_search(project_id: int, query: schemas.QueryCreate, db: Session = Depends(get_db)):
    db_query = crud.create_query(db, query=query)
    
    # Vectorize query and retrieve results
    # Initialize the query interface with your index
    query_interface = QueryInterface(index)
    # Example 1.1: More clean for simple semantic search, without synthesiser
    query_interface.configure_retriever(similarity_top_k=None)
    source_nodes = query_interface.retriever.retrieve(query.query_text)
    # query_interface.inspect_similarity_scores(source_nodes) #for debug

    results = [
        schemas.ResultBase(
            source_id = source_node.metadata['source'],
            similarity = source_node.score,
            authors = source_node.metadata['authors'],
            year = source_node.metadata['year'],
            title = source_node.metadata['title'],
            abstract = source_node.text,
            pico_p = source_node.metadata['pico_p'],
            pico_i = source_node.metadata['pico_i'],
            pico_c = source_node.metadata['pico_c'],
            pico_o = source_node.metadata['pico_o'],
            funnel_stage = schemas.FunnelEnum.IDENTIFIED,
            is_archived = random.choice([True, False]),
            has_pdf = random.choice([True, False])
        )
        for source_node in source_nodes
    ]
    db_results = crud.create_results(db, results, db_query)

    # Mock a few with status Screened
    db_results[0].funnel_stage = schemas.FunnelEnum.SCREENED
    db_results[1].funnel_stage = schemas.FunnelEnum.SCREENED
    db_results[2].funnel_stage = schemas.FunnelEnum.SCREENED
    db_results[3].funnel_stage = schemas.FunnelEnum.SCREENED
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
        key = "archived" if is_reviewed else "active"
        funnel_count_dict[schemas.FunnelEnum(stage).value][key] = count

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
    if field != "All Fields":
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
    source_ids = [node.metadata['source'] for node in filtered_nodes if 'source' in node.metadata]

    # Return the list of source_ids
    return {"source_ids": [int(x) for x in source_ids]} # for some reason need to pass ints to front-end...

@app.post("/projects/{project_id}/chat/document/{document_id}")
def start_streamlit_session(document_id):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.environ['FASTAPI_HOST'], port=int(os.environ['FASTAPI_PORT']), reload=True)

# main.py
import os
import random
from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func


from serverfastapi import crud, models, schemas
from serverfastapi.database import get_db, engine

from llama_index.core.query_pipeline import QueryPipeline


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Set up orchestrator (maybe we move to different file)
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.settings_manager import SettingsManager
from lamatidb.interfaces.query_interface import QueryInterface

# Set global settings
SettingsManager.set_global_settings()

# Database and vector table names
DB_NAME = "scibert_alldata_pico" #os.environ['TIDB_DB_NAME'] # set to test_matias as this has data loaded
VECTOR_TABLE_NAME = 'scibert_alldata' #'mocked_data'"scibert_alldata"

# CHAT_WITH_DATA_DB = "test"
# CHAT_WITH_DATA_VECTOR_TABLE_NAME = "Ben_full_docs_v3"
# CHAT_WITH_DATA_EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"

# Load or create the index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
index_interface.load_index_from_vector_store()
index = index_interface.get_index()

# cwd_index_interface = IndexInterface(CHAT_WITH_DATA_DB,CHAT_WITH_DATA_VECTOR_TABLE_NAME,embedding_model_name=CHAT_WITH_DATA_EMBEDDING_MODEL)
# cwd_index_interface.load_index_from_vector_store()
# cwd_index = cwd_index_interface.get_index()

@app.post("/projects/{project_id}/search/")
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
            funnel_stage = models.FunnelEnum.IDENTIFIED,
            is_archived = random.choice([True, False]),
            has_pdf = random.choice([True, False])
        )
        for source_node in source_nodes
    ]
    db_results = crud.create_results(db, results, db_query)

    # Mock a few with status Screened
    db_results[0].funnel_stage = models.FunnelEnum.SCREENED
    db_results[1].funnel_stage = models.FunnelEnum.SCREENED
    db_results[2].funnel_stage = models.FunnelEnum.SCREENED
    db_results[3].funnel_stage = models.FunnelEnum.SCREENED
    db.commit()

    return {
        "query": db_query,
        "results": db_results
    }

@app.patch("/projects/{project_id}/documents/{document_ids}/status/{status}")
def update_document_status(project_id: int, document_ids, status: str, db: Session = Depends(get_db)):
    # Split the document_ids string into a list of integers
    try:
        document_id_list = [int(doc_id) for doc_id in document_ids.split(',')]
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
    funnel_count_dict = {stage.value: {"archived": 0, "active": 0} for stage in models.FunnelEnum}

    # Update the dictionary with actual counts from the query
    for stage, is_reviewed, count in funnel_count_query:
        key = "archived" if is_reviewed else "active"
        funnel_count_dict[models.FunnelEnum(stage).value][key] = count

    return {
        "status": status,
        "records": filtered_records,
        "funnel_count": funnel_count_dict
    }


@app.post("/projects/{project_id}/semantic_search/")
def create_query_and_semantic_search(
    project_id: int, 
    query: schemas.QueryCreate, 
    field_name: str = "All Fields", 
    source_ids: List[int] = [], 
    db: Session = Depends(get_db)
):

    # Make sure source_ids is a list of strings
    source_ids = [str(source_id) for source_id in source_ids]
    filters = []

    # if field_name != "All Fields":
    #     filters.append({"key": field_name, "value": query.query_text, "operator": "contains"})
    
    if source_ids:
        filters.append({"key": "source", "value": source_ids, "operator": "in"})

    # Initialize the query interface with your index
    query_interface = QueryInterface(index)
    query_interface.configure_retriever(similarity_top_k=None, metadata_filters=filters)
    retrieved_nodes = query_interface.retriever.retrieve(query.query_text)
    filtered_nodes = query_interface.filter_by_similarity_score(retrieved_nodes, 0.5)

    # Extract source_ids from the filtered results
    source_ids = [node.metadata['source'] for node in filtered_nodes if 'source' in node.metadata]

    # Return the list of source_ids
    return {"source_ids": source_ids}

@app.post("/projects/{project_id}/chat/document/{document_id}")
def start_streamlit_session(document_id):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.environ['FASTAPI_HOST'], port=int(os.environ['FASTAPI_PORT']), reload=True)

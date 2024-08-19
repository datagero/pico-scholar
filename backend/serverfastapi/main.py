# main.py
import os
from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from serverfastapi import crud, models, schemas
from serverfastapi.database import get_db, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Set up orchestrator (maybe we move to different file)
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.settings_manager import SettingsManager
from lamatidb.interfaces.query_interface import QueryInterface

# Set global settings
SettingsManager.set_global_settings()

# Database and vector table names
DB_NAME = "test_matias" #os.environ['TIDB_DB_NAME'] # set to test_matias as this has data loaded
VECTOR_TABLE_NAME = "scibert_alldata"

CHAT_WITH_DATA_DB = "test"
CHAT_WITH_DATA_VECTOR_TABLE_NAME = "Ben_full_docs_v3"
CHAT_WITH_DATA_EMBEDDING_MODEL = "allenai/scibert_scivocab_uncased"

# Load or create the index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
index_interface.load_index_from_vector_store()
index = index_interface.get_index()

cwd_index_interface = IndexInterface(CHAT_WITH_DATA_DB,CHAT_WITH_DATA_VECTOR_TABLE_NAME,embedding_model_name=CHAT_WITH_DATA_EMBEDDING_MODEL)
cwd_index_interface.load_index_from_vector_store()
cwd_index = cwd_index_interface.get_index()

@app.post("/projects/{project_id}/search/")
def create_query_and_search(project_id: int, query: schemas.QueryCreate, db: Session = Depends(get_db)):
    db_query = crud.create_query(db, query=query)
    
    # Vectorize query and retrieve results
    # Initialize the query interface with your index
    query_interface = QueryInterface(index)
    # Example 1.1: More clean for simple semantic search, without synthesiser
    query_interface.configure_retriever(similarity_top_k=100)
    source_nodes = query_interface.retriever.retrieve(query.query_text)
    # query_interface.inspect_similarity_scores(source_nodes)

    results = [
        schemas.ResultBase(
            source_id = source_node.metadata['source'],
            similarity = source_node.score,
            authors = source_node.metadata['authors'],
            year = source_node.metadata['year'],
            title = source_node.metadata['title'],
            abstract = source_node.text,
            pico_p = "",
            pico_i = "",
            pico_c = "",
            pico_o = "",
            funnel_stage = models.FunnelEnum.IDENTIFIED,
            is_reviewed = False
        )
        for source_node in source_nodes
    ]
    db_results = crud.create_results(db, results, db_query)

    # # Mock a few with status Screened
    # db_results[0].funnel_stage = models.FunnelEnum.SCREENED
    # db_results[1].funnel_stage = models.FunnelEnum.SCREENED
    # db_results[2].funnel_stage = models.FunnelEnum.SCREENED
    # db_results[3].funnel_stage = models.FunnelEnum.SCREENED
    # db.commit()

    return {
        "query": db_query,
        "results": db_results
    }


# @app.post("/projects/{project_id}/get_status/{status}")
# def get_status(project_id: int, status: schemas.QueryCreate, db: Session = Depends(get_db)):
#     filtered_records = db.query(models.Result).filter(models.Result.funnel_stage == status).all()
#     return {
#         "status": status,
#         "records": filtered_records
#     }





def chat_with_documents(query:str, PMID=None)->str:
    query_interface = QueryInterface(cwd_index)
    query_interface.configure_retriever(similarity_top_k=100)
    query_interface.configure_response_synthesizer()
    query_interface.assemble_query_engine()
    if PMID is not None:
        filters = [
        {"key": "PMID", "value": str(PMID), "operator": "=="},
        ]
        response = query_interface.perform_metadata_filtered_query(query, filters)
        
    else:
        response = query_interface.perform_query(query)
    return str(response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.environ['FASTAPI_HOST'], port=int(os.environ['FASTAPI_PORT']), reload=True)

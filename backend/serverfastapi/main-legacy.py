# main.py
import os
import re
import json
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
    mysql_interface = DatabaseInterface(db_type='tidb', db_name='operations', force_recreate_db=True)
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
    index_fulltext = index_interface_fulltext.get_index()

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
        idx_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+f"_{key}")
        idx_interface.load_index_from_vector_store()
        return key, idx_interface.get_index()

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
def create_query_and_search(
    project_id: int, 
    query: schemas.QueryCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new query and perform a search within the project's dataset.

    Args:
        project_id (int): ID of the project where the search is performed.
        query (schemas.QueryCreate): The search query details.
        db (Session): Database session.

    Returns:
        dict: Contains the query details and the search results.
    """
    # Create the query record in the database
    db_query = crud.create_query(db, query=query)

    # Configure and execute the search using the QueryInterface
    query_interface = QueryInterface(index)
    query_interface.configure_retriever(similarity_top_k=None)
    source_nodes = query_interface.retriever.retrieve(query.query_text)

    # Check if documents have a PDF available by comparing with datastore
    query = "SELECT documentId FROM datastore.DocumentFull"
    fulldoc_result = tidb_interface.fetch_data_from_db(query)
    doc_ids = [x[0] for x in fulldoc_result]
    
    for source_node in source_nodes:
        source_node.metadata['has_pdf'] = source_node.metadata['source'] in doc_ids

    # Store the search results in the database
    db_results = crud.create_results(db, source_nodes, db_query)

    print(f"First results: {db_results[0]}")

    # # Mock some results with a 'Screened' status for demonstration
    # for idx in [0, 1, 2, 3]:
    #     db_results[idx].funnel_stage = "Screened"

    # # Archive certain results for demonstration
    # for idx in [3, 8, 9, 13]:
    #     db_results[idx].is_archived = True

    db.commit()

    return {
        "query": db_query.query_text,
        "results": db_results
    }

@app.get("/projects/{project_id}/get_status/{status}")
@retry_decorator
def get_status(
    project_id: int, 
    status: str, 
    archived: bool, 
    db: Session = Depends(get_db)
):
    """
    Retrieve documents within a specific funnel stage and their status.

    Args:
        project_id (int): ID of the project.
        status (str): Funnel stage to filter documents by.
        archived (bool): Whether to include archived documents.
        db (Session): Database session.

    Returns:
        dict: Contains the requested status, filtered records, and a count of documents in each funnel stage.
    """
    # Filter the documents by the given status and archived flag
    query = db.query(models.Result).filter(models.Result.funnel_stage == status)

    if not archived:
        query = query.filter(models.Result.is_archived == False)
                             
    filtered_records = query.all()

    # Count the number of documents in each funnel stage, considering the archived status
    funnel_count_query = (
        db.query(models.Result.funnel_stage, models.Result.is_archived, func.count(models.Result.funnel_stage))
        .group_by(models.Result.funnel_stage, models.Result.is_archived)
    )

    # Initialize a dictionary to hold the counts for each funnel stage
    funnel_count_dict = {stage.value: {"archived": 0, "active": 0} for stage in schemas.FunnelEnum}

    # Update the dictionary with actual counts from the query
    for stage, is_archived, count in funnel_count_query:
        key = "archived" if is_archived else "active"
        funnel_count_dict[stage][key] = count

    return {
        "status": status,
        "records": filtered_records,
        "funnel_count": funnel_count_dict
    }

@app.patch("/projects/{project_id}/documents/{document_ids}/status/{status}")
@retry_decorator
def update_document_status(
    project_id: int, 
    document_ids: str, 
    status: str, 
    db: Session = Depends(get_db)
):
    """
    Update the status of documents within a project.

    Args:
        project_id (int): ID of the project.
        document_ids (str): Comma-separated list of document IDs to update.
        status (str): New status to set for the documents.
        db (Session): Database session.

    Returns:
        dict: Confirmation message with the updated document IDs and new status.
    """
    # Convert the comma-separated document IDs to a list
    try:
        document_id_list = [doc_id.strip() for doc_id in document_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    # Fetch the documents by their IDs
    documents = db.query(models.Result).filter(models.Result.source_id.in_(document_id_list)).all()

    if not documents:
        raise HTTPException(status_code=404, detail="Documents not found")

    # Update the funnel stage of each document
    for document in documents:
        document.funnel_stage = status

    db.commit()

    return {"message": "Status updated successfully", "document_ids": document_ids, "new_status": status}

@app.patch("/projects/{project_id}/document/{document_id}/archive/{is_archived}")
@retry_decorator
def update_document_archived_status(
    project_id: int, 
    document_id: str, 
    is_archived: bool, 
    db: Session = Depends(get_db)
):
    """
    Update the archived status of a single document within a project.

    Args:
        project_id (int): ID of the project to which the document belongs.
        document_id (int): ID of the document to update.
        is_archived (bool): The new archived status (True for archived, False for active).
        db (Session): Database session.

    Returns:
        dict: Confirmation message with the updated document ID and new archived status.
    """
    # Fetch the document by its ID
    document = db.query(models.Result).filter(
        models.Result.source_id == document_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Update the is_archived status of the document
    document.is_archived = is_archived

    db.commit()

    return {
        "message": "Archived status updated successfully", 
        "document_id": document_id, 
        "new_archived_status": is_archived
    }

@app.post("/translate_terms/")
def translate_terms_via_chatgpt(terms: dict, db: Session = Depends(get_db)):
    """
    Translate plain language terms into scientific notation using ChatGPT.

    Args:
        terms (dict): A dictionary of terms to translate. 
                      Example: {"Year of Publication": "After 2010", "P (Population)": "Adults over 25 years"}

    Returns:
        dict: A dictionary where keys are the original terms and values are their scientific notations.
    """
    # Step 1: Format the input for ChatGPT with detailed examples and technical notations
    chatgpt_prompt = (
        "Translate the following plain language terms into scientific notation. "
        "Use appropriate scientific notations such as:\n"
        "- '/' after an index term to indicate that all subheadings were selected.\n"
        "- '*' before an index term to indicate the term was focused (major term).\n"
        "- 'exp' before an index term to indicate the term was exploded.\n"
        "- '.tw.' for title/abstract search, '.mp.' for free text search, '.pt.' for publication type.\n"
        "- '$' for truncation, '?' for wildcards, and 'adj' for adjacency.\n\n"
        "For example, if 'Adult over 25 years' is given, return 'age>=25/class=Adult.tw.'.\n\n"
        "Translate the following keys into scientific notation and match them with their corresponding plain language values:\n\n"
    )

    # Append each term to the prompt in a more structured format
    for key, value in terms.items():
        chatgpt_prompt += f"Key: {key}\nValue: {value}\n"

    chatgpt_prompt += (
        "\Return the output exclusively in JSON format (no other text), where each key is the original plain language term "
        "and the corresponding value is the translated scientific notation. Ensure the JSON structure is as follows:\n"
        "{\n"
        "  'Year of Publication': 'scientific notation here',\n"
        "  'Country of Publication': 'scientific notation here',\n"
        "  'Does the Study use Randomized Trial?': 'scientific notation here',\n"
        "  'P (Population)': 'scientific notation here',\n"
        "  'I (Intervention)': 'scientific notation here',\n"
        "  'C (Comparison)': 'scientific notation here',\n"
        "  'O (Outcome)': 'scientific notation here'\n"
        "}"
    )
    try:
        query_interface = QueryInterface(index)
        response = query_interface.query_chatgpt(chatgpt_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with ChatGPT: {str(e)}")

    translated_dict = {}
    for attempt in range(3):
        try:
            if attempt == 0:
                translated_dict = json.loads(response)
                break
            if attempt == 1:
                match = re.search(r'\{(.*)\}', response, re.DOTALL)
                if match:
                    extracted_text = match.group(0)  # Use group(0) to get the whole match including the braces
                    print(extracted_text)
                else:
                    print("No match found.")
                translated_dict = json.loads(extracted_text)
                break
        except json.JSONDecodeError:
            print("Failed to decode JSON from ChatGPT response. Retrying...")
            if attempt < 2:  # If it's not the last attempt, continue trying
                continue
            else:  # On the third failure, return an error message
                first_term_key = list(terms.keys())[0]  # Get the first key from the input terms
                translated_dict = {
                    first_term_key: "Failed to decode JSON from ChatGPT response. Please try again."
                }

    return {
        "original_terms": terms,
        "scientific_notation": translated_dict
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
    """
    Perform a semantic search within the project's dataset.

    Args:
        project_id (int): ID of the project where the search is performed.
        query (schemas.QueryCreate): The search query details.
        fields (List[str]): Fields to focus the search on.
        source_ids (List[int]): Specific document IDs to include in the search.
        db (Session): Database session.

    Returns:
        dict: Contains the list of document source IDs that match the search criteria.
    """
    # Map PICO fields to corresponding metadata keys
    metadata_mapper = {
        'Patient': 'p',
        'Intervention': 'i',
        'Comparison': 'c',
        'Outcome': 'o'
    }

    # Ensure source_ids are strings for filtering
    source_ids = [str(source_id) for source_id in source_ids]
    filters = []

    # Select the appropriate index based on the field
    field = fields[0] 
    if field == "Full Document":
        semantic_index = index_fulltext
    elif field != "All Fields":
        index_name = metadata_mapper.get(field)
        semantic_index = metadata_indexes.get(index_name)
    else:
        semantic_index = index
    
    if source_ids:
        filters.append({"key": "source", "value": source_ids, "operator": "in"})

    # Initialize the QueryInterface and perform the retrieval
    query_interface = QueryInterface(semantic_index)
    query_interface.configure_retriever(similarity_top_k=None, metadata_filters=filters)
    retrieved_nodes = query_interface.retriever.retrieve(query.query_text)
    
    # Filter results based on similarity score threshold
    filtered_nodes = query_interface.filter_by_similarity_score(retrieved_nodes, 0.5)

    # Extract document source IDs from the filtered results
    source_ids = [int(node.metadata['source']) for node in filtered_nodes if 'source' in node.metadata]

    return {"source_ids": source_ids}

@app.post("/projects/{project_id}/chat/document/{document_id}")
def start_streamlit_session(document_id: int):
    """
    Start a Streamlit session for exploring a specific document.

    Args:
        document_id (int): ID of the document to explore.

    Note:
        This function initiates a Streamlit session by calling an external script.
    """
    from lamatidb.interfaces.run_streamlit import run
    run(str(document_id)) #"16626815"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.environ['FASTAPI_HOST'], port=int(os.environ['FASTAPI_PORT']), reload=True)

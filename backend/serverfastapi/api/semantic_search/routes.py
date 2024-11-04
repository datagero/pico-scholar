# Contains the FastAPI route to handle the HTTP request and invoke the service logic.
import nest_asyncio
import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from serverfastapi.api.semantic_search.schemas import QueryCreate, SemanticQueryCreate, ResultBase, Result
from serverfastapi.api.semantic_search.services import (
    execute_simple_search,
    execute_advanced_search,
    perform_semantic_search,
    create_semantic_query,
    create_semantic_results,
    get_status, 
    update_document_status, 
    update_document_archived_status
)
from serverfastapi.core.db import get_db
from serverfastapi.core.retry import retry_decorator

# Set up logging according to policy
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
nest_asyncio.apply()

router = APIRouter()

@router.post("/projects/{project_id}/simple_search/")#, response_model=QueryResponse)
def create_query_and_search(
    project_id: int,
    query: QueryCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating and executing search for project ID: {project_id}")

    # Retrieve necessary services from app state
    services = request.app.state.services
    index = services["index"]
    datastore_db = services["datastore_db"]
    
    try:
        search_result = execute_simple_search(db, project_id, query, index, datastore_db)
        return search_result
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Search operation failed.")

@router.post("/projects/{project_id}/advanced_search/")
@retry_decorator
def create_advanced_query_and_search(
    project_id: int,
    query: QueryCreate,
    request: Request,
    db: Session = Depends(get_db),
    num_gen_queries: Optional[int] = 3
):
    logger.info(f"Creating and executing advanced search for project ID: {project_id}")

    # Retrieve necessary services from app state
    services = request.app.state.services
    index = services["index"]
    datastore_db = services["datastore_db"]

    try:
        # Perform the advanced search
        search_result = execute_advanced_search(
            db=db,
            project_id=project_id,
            query=query,
            index=index,
            datastore_db=datastore_db,
            num_gen_queries=num_gen_queries
        )
        return search_result
    except Exception as e:
        logger.error(f"Advanced search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Advanced search operation failed.")

@router.post("/projects/{project_id}/semantic_search/")#, response_model=QueryResponse)
def create_query_and_semantic_search(
    project_id: int,
    query: SemanticQueryCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    logger.info(f"Starting semantic search for project ID: {project_id}")

    services = request.app.state.services
    
    try:
        db_query = create_semantic_query(db, query)
        results = perform_semantic_search(query.query_text, query.fields, query.source_ids, services)
        create_semantic_results(db, results, db_query)
        
        return {
            "query": db_query.query_text,
            "results": results
        }
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Semantic search operation failed.")

@router.get("/projects/{project_id}/get_status/{status}")#, response_model=List[Result])
def get_status_endpoint(project_id: int, status: str, archived: bool, db: Session = Depends(get_db)):
    logger.info(f"Fetching status '{status}' for project ID: {project_id} (Archived: {archived})")
    results = get_status(db, status=status, archived=archived)
    if not results:
        logger.warning(f"No results found for status '{status}' in project ID: {project_id}")
        raise HTTPException(status_code=404, detail="No results found")
    logger.info(f"Retrieved {len(results)} results for status '{status}'.")
    return results

@router.patch("/projects/{project_id}/documents/{document_ids}/status/{status}")
def update_document_status_endpoint(project_id: int, document_ids: str, status: str, db: Session = Depends(get_db)):
    logger.info(f"Updating status for documents in project ID: {project_id} to '{status}'")

    try:
        document_id_list = [doc_id.strip() for doc_id in document_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    updated_documents = update_document_status(db, document_id_list, status)
    logger.info(f"Updated status for {len(updated_documents)} documents.")
    return {"message": "Status updated", "updated_documents": updated_documents}

@router.patch("/projects/{project_id}/document/{document_id}/archive/{is_archived}")
def update_document_archived_status_endpoint(project_id: int, document_id: int, is_archived: bool, db: Session = Depends(get_db)):
    logger.info(f"Updating archive status for document ID: {document_id} in project ID: {project_id}")
    document = update_document_archived_status(db, document_id, is_archived)
    if not document:
        logger.error(f"Document ID: {document_id} not found in project ID: {project_id}")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info(f"Archived status updated for document ID: {document_id}")
    return {"message": "Archived status updated", "document_id": document_id, "new_archived_status": is_archived}

import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List
from lamatidb.interfaces.index_interface import IndexInterface
from serverfastapi.api.rag_system.services import summarize_documents_by_ids, init_document_chat_by_id, query_docu_chat
#, chat_with_document_by_id, expand_query_with_alternatives
from serverfastapi.api.rag_system.schemas import SummarizeRequest, SummarizeResponse, ChatResponse, ChatRequest
from serverfastapi.core.db import get_db

# Set up logging according to policy
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

router = APIRouter()
    
@router.post("/projects/{project_id}/docu_chat/query_bot", response_model=ChatResponse)
def query_document_chat_endpoint(
    project_id: int,
    query: str,
    document_id: int, 
    request: Request,
    ):
    """
    Endpoint to query the document chat engine
    """
    if not hasattr(request.app.state, 'chat_engine'):
        services = request.app.state.services
        index = services["index"]
        request.app.state.chat_engine = init_document_chat_by_id(document_id, index) # To initialize documents of different ids that may require some meta data storage
    try:
        chat_engine = request.app.state.chat_engine
        response = query_docu_chat(query=query, chat_engine=chat_engine)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")


@router.post("/projects/{project_id}/summarize/", response_model=SummarizeResponse)
def summarize_documents_endpoint(
    project_id: int,
    doc_ids: List[int],
    request: Request,
    ):
    """
    Endpoint to summarize the combined content of multiple document IDs.
    """

    """
    Generate and return summary top ten documents for a project
    Args:
        project_id (int): ID of the project where the search is performed
        doc_ids (List[int]): List of top 10 document IDs from the search
    """

    logger.info(f"Creating and executing summarization for project ID: {project_id}")

    # Retrieve necessary services from app state
    services = request.app.state.services
    index = services["index"]

    try:
        response = summarize_documents_by_ids(doc_ids, index)

        return {
            "summary": response
        }
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during summarization")

# @router.post("/rag/chat/")
# def chat_with_document_endpoint(document_id: int, question: str, db: Session = Depends(get_db)):
#     """
#     Endpoint to chat with a specific document by ID.
#     """
#     try:
#         answer = chat_with_document_by_id(db, document_id, question)
#         return {"answer": answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/rag/expand_query/")
# def expand_query_endpoint(initial_query: str):
#     """
#     Endpoint to generate query expansion alternatives.
#     """
#     try:
#         alternative_queries = expand_query_with_alternatives(initial_query)
#         return {"alternatives": alternative_queries}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

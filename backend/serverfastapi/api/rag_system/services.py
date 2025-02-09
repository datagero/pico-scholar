from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from lamatidb.interfaces.query_interface import QueryInterface
from llama_index.core.vector_stores import FilterCondition
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters
# from some_chat_module import chat_with_document
# from some_query_expansion_module import expand_query

def summarize_documents_by_ids(
        document_ids: List[str],
        index: QueryInterface, 
        ) -> str:
    """
    Summarizes the combined content of multiple documents identified by their IDs.
    """
    filters = [
        {
            "key": "source", 
            "value": str(doc_id), # check if this shows up as a str
            "operator": "==",
        } for doc_id in document_ids
    ]

    # Initialize and configure QueryInterface
    sum_query_interface = QueryInterface(index)
    sum_query_interface.configure_retriever(similarity_top_k=10, metadata_filters=filters, condition=FilterCondition.OR) # when db scales up may need to increase top_k
    sum_query_interface.configure_response_synthesizer()
    sum_query_interface.assemble_query_engine()
        
    prompt = f"""You are a skilled researcher and summarization expert. Your task is to summarize the academic articles based on their abstracts into one cohesive description. Each article may come from a different field or focus on different aspects (theory, experiments, reviews, etc.), so ensure your summary reflects the key points accurately for each one.  
    Form a cohesive paragraph that explains what the abstracts are generally about. Ensure you encapsulate the following topics from each of the abstracts:
    1. Discipline or Topic: Identify the general areas of exploration for each abstract, if many overlap just include the overlapping topic once
    2. Objective or Focus: Describe the main question, objective, or hypothesis the articles.
    3. Methodology or Approach: Mention the type of study (e.g., experiment, survey, case study, literature review) and any notable techniques used.
    Be concise but thorough, extracting only the most important information from the abstracts. Do not list each article one at a time but rather refer to the general idea of all articles. Keep your summary to a maximum of 75 words."""

    response = sum_query_interface.perform_query(prompt)
    return response.response # returns just the response from the chatbot without the metadata and excess information

def init_document_chat_by_id(document_id: int, index: QueryInterface) -> str:
    """
    Initializes bot chatting with a specific document by ID.
    """
    doc_chat_interface = QueryInterface(index)
    doc_chat_interface.configure_document_chat(document_id)
    return doc_chat_interface

def query_docu_chat(query: str, chat_engine: QueryInterface):
    """
    Queries chatbot for a single response
    """
    response = chat_engine.query_document_chat(query) # Tested for chat history memory between queries and it passes
    return response.response 


# def expand_query_with_alternatives(initial_query: str) -> List[str]:
#     """
#     Generates query alternatives for query expansion.
#     """
#     alternative_queries = expand_query(initial_query)  # Use your query expansion method
#     return alternative_queries

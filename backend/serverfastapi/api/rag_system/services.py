from cachetools import cached, TTLCache
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from lamatidb.interfaces.query_interface import QueryInterface
from llama_index.core.vector_stores import FilterCondition
# from some_chat_module import chat_with_document
# from some_query_expansion_module import expand_query

# Create a TTL cache for caching results with a 5-minute expiration
cache = TTLCache(maxsize=100, ttl=300)

def cache_key(document_ids: List[str]):
    """
    Creates a unique key for caching based on document_ids.
    """
    return tuple(sorted(document_ids))  # Sorting to handle order variations

#NOTE - Cache not tested, may need to be adjusted
@cached(cache, key=lambda document_ids, index: cache_key(document_ids))
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

    if not filters:
        return "No documents to summarize."

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
    return response.response

# def chat_with_document_by_id(db: Session, document_id: int, question: str) -> str:
#     """
#     Allows chatting with a specific document by ID.
#     """
#     document = get_document_by_id(db, document_id)
#     answer = chat_with_document(document.content, question)  # Use your chat method
#     return answer

# def expand_query_with_alternatives(initial_query: str) -> List[str]:
#     """
#     Generates query alternatives for query expansion.
#     """
#     alternative_queries = expand_query(initial_query)  # Use your query expansion method
#     return alternative_queries

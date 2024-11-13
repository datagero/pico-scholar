# This file will handle the core logic, including creating queries, retrieving documents, checking metadata, and storing results.

from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from serverfastapi.api.semantic_search.models import Query, Result, SemanticQuery, SemanticResult
from serverfastapi.api.semantic_search.schemas import QueryCreate, SemanticQueryCreate, FunnelEnum
from lamatidb.interfaces.query_interface import QueryInterface
from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface
from serverfastapi.core.logger import logger
from sqlalchemy import func

def execute_simple_search(
    db: Session, 
    project_id: int,
    query: QueryCreate, 
    index: QueryInterface, 
    datastore_db: DatabaseInterface
) -> dict:
    """
    Perform a standard search and store results in the database.
    """
    logger.info("Creating query record in database.")
    db_query = create_query(db, project_id, query=query)

    # Configure and execute the search
    query_interface = QueryInterface(index)
    query_interface.configure_retriever(similarity_top_k=None)
    logger.info("Executing search.")
    source_nodes = query_interface.retriever.retrieve(query.query_text)

    # Check if documents have a PDF available by querying the datastore
    logger.info("Checking for PDF availability in datastore.")
    pdf_check_query = "SELECT documentId FROM datastore.DocumentFull"
    fulldoc_result = datastore_db.fetch_data_from_db(pdf_check_query)
    doc_ids_with_pdf = {x[0] for x in fulldoc_result}

    for source_node in source_nodes:
        source_node.metadata['has_pdf'] = source_node.metadata['source'] in doc_ids_with_pdf

    # Store the search results in the database
    orm_results = create_results(db, source_nodes, db_query)
    db.commit()

    return {
        "query": db_query.query_text,
        "results": [result.to_dict() for result in orm_results[:5]]
    }

def execute_advanced_search(
    db: Session, 
    project_id: int,
    query: QueryCreate, 
    index: QueryInterface, 
    datastore_db: DatabaseInterface,
    num_gen_queries: int = 3
) -> Dict:
    """
    Generate additional queries based on the input query, perform a search, 
    and store results in the database.
    """
    logger.info("Creating query record in database.")
    db_query = create_query(db, query=query)

    # Configure and execute the search using the QueryInterface
    query_interface = QueryInterface(index)
    query_interface.configure_advanced_retriever(similarity_top_k=100, num_queries = num_gen_queries + 1)
    logger.info("Executing search with advanced retriever.")
    source_nodes = query_interface.retriever.retrieve(query.query_text)

    # Check if documents have a PDF available in the datastore
    logger.info("Checking for PDF availability in datastore.")
    pdf_check_query = "SELECT documentId FROM datastore.DocumentFull"
    fulldoc_result = datastore_db.fetch_data_from_db(pdf_check_query)
    doc_ids_with_pdf = {x[0] for x in fulldoc_result}

    for source_node in source_nodes:
        source_node.metadata['has_pdf'] = source_node.metadata['source'] in doc_ids_with_pdf

    # Store the search results in the database
    orm_results = create_results(db, source_nodes, db_query)
    db.commit()

    return {
        "query": db_query.query_text,
        "results": [result.to_dict() for result in orm_results]
    }

def perform_semantic_search(
    query_text: str,
    fields: List[str],
    source_ids: List[int],
    services: Dict
) -> List[Dict[str, Optional[int]]]:
    """
    Perform a semantic search and return document source IDs.
    """
    semantic_index = get_index_for_field(fields, services)
    filters = [{"key": "source", "value": source_ids, "operator": "in"}] if source_ids else []
    query_interface = QueryInterface(semantic_index)
    query_interface.configure_retriever(metadata_filters=filters)
    retrieved_nodes = query_interface.retriever.retrieve(query_text)
    filtered_nodes = query_interface.filter_by_similarity_score(retrieved_nodes, 0.5)

    return [
        int(node.metadata["source"]) for node in filtered_nodes if "source" in node.metadata
    ]

def create_query(db: Session, project_id: int, query: QueryCreate) -> Query:
    """
    Create a standard query record in the database.
    """
    db_query = Query(query_text=query.query_text, project_id=project_id)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def create_semantic_query(db: Session, query: SemanticQueryCreate) -> SemanticQuery:
    """
    Create a semantic query record in the database.
    """
    db_query = SemanticQuery(query_text=query.query_text, fields=query.fields, source_ids=query.source_ids)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def create_results(db: Session, results: list, db_query: Query) -> List[Result]:
    """
    Insert search results into the Result table for a given query.
    """
    result_objects = [
        Result(
            query_id=db_query.id,
            source_id=source_node.metadata['source'],
            similarity=source_node.score,
            authors=source_node.metadata['authors'],
            year=source_node.metadata['year'],
            title=source_node.metadata['title'],
            abstract=source_node.text,
            pico_p=source_node.metadata['pico_p'],
            pico_i=source_node.metadata['pico_i'],
            pico_c=source_node.metadata['pico_c'],
            pico_o=source_node.metadata['pico_o'],
            funnel_stage="Identified",
            is_archived=False,
            has_pdf=source_node.metadata['has_pdf']
        )
        for source_node in results
    ]
    db.bulk_save_objects(result_objects)
    db.commit()
    logger.info(f"Stored {len(result_objects)} search results in the database.")
    return result_objects

def create_semantic_results(db: Session, source_ids: list, db_semantic_query: SemanticQuery) -> None:
    """
    Insert results for a semantic query into the SemanticResult table.
    """
    semantic_result = SemanticResult(
        semantic_query_id=db_semantic_query.id,
        source_ids=source_ids
    )
    db.add(semantic_result)
    db.commit()

# Access the necessary indexes and services from the app state
def get_index_for_field(fields: List[str], services: Dict) -> QueryInterface:
    """
    Determine the appropriate index based on the search field.

    Args:
        fields (List[str]): List of search fields.
        services (Dict): Dictionary of initialized services and indexes.

    Returns:
        QueryInterface: The appropriate query interface for the given field.
    """
    metadata_mapper = {
        'Patient': 'p',
        'Intervention': 'i',
        'Comparison': 'c',
        'Outcome': 'o'
    }

    field = fields[0]
    if field == "Full Document":
        return services["index_fulltext"]
    elif field != "All Fields":
        index_name = metadata_mapper.get(field)
        return services["metadata_indexes"].get(index_name, services["index"])
    else:
        return services["index"]


def get_status(
    db: Session, 
    status: str, 
    archived: bool
):
    """
    Retrieve documents within a specific funnel stage and their status.
    
    Args:
        status (str): Funnel stage to filter documents by.
        archived (bool): Whether to include archived documents.
        db (Session): Database session.
    
    Returns:
        dict: Contains the requested status, filtered records, and a count of documents in each funnel stage.
    """
    # Filter documents by the specified status and archived flag
    query = db.query(Result).filter(Result.funnel_stage == status)
    
    if not archived:
        query = query.filter(Result.is_archived == False)
        
    filtered_records = query.all()

    # Count documents in each funnel stage, grouped by archived status
    funnel_count_query = (
        db.query(Result.funnel_stage, Result.is_archived, func.count(Result.funnel_stage))
        .group_by(Result.funnel_stage, Result.is_archived)
    )
    
    # Initialize a dictionary with counts for each funnel stage
    funnel_count_dict = {stage.value: {"archived": 0, "active": 0} for stage in FunnelEnum}
    
    # Update dictionary with actual counts from the query results
    for stage, is_archived, count in funnel_count_query:
        key = "archived" if is_archived else "active"
        funnel_count_dict[stage][key] = count
    
    return {
        "status": status,
        "records": [result.to_dict() for result in filtered_records],
        "funnel_count": funnel_count_dict
    }

def update_document_status(db: Session, document_ids: List[int], status: str):
    """Update the status of multiple documents."""
    documents = db.query(Result).filter(Result.source_id.in_(document_ids)).all()
    for document in documents:
        document.funnel_stage = status
    db.commit()
    return documents

def update_document_archived_status(db: Session, document_id: int, is_archived: bool):
    """Update the archived status of a single document."""
    document = db.query(Result).filter(Result.source_id == document_id).first()
    if document:
        document.is_archived = is_archived
        db.commit()
    return document

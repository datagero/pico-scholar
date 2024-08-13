import connexion
import six
from flask import jsonify

from swagger_server.models.document_chat_response import DocumentChatResponse  # noqa: E501
from swagger_server.models.document_id_chat_body import DocumentIdChatBody  # noqa: E501
from swagger_server.models.funnel_reviewed_body import FunnelReviewedBody  # noqa: E501
from swagger_server.models.funnel_status import FunnelStatus  # noqa: E501
from swagger_server.models.funnel_status_body import FunnelStatusBody  # noqa: E501
from swagger_server.models.project import Project  # noqa: E501
from swagger_server.models.project_id_add_search_query_body import ProjectIdAddSearchQueryBody  # noqa: E501
from swagger_server.models.project_id_search_body import ProjectIdSearchBody  # noqa: E501
from swagger_server.models.query_id_search_body import QueryIdSearchBody  # noqa: E501
from swagger_server.models.search_query_history import SearchQueryHistory  # noqa: E501
from swagger_server.models.search_result import SearchResult  # noqa: E501
from swagger_server import util


def documents_document_id_chat_post(body, document_id):  # noqa: E501
    """Chat with a specific document

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param document_id: 
    :type document_id: str

    :rtype: DocumentChatResponse
    """
    if connexion.request.is_json:
        body = DocumentIdChatBody.from_dict(connexion.request.get_json())  # noqa: E501
    return jsonify({"response": "This is a hardcoded response to your question for document {}".format(document_id)}), 200


def projects_get():  # noqa: E501
    """Get a list of all available project IDs and Names

     # noqa: E501


    :rtype: List[Project]
    """
    return jsonify([
        {"projectId": "1", "name": "Test Project 1"},
        {"projectId": "2", "name": "Test Project 2"}
    ]), 200


def projects_project_id_add_search_query_post(body, project_id):  # noqa: E501
    """Add a search query to the history

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param project_id: 
    :type project_id: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = ProjectIdAddSearchQueryBody.from_dict(connexion.request.get_json())  # noqa: E501
    return jsonify({"message": "Search query added to project {}".format(project_id)}), 201


def projects_project_id_get(project_id):  # noqa: E501
    """Get search query history for a given project

     # noqa: E501

    :param project_id: 
    :type project_id: str

    :rtype: SearchQueryHistory
    """
    return jsonify({
        "projectId": project_id,
        "queryId": "123",
        "query": "Example query",
        "timestamp": "2024-01-01T00:00:00Z"
    },
    {
        "projectId": project_id,
        "queryId": "234",
        "query": "Example query",
        "timestamp": "2024-01-02T00:00:00Z"
    }), 200


def projects_project_id_query_query_id_data_post(project_id, query_id):  # noqa: E501
    """Retrieve data for a specific search query

     # noqa: E501

    :param project_id: 
    :type project_id: str
    :param query_id: 
    :type query_id: str

    :rtype: List[SearchResult]
    """
    return jsonify([
        {"id": "doc1", "title": "Document 1", "author": "Author 1", "year": 2023, "abstract": "Abstract 1"},
        {"id": "doc2", "title": "Document 2", "author": "Author 2", "year": 2022, "abstract": "Abstract 2"}
    ]), 200


def projects_project_id_query_query_id_funnel_overview_get(project_id, query_id):  # noqa: E501
    """Get funnel statuses and item counts

     # noqa: E501

    :param project_id: 
    :type project_id: str
    :param query_id: 
    :type query_id: str

    :rtype: List[FunnelStatus]
    """
    return jsonify([
        {"status": "screened", "count": 10},
        {"status": "reviewed", "count": 5}
    ]), 200


def projects_project_id_query_query_id_funnel_reviewed_patch(body, project_id, query_id):  # noqa: E501
    """Bulk update the reviewed marker of selected records

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param project_id: 
    :type project_id: str
    :param query_id: 
    :type query_id: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = FunnelReviewedBody.from_dict(connexion.request.get_json())  # noqa: E501
    return jsonify({"message": "Reviewed markers updated for project {} and query {}".format(project_id, query_id)}), 200


def projects_project_id_query_query_id_funnel_status_get(project_id, query_id, status):  # noqa: E501
    """Get records filtered by funnel status

     # noqa: E501

    :param project_id: 
    :type project_id: str
    :param query_id: 
    :type query_id: str
    :param status: 
    :type status: str

    :rtype: List[SearchResult]
    """
    return jsonify([
        {"id": "doc1", "title": "Document 1", "author": "Author 1", "year": 2023, "abstract": "Abstract 1"},
        {"id": "doc2", "title": "Document 2", "author": "Author 2", "year": 2022, "abstract": "Abstract 2"}
    ]), 200


def projects_project_id_query_query_id_funnel_status_patch(body, project_id, query_id):  # noqa: E501
    """Bulk update the status of selected records

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param project_id: 
    :type project_id: str
    :param query_id: 
    :type query_id: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = FunnelStatusBody.from_dict(connexion.request.get_json())  # noqa: E501
    return jsonify({"message": "Statuses updated for project {} and query {}".format(project_id, query_id)}), 200


def projects_project_id_query_query_id_search_post(body, project_id, query_id):  # noqa: E501
    """Perform a semantic search on the records

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param project_id: 
    :type project_id: str
    :param query_id: 
    :type query_id: str

    :rtype: List[str]
    """
    if connexion.request.is_json:
        body = QueryIdSearchBody.from_dict(connexion.request.get_json())  # noqa: E501
    return jsonify(["doc1", "doc2"]), 200


def projects_project_id_search_post(body, project_id):  # noqa: E501
    """Perform a research query vector search

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param project_id: 
    :type project_id: str

    :rtype: List[SearchResult]
    """
    if connexion.request.is_json:
        body = ProjectIdSearchBody.from_dict(connexion.request.get_json())  # noqa: E501
    return jsonify([
        {"id": "doc1", "title": "Document 1", "author": "Author 1", "year": 2023, "abstract": "Abstract 1"},
        {"id": "doc2", "title": "Document 2", "author": "Author 2", "year": 2022, "abstract": "Abstract 2"}
    ]), 200


def swagger_server_controllers_test_controller_root_get():  # noqa: E501
    """Root path

    This is the root of the API # noqa: E501


    :rtype: None
    """
    return jsonify({"message": "This is the root of the API"}), 200

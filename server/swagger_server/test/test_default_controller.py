# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

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
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_documents_document_id_chat_post(self):
        """Test case for documents_document_id_chat_post

        Chat with a specific document
        """
        body = DocumentIdChatBody()
        response = self.client.open(
            '//documents/{documentId}/chat'.format(document_id='document_id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_get(self):
        """Test case for projects_get

        Get a list of all available project IDs and Names
        """
        response = self.client.open(
            '//projects',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_add_search_query_post(self):
        """Test case for projects_project_id_add_search_query_post

        Add a search query to the history
        """
        body = ProjectIdAddSearchQueryBody()
        response = self.client.open(
            '//projects/{projectId}/add_searchQuery'.format(project_id='project_id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_get(self):
        """Test case for projects_project_id_get

        Get search query history for a given project
        """
        response = self.client.open(
            '//projects/{projectId}'.format(project_id='project_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_query_query_id_data_post(self):
        """Test case for projects_project_id_query_query_id_data_post

        Retrieve data for a specific search query
        """
        response = self.client.open(
            '//projects/{projectId}/query/{queryId}/data'.format(project_id='project_id_example', query_id='query_id_example'),
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_query_query_id_funnel_overview_get(self):
        """Test case for projects_project_id_query_query_id_funnel_overview_get

        Get funnel statuses and item counts
        """
        response = self.client.open(
            '//projects/{projectId}/query/{queryId}/funnel_overview'.format(project_id='project_id_example', query_id='query_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_query_query_id_funnel_reviewed_patch(self):
        """Test case for projects_project_id_query_query_id_funnel_reviewed_patch

        Bulk update the reviewed marker of selected records
        """
        body = FunnelReviewedBody()
        response = self.client.open(
            '//projects/{projectId}/query/{queryId}/funnel/reviewed'.format(project_id='project_id_example', query_id='query_id_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_query_query_id_funnel_status_get(self):
        """Test case for projects_project_id_query_query_id_funnel_status_get

        Get records filtered by funnel status
        """
        response = self.client.open(
            '//projects/{projectId}/query/{queryId}/funnel/{status}'.format(project_id='project_id_example', query_id='query_id_example', status='status_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_query_query_id_funnel_status_patch(self):
        """Test case for projects_project_id_query_query_id_funnel_status_patch

        Bulk update the status of selected records
        """
        body = FunnelStatusBody()
        response = self.client.open(
            '//projects/{projectId}/query/{queryId}/funnel/status'.format(project_id='project_id_example', query_id='query_id_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_query_query_id_search_post(self):
        """Test case for projects_project_id_query_query_id_search_post

        Perform a semantic search on the records
        """
        body = QueryIdSearchBody()
        response = self.client.open(
            '//projects/{projectId}/query/{queryId}/search'.format(project_id='project_id_example', query_id='query_id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_id_search_post(self):
        """Test case for projects_project_id_search_post

        Perform a research query vector search
        """
        body = ProjectIdSearchBody()
        response = self.client.open(
            '//projects/{projectId}/search'.format(project_id='project_id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_swagger_server_controllers_default_controller_root_get(self):
        """Test case for swagger_server_controllers_default_controller_root_get

        Root path
        """
        response = self.client.open(
            '//',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

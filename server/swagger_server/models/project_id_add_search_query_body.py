# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectIdAddSearchQueryBody(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, query: str=None):  # noqa: E501
        """ProjectIdAddSearchQueryBody - a model defined in Swagger

        :param query: The query of this ProjectIdAddSearchQueryBody.  # noqa: E501
        :type query: str
        """
        self.swagger_types = {
            'query': str
        }

        self.attribute_map = {
            'query': 'query'
        }
        self._query = query

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectIdAddSearchQueryBody':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projectId_add_searchQuery_body of this ProjectIdAddSearchQueryBody.  # noqa: E501
        :rtype: ProjectIdAddSearchQueryBody
        """
        return util.deserialize_model(dikt, cls)

    @property
    def query(self) -> str:
        """Gets the query of this ProjectIdAddSearchQueryBody.

        The search query to add to history  # noqa: E501

        :return: The query of this ProjectIdAddSearchQueryBody.
        :rtype: str
        """
        return self._query

    @query.setter
    def query(self, query: str):
        """Sets the query of this ProjectIdAddSearchQueryBody.

        The search query to add to history  # noqa: E501

        :param query: The query of this ProjectIdAddSearchQueryBody.
        :type query: str
        """

        self._query = query

# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from web_api.models.check import Check  # noqa: E501
from web_api.models.inv_par import InvPar  # noqa: E501
from web_api.models.result import Result  # noqa: E501
from web_api.test import BaseTestCase


class TestQueryController(BaseTestCase):
    """QueryController integration test stubs"""

    def test_test_servers(self):
        """Test case for test_servers

        Send a query to the backend to test name servers
        """
        body = Check()
        response = self.client.open(
            '/v1/check',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

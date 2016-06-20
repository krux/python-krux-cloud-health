# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest
import sys

#
# Third party libraries
#

from mock import MagicMock, patch

#
# Internal libraries
#

from krux_cloud_health.CloudAPI import CloudAPI


class CloudAPItest(unittest.TestCase):
    """
        Test case for CloudAPI
    """
    # Replace '12345' with your own API key
    @patch.object(sys, 'argv', ['placeholder', '--api-key', '12345'])
    @patch('krux_cloud_health.CloudAPI.requests')
    def test_cloud_health_call(self, mock_requests):

        mock_requests.get.return_value.json.return_value = {
            'dimensions': [
                {
                    'time': [
                        {'name': '2016-05'},
                        {'name': '2016-06'}
                    ]
                },
                {
                    'AWS-Service-Category': [
                        {'label': 'Label-1'},
                        {'label': 'Label-2'}
                    ]
                }
            ],
            'data': [
                [
                    ['a'],
                    ['b']
                ],
                [
                    ['c'],
                    ['d']
                ]
            ]
        }

        test_case = CloudAPI()
        test_case.run()

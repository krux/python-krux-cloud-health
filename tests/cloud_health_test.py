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

from krux.cli import get_parser, get_group
from krux.stats import DummyStatsClient
from krux_cloud_health.cloud_health import CloudHealth, get_cloud_health, Interval, NAME


class CloudHealthTest(unittest.TestCase):

    API_KEY = '12345'
    COST_HISTORY_REPORT = 'olap_reports/cost/history'
    COST_CURRENT_REPORT = 'olap_reports/cost/current'
    
    @patch('krux_cloud_health.cloud_health.get_stats')
    @patch('krux_cloud_health.cloud_health.get_logger')
    def setUp(self, mock_logger, mock_stats):
        self.mock_logger = mock_logger
        self.mock_stats = mock_stats
        self.cloud_health = CloudHealth(CloudHealthTest.API_KEY, self.mock_logger, self.mock_stats)

    @patch('krux_cloud_health.cloud_health.get_stats')
    @patch('krux_cloud_health.cloud_health.get_logger')
    @patch('krux_cloud_health.cloud_health.get_parser')
    @patch('krux_cloud_health.cloud_health.CloudHealth')
    def test_get_cloud_health_no_args(self, mock_cloud_health, mock_parser, mock_logger, mock_stats):
        mock_parser.return_value.parse_args.return_value = MagicMock(api_key=CloudHealthTest.API_KEY)
        cloud_health = get_cloud_health()
        mock_cloud_health.assert_called_once_with(
            api_key = CloudHealthTest.API_KEY,
            logger=mock_logger(name=NAME),
            stats=mock_stats(prefix=NAME),
            )

    def test_cost_history(self):
        self.cloud_health._get_api_call = MagicMock()
        cost_history = self.cloud_health.cost_history(Interval['daily'], 'time_input')
        self.cloud_health._get_api_call.assert_called_once_with(
            CloudHealthTest.COST_HISTORY_REPORT,
            CloudHealthTest.API_KEY,
            {'interval': 'daily', 'filters[]': 'time:select:time_input'},
            )

    def test_cost_current(self):
        self.cloud_health._get_api_call = MagicMock()
        cost_current = self.cloud_health.cost_current()
        self.cloud_health._get_api_call.assert_called_once_with(
            CloudHealthTest.COST_CURRENT_REPORT,
            CloudHealthTest.API_KEY
            )

    @patch('krux_cloud_health.cloud_health.pprint.pformat')
    @patch('krux_cloud_health.cloud_health.requests')
    def test_get_api_call(self, mock_request, mock_pprint):
        api_call = {'api_call': 'return'}
        mock_request.get.return_value.json.return_value = api_call
        get_api_call = self.cloud_health._get_api_call(CloudHealthTest.COST_HISTORY_REPORT, CloudHealthTest.API_KEY)
        mock_pprint.assert_called_once_with(api_call)
        self.cloud_health.logger.debug.assert_called_once_with(mock_pprint(api_call))

    @patch('krux_cloud_health.cloud_health.requests')
    def test_get_api_call_error(self, mock_request):
        api_call = {'error': 'Error message'}
        mock_request.get.return_value.json.return_value = api_call
        with self.assertRaises(ValueError):
            get_api_call = self.cloud_health._get_api_call(CloudHealthTest.COST_HISTORY_REPORT, CloudHealthTest.API_KEY)

    def test_get_data(self):
        api_call = {'dimensions':
            [
                {'time': 
                    [
                        {'label': 'Total'},
                    ]
                },
                {'AWS-Service-Category': 
                    [
                        {'label': 'service'} 
                    ]
                }
            ]
        }
        self.cloud_health._get_data_info = MagicMock()
        get_data = self.cloud_health._get_data(api_call, 'time')
        self.cloud_health._get_data_info.assert_called_once_with(api_call, [{'label': 'service'}], 'Total', 0)


    def test_get_data_info(self):
        api_call = {'data': [
                [
                    [100]
                ]
            ]
        }
        get_data_info = self.cloud_health._get_data_info(api_call, [{'label': 'service', 'parent': 1}], 'Total', 0)
        self.assertEqual(get_data_info, {'Total': {'service': 100}})

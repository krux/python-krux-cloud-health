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
    API_ENDPOINT = 'https://apps.cloudhealthtech.com/'
    COST_HISTORY_URI = '{}{}'.format(API_ENDPOINT, COST_HISTORY_REPORT)
    URI_ARGS_NO_PARAMS = {'api_key': API_KEY}
    TIME_INTERVAL = Interval['daily']
    TIME_INPUT = 'time_input'
    COST_HISTORY_CATEGORY_TYPE = 'time'
    COST_CURRENT_CATEGORY_TYPE = 'AWS-Account'
    PARAMS_INTERVAL = {'interval': 'daily'} 
    PARAMS_TIME_INPUT = {'interval': 'daily', 'filters[]': 'time:select:{}'.format(TIME_INPUT)}
    API_CALL = {'api_call': 'return'}
    API_CALL_ERROR = {'error': 'Error message'} 
    
    def setUp(self):
        self.cloud_health = get_cloud_health(args=MagicMock(api_key=CloudHealthTest.API_KEY))

    @patch('krux_cloud_health.cloud_health.get_stats')
    @patch('krux_cloud_health.cloud_health.get_logger')
    @patch('krux_cloud_health.cloud_health.get_parser')
    @patch('krux_cloud_health.cloud_health.CloudHealth')
    def test_get_cloud_health_no_args(self, mock_cloud_health, mock_parser, mock_logger, mock_stats):
        """
        Cloud Health Test: All arguments created and passed into CloudHealth if none are provided.
        """
        mock_parser.return_value.parse_args.return_value = MagicMock(api_key=CloudHealthTest.API_KEY)
        cloud_health = get_cloud_health()
        mock_cloud_health.assert_called_once_with(
            api_key = CloudHealthTest.API_KEY,
            logger=mock_logger(name=NAME),
            stats=mock_stats(prefix=NAME),
            )

    @patch('krux_cloud_health.cloud_health.get_stats')
    @patch('krux_cloud_health.cloud_health.get_logger')
    @patch('krux_cloud_health.cloud_health.CloudHealth')
    def test_get_cloud_health_all_args(self, mock_cloud_health, mock_logger, mock_stats):
        """
        Cloud Health Test: All arguments into passed CloudHealth if provided.
        """
        mock_args = MagicMock(api_key=CloudHealthTest.API_KEY)
        cloud_health = get_cloud_health(mock_args, mock_logger, mock_stats)
        mock_cloud_health.assert_called_once_with(
            api_key = CloudHealthTest.API_KEY,
            logger=mock_logger,
            stats=mock_stats,
            )

    def test_cost_history_time_input(self):
        """
        Cloud Health Test: Cost history method properly passes in arguments with time_input provided
        to Get API call method.
        """
        self.cloud_health._get_api_call = MagicMock()
        self.cloud_health._get_data = MagicMock()
        cost_history = self.cloud_health.cost_history(CloudHealthTest.TIME_INTERVAL, CloudHealthTest.TIME_INPUT)
        self.cloud_health._get_api_call.assert_called_once_with(
            CloudHealthTest.COST_HISTORY_REPORT,
            CloudHealthTest.API_KEY,
            CloudHealthTest.PARAMS_TIME_INPUT,
            )
        self.cloud_health._get_data.assert_called_once_with(
            self.cloud_health._get_api_call(
                CloudHealthTest.COST_HISTORY_REPORT,
                CloudHealthTest.API_KEY,
                CloudHealthTest.PARAMS_TIME_INPUT),
                CloudHealthTest.COST_HISTORY_CATEGORY_TYPE,
                CloudHealthTest.TIME_INPUT
                )

    def test_cost_history_no_time_input(self):
        """
        Cloud Health Test: Cost history method properly passes in arguments to Get API call method.
        without a specified time_input
        """
        self.cloud_health._get_api_call = MagicMock(return_value=CloudHealthTest.API_CALL)
        self.cloud_health._get_data = MagicMock()
        cost_history = self.cloud_health.cost_history(CloudHealthTest.TIME_INTERVAL)
        self.cloud_health._get_api_call.assert_called_once_with(
            CloudHealthTest.COST_HISTORY_REPORT,
            CloudHealthTest.API_KEY,
            CloudHealthTest.PARAMS_INTERVAL,
            )
        self.cloud_health._get_data.assert_called_once_with(
            CloudHealthTest.API_CALL,
            CloudHealthTest.COST_HISTORY_CATEGORY_TYPE,
            None)

    def test_cost_current(self):
        """
        Cloud Health Test: Cost current method properly passes in arguments to Get API call method.
        """
        self.cloud_health._get_api_call = MagicMock(return_value=CloudHealthTest.API_CALL)
        self.cloud_health._get_data = MagicMock()
        cost_current = self.cloud_health.cost_current()
        self.cloud_health._get_api_call.assert_called_once_with(
            CloudHealthTest.COST_CURRENT_REPORT,
            CloudHealthTest.API_KEY
            )
        self.cloud_health._get_data.assert_called_once_with(
            CloudHealthTest.API_CALL,
            CloudHealthTest.COST_CURRENT_CATEGORY_TYPE,
            None)

    @patch('krux_cloud_health.cloud_health.pprint.pformat')
    @patch('krux_cloud_health.cloud_health.requests')
    def test_get_api_call(self, mock_request, mock_pprint):
        """
        Cloud Health Test: Get API call method calls API with valid report and API key.
        """
        self.cloud_health.logger = MagicMock()
        mock_request.get.return_value.json.return_value = CloudHealthTest.API_CALL
        get_api_call = self.cloud_health._get_api_call(CloudHealthTest.COST_HISTORY_REPORT, CloudHealthTest.API_KEY)
        mock_request.get.assert_called_once_with(
            CloudHealthTest.COST_HISTORY_URI,
            params=CloudHealthTest.URI_ARGS_NO_PARAMS
            )
        mock_pprint.assert_called_once_with(CloudHealthTest.API_CALL)
        self.cloud_health.logger.debug.assert_called_once_with(mock_pprint(CloudHealthTest.API_CALL))
        self.assertEqual(get_api_call, CloudHealthTest.API_CALL)

    @patch('krux_cloud_health.cloud_health.requests')
    def test_get_api_call_error(self, mock_request):
        """
        Cloud Health Test: Get API call method throws ValueError if API returns an error.
        """
        mock_request.get.return_value.json.return_value = CloudHealthTest.API_CALL_ERROR
        self.cloud_health.logger = MagicMock()
        with self.assertRaises(ValueError) as ve:
            get_api_call = self.cloud_health._get_api_call(
                CloudHealthTest.COST_HISTORY_REPORT,
                CloudHealthTest.API_KEY)
        self.assertEqual(ve.exception.message, CloudHealthTest.API_CALL_ERROR.get('error'))

    def test_get_data(self):
        """
        Cloud Health Test: Get Data method correctly gets category and service information from API call. It then
        passes information for each category into Get Data Info.
        """
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
        """
        Cloud Health Test: Get Data Info method organizes information for inputted category and
        filters unnecessary services.
        """
        api_call = {'data': [
                [
                    [100]
                ]
            ]
        }
        get_data_info = self.cloud_health._get_data_info(
            api_call,
            [{'label': 'service', 'parent': 1}, {'label': 'Total', 'parent': 0}],
            'Total', 0)
        self.assertEqual(get_data_info, {'Total': {'service': 100}})

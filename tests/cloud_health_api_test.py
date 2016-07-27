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

from krux_cloud_health.cloud_health_api import Application, main
from krux_cloud_health.cloud_health import Interval, NAME
from krux.stats import DummyStatsClient


class CloudHealthAPITest(unittest.TestCase):

    NAME = 'cloud-health-tech'
    API_KEY = '12345'

    @patch('sys.argv', ['api-key', API_KEY])
    def setUp(self):
        self.app = Application()
        self.app.logger = MagicMock()
        self.app.cloud_health.cost_history = MagicMock()
        self.app.cloud_health.cost_history.return_value = {
            'Total': {'key': 'value'},
            '2016-05-01': {'key': 'value'},
            '2016-06-01': {'key': 'value'},
            '2016-07-01': {'key': 'value'},
        }

    def test_add_cli_arguments(self):
        """
        Cloud Health API Test: All arguments from present in the args
        """
        self.assertIn('api_key', self.app.args)
        self.assertIn('interval', self.app.args)
        self.assertIn('set_date', self.app.args)

        self.assertEqual(self.API_KEY, self.app.args.api_key)
        self.assertEqual(Interval.daily.name, self.app.args.interval)
        self.assertIsNone(self.app.args.set_date)

    # @patch('sys.argv', ['api-key', '12345', '--set-date', '2016-05-01'])
    # def test_run_with_set_date(self):

    def test_run_error(self):
        self.app.cloud_health.cost_history = MagicMock(side_effect=ValueError('Error message'))
        # self.app.cloud_health.cost_history.side_effect = ValueError('Error message')
        self.app.run()
        self.app.logger.error.assert_called_once_with('Error message')

    @patch('krux_cloud_health.cloud_health_api.pprint.pformat')
    def test_run_without_set_date(self, mock_pprint):
        """
        Cloud Health API Test: Cloud Health's cost_history and cost_current methods are correctly called in self.app.run()
        """
        self.app.run()
        self.app.cloud_health.cost_history.assert_called_once_with(Interval['daily'], None)
        mock_pprint.assert_called_once_with(self.app.cloud_health.cost_history(time_interval='daily', time_input=None))
        self.app.logger.info.assert_called_once_with('Determined %s is the most recent time with data' % '2016-07-01')

    @patch('sys.argv', ['api-key', '12345', '--set-date', '2016-05-01'])
    def test_run_with_set_date(self):
        app = Application()
        app.cloud_health.cost_history = MagicMock()
        app.cloud_health.cost_history.return_value = {
            'Total': {'key': 'value'},
            '2016-05-01': {'key': 'value'},
            '2016-06-01': {'key': 'value'},
            '2016-07-01': {'key': 'value'},
        }
        app.run()
        app.cloud_health.cost_history.assert_called_once_with(Interval['daily'], '2016-05-01')

    def test_main(self):
        """
        Cloud Health API Test: Application is instantiated and run() is called in main()
        """
        app = MagicMock()
        app_class = MagicMock(return_value=app)

        with patch('krux_cloud_health.cloud_health_api.Application', app_class):
            main()

        app_class.assert_called_once_with()
        app.run.assert_called_once_with()


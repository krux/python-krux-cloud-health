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

from krux_cloud_health.cli import Application, main
from krux_cloud_health.cloud_health import Interval
from krux.stats import DummyStatsClient


class CLItest(unittest.TestCase):

    NAME = 'cloud-health-tech'
    API_KEY = '12345'
    INTERVAL = Interval.weekly
    AWS_ACCOUNT = 'Krux IT'
    COST_HISTORY_RV =  {
            'Total': {'key': 'value'},
            '2016-05-01': {'key': 'value'},
            '2016-06-01': {'key': 'value'},
            '2016-07-01': {'key': 'value'}
        }
    COST_CURRENT_RV = {
            'Total': {'key': 'value'},
            'Krux IT': {'key': 'value'},
            'Krux Ops': {'key': 'value'}
        }

    @patch('krux_cloud_health.cli.get_cloud_health')
    @patch('sys.argv', ['api-key', API_KEY])
    def setUp(self, mock_get_cloud_health):
        self.app = Application()
        self.app.cloud_health = MagicMock()
        self.app.cloud_health.cost_history.return_value = CLItest.COST_HISTORY_RV
        self.app.cloud_health.cost_current.return_value = CLItest.COST_CURRENT_RV
        self.mock_get_cloud_health = mock_get_cloud_health

    def test_init(self):
        """
        CLI Test: CLI constructor creates all the required private properties
        """
        self.assertEqual(self.NAME, self.app.name)
        self.assertEqual(self.NAME, self.app.parser.description)
        # The dummy stats client has no awareness of the name. Just check the class.
        self.assertIsInstance(self.app.stats, DummyStatsClient)

        self.mock_get_cloud_health.assert_called_once_with(
            args=self.app.args,
            logger=self.app.logger,
            stats=self.app.stats
        )

    def test_add_cli_arguments(self):
        """
        CLI Test: All arguments from Cloud Health Tech are present in the args
        """
        self.assertIn('api_key', self.app.args)
        self.assertEqual(self.API_KEY, self.app.args.api_key)

    @patch('krux_cloud_health.cloud_health_api.pprint.pformat')
    def test_run(self, mock_pprint): #FIX
        """
        CLI Test: Cloud Health's cost_history and cost_current methods are correctly called in self.app.run()
        """
        self.app.logger = MagicMock()
        self.app.run()
        self.app.cloud_health.cost_history.assert_called_once_with(CLItest.INTERVAL)
        self.app.logger.info.assert_called_once_with(mock_pprint(CLItest.COST_HISTORY_RV))

    def test_main(self):
        """
        CLI Test: Application is instantiated and run() is called in main()
        """
        app = MagicMock()
        app_class = MagicMock(return_value=app)

        with patch('krux_cloud_health.cli.Application', app_class):
            main()

        app_class.assert_called_once_with()
        app.run.assert_called_once_with()


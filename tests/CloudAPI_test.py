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
    def test_cloud_health_call(self):
        test_case = CloudAPI()
        test_case.run()

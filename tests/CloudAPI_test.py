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

    def test_cloud_health_call(self):
        self.assertEqual(0, 1)

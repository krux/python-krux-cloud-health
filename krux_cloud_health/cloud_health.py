# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#
"""
Class to retrieve data from Cloud Health Tech API
"""

#
# Standard libraries
#

from __future__ import absolute_import
import sys
import urlparse
import pprint

#
# Third party libraries
#

import requests
from enum import Enum

#
# Internal libraries
#

from krux.cli import get_parser, get_group
from krux.logging import get_logger
from krux.stats import get_stats


NAME = "cloud-health-tech"


class Interval(Enum):
    hourly = 1
    daily = 2
    weekly = 3
    monthly = 4


def add_cloud_health_cli_arguments(parser):
    # Add those specific to the application
    group = get_group(parser, NAME)

    group.add_argument(
        'api_key',
        type=str,
        help="API key to retrieve data",
    )


def get_cloud_health(args=None, logger=None, stats=None):
    if not args:
        parser = get_parser(description=NAME)
        add_cloud_health_cli_arguments(parser)
        args = parser.parse_args()

    if not logger:
        logger = get_logger(name=NAME)

    if not stats:
        stats = get_stats(prefix=NAME)

    return CloudHealth(
        api_key=args.api_key,
        logger=logger,
        stats=stats,
        )


class CloudHealth(object):
    _API_ENDPOINT = "https://apps.cloudhealthtech.com/"
    _CATEGORY_DIMENSION_INDEX = 0
    _SERVICE_DIMENSION_INDEX = 1

    def __init__(self, api_key, logger, stats):
        self.api_key = api_key
        self.logger = logger
        self.stats = stats

    def cost_history(self, time_interval, time_input=None):
        """
        Cost history for specified time interval and input.

        :argument time_interval: time interval for which data is retrieved
        :argument time_input: date for which data is retrieved (optional) - if not specified, returns 'total'
        """
        report = "olap_reports/cost/history"
        params = {'interval': time_interval.name}

        if time_input is not None:
            params['filters[]'] = 'time:select:{0}'.format(time_input)

        api_call = self._get_api_call(report, self.api_key, params)

        return self._get_data(api_call, 'time', time_input)

    def cost_current(self, aws_account_input=None):
        """
        Current month's costs for AWS accounts.

        :argument time_input: AWS account for which data is retrieved (optional) - if not specified, will return information for all AWS accounts
        """
        report = "olap_reports/cost/current"
        api_call = self._get_api_call(report, self.api_key)

        return self._get_data(api_call, 'AWS-Account', aws_account_input)

    def _get_api_call(self, report, api_key, params={}):
        """
        Returns API call for specified report and time interval using API Key.

        :argument report: Filters data from API call for specific report
        :argument api_key: API allows data to be retrieved
        :argument time_interval: Filters data from API call for specific time interval
        """
        uri_args = {'api_key': api_key}
        uri_args.update(params)

        uri = urlparse.urljoin(self._API_ENDPOINT, report)

        r = requests.get(uri, params=uri_args)
        api_call = r.json()

        if api_call.get('error'):
            raise ValueError(api_call['error'])

        self.logger.debug(pprint.pformat(api_call))

        return api_call

    def _get_data(self, api_call, category_type, category_name=None):
        """
        Retrieves data from API call for

        :argument api_call: API call with information
        :argument category_type: Key of the first dimension (i.e. 'time' or 'AWS-Account')
        :argument category_name: Specifies category_name to retrieve from category_list (optional) - if not specified, retrieves info from all categories
        """
        # GOTCHA: Default with two empty dictionaries so lists can be retrieved
        dimensions = api_call.get('dimensions', [{}, {}])

        categories = [
            str(category.get('label'))
            for category in dimensions[self._CATEGORY_DIMENSION_INDEX].get(category_type, {})
            if category_name is None or category_name == category.get('label')
        ]

        services = dimensions[self._SERVICE_DIMENSION_INDEX].get('AWS-Service-Category', {})

        total_data = {}
        for index in range(len(categories)):
            category = categories[index]
            category_info = self._get_data_info(api_call, services, category, index)
            total_data.update(category_info)

        return total_data

    def _get_data_info(self, api_call, items_list, category_input, index):
        """
        Retrieves information for specific entry in category_list.
        """
        # TODO: Refactor this to be cleaner
        info = {category_input: {}}
        data_nested = api_call["data"][index]
        data_list = [data for sublist in data_nested for data in sublist]
        data_list = [float("%.2f" % data) if isinstance(data, float) else data for data in data_list]
        for i in range(len(items_list)):
            item = items_list[i]
            if item.get("parent") >= 0 and item["label"] != "Total":
                info[category_input][str(item["label"])] = data_list[i]
        return info

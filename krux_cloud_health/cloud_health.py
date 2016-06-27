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

#
# Third party libraries
#

import requests

#
# Internal libraries
#

from krux.cli import get_parser, get_group


API_ENDPOINT = "https://apps.cloudhealthtech.com/"
NAME = "cloud-health-tech"
INTERVAL = ['daily', 'monthly']


def add_cloud_health_cli_arguments(parser):
    # Add those specific to the application
    group = get_group(parser, NAME)
    
    group.add_argument(
        'api_key',
        type=str,
        help="API key to retrieve data",
    )


def get_cloud_health(args, logger, stats):
    if not args:
        parser = get_parser(description=NAME)
        add_dns_cli_arguments(parser)
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
    def __init__(self, api_key, logger, stats):
        self.api_key = api_key
        self.logger = logger
        self.stats = stats

    def cost_history_month(self, month_input=None):
        """
        Cost history for specified month.

        :argument month_input: month for which data is retrieved (optional)
        """
        return self._cost_history("monthly", month_input)

    def cost_history_day(self, day_input=None):
        """
        Cost history for specified day.

        :argument month_input: month for which data is retrieved (optional)
        """
        return self._cost_history("daily", day_input)

    def _cost_history(self, time_interval, time_input):
        """
        Cost history for specified time interval and input.
    
        :argument time_interval: time interval for which data is retrieved
        :argument time_input: date for which data is retrieved (optional) - if not specified, returns 'total'
        """
        report = "olap_reports/cost/history"
        api_call = self._get_api_call(report, self.api_key, time_interval)

        dimensions = api_call.get('dimensions', [])
        time_dict = dimensions[0].get('time', {})
        time_list = [str(time["name"]) for time in time_dict]

        items_list = dimensions[1].get('AWS-Service-Category', {})

        return self._get_data(api_call, items_list, time_list, time_input, time_interval)

    def cost_current(self, aws_account_input=None):
        """
        Current month's costs for AWS accounts.

        :argument time_input: AWS account for which data is retrieved (optional) - if not specified, will return information for all AWS accounts
        """
        report = "olap_reports/cost/current"
        api_call = self._get_api_call(report, self.api_key, None)

        
        dimensions = api_call.get('dimensions', [])
        aws_accounts_dict = dimensions[0].get('AWS-Account', {})
        aws_accounts_list = [str(aws_account["label"]) for aws_account in aws_accounts_dict]

        items_list = dimensions[1].get('AWS-Service-Category', {})

        return self._get_data(api_call, items_list, aws_accounts_list, aws_account_input, "AWS account")

    def _get_api_call(self, report, api_key, time_interval=None):
        """
        Returns API call for specified report and time interval using API Key.

        :argument report: Filters data from API call for specific report
        :argument api_key: API allows data to be retrieved
        :argument time_interval: Filters data from API call for specific time interval
        """
        uri_args = {'api_key': api_key, 'interval': time_interval}
        uri = urlparse.urljoin(API_ENDPOINT, report)
        r = requests.get(uri, params=uri_args)
        api_call = r.json()
        if api_call.get('error'):
            raise ValueError(api_call['error'])
        return api_call

    def _get_data(self, api_call, items_list, category_list, category_input, category_type):
        """
        Retrieves data from API call for 

        :argument api_call: API call with information
        :argument items_list: Items retrieved from API call
        :argument category_list: Categories retrieved from API call
        :argument category_input: Specifies category_input to retrieve from category_list (optional) - if not specified, retrieves info from all categories
        :argument category_type: Type of data in category_list
        """

        if category_input is None:
            return self._get_total_data(api_call, items_list, category_list)

        if category_input not in category_list:
            raise ValueError("Invalid {} input".format(category_type))

        category_index = category_list.index(category_input)
        return self._get_data_info(api_call, items_list, category_input, category_index)

    def _get_total_data(self, api_call, items_list, category_list):
        """
        Retrieves information for all entries in category_list.
        """
        total_data = []
        for index in range(len(category_list)):
            category = category_list[index]
            category_info = self._get_data_info(api_call, items_list, category, index)
            total_data.append(category_info)
        return total_data

    def _get_data_info(self, api_call, items_list, category_input, index):
        """
        Retrieves information for specific entry in category_list.
        """
        info = {category_input: {}}
        data_nested = api_call["data"][index]
        data_list = [data for sublist in data_nested for data in sublist]
        data_list = [float("%.2f" % data) if isinstance(data, float) else data for data in data_list]
        for i in range(len(items_list)):
            item = items_list[i]
            if item.get("parent") >= 0 and item["label"] != "Total":
                info[category_input][str(item["label"])] = data_list[i]
        return info

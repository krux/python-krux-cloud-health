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
    """
    """
    def __init__(self, api_key, logger, stats):
        self.api_key = api_key
        self.logger = logger
        self.stats = stats

    def costHistory(self, month_input=None):
        report = "olap_reports/cost/history"
        api_call = self._get_api_call(report, self.api_key)

        months_dict = api_call["dimensions"][0]["time"]
        months_list = [str(month["name"]) for month in months_dict]

        items_list = api_call["dimensions"][1]["AWS-Service-Category"]

        if month_input is None:
            total_data = self._get_total_data(api_call, items_list, months_list)
            return total_data

        if month_input not in months_list:
            raise ValueError("Invalid month input.")

        month_index = months_list.index(month_input)
        month_info = self._get_data_info(api_call, items_list, month_input, month_index)
        return month_info

    def costCurrent(self, aws_account_input=None):
        report = "olap_reports/cost/current"
        api_call = self._get_api_call(report, self.api_key)

        aws_accounts_dict = api_call["dimensions"][0]["AWS-Account"]
        aws_accounts_list = [str(aws_account["label"]) for aws_account in aws_accounts_dict]

        items_list = api_call["dimensions"][1]["AWS-Service-Category"]

        if aws_account_input is None:
            total_data = self._get_total_data(api_call, items_list, aws_accounts_list)
            return total_data

        if aws_account_input not in aws_accounts_list:
            raise ValueError("Invalid AWS account input.")

        aws_account_index = aws_accounts_list.index(aws_account_input)
        aws_account_info = self._get_data_info(api_call, items_list, aws_account_input, aws_account_index)
        return aws_account_info

    def _get_api_call(self, report, api_key):
        uri_args = {'api_key': api_key}
        uri = urlparse.urljoin(API_ENDPOINT, report)
        r = requests.get(uri, params=uri_args)
        api_call = r.json()
        if api_call.get('error'):
            raise ValueError(api_call['error'])
        return api_call

    def _get_total_data(self, api_call, items_list, category_list):
        total_data = []
        for index in range(len(category_list)):
            category = category_list[index]
            category_info = self._get_data_info(api_call, items_list, category, index)
            total_data.append(category_info)
        return total_data

    def _get_data_info(self, api_call, items_list, category_input, index):
        info = {category_input: {}}
        data_nested = api_call["data"][index]
        data_list = [data for sublist in data_nested for data in sublist]
        data_list = [float("%.2f" % data) if isinstance(data, float) else data for data in data_list]
        for i in range(len(items_list)):
            item = items_list[i]
            if item.get("parent") >= 0 and item["label"] != "Total":
                info[category_input][str(item["label"])] = data_list[i]
        return info

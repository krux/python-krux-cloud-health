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

#
# Internal libraries
#

from krux.cli import Application
from krux.cli import get_parser, get_group

API_ENDPOINT = "https://apps.cloudhealthtech.com/"


class CloudHealth(object):
    """
    """
    def __init__(self, api_key, logger, stats):
        self.api_key = api_key
        self.logger = logger
        self.stats = stats

    def costHistory(self):
        report = "olap_reports/cost/history"
        api_call = self.get_api_call(report, self.api_key)

        months = api_call["dimensions"][0]["time"]
        month_list = [str(month["name"]) for month in months]

        items_list = api_call["dimensions"][1]["AWS-Service-Category"]

        total_data = []

        for month_index in range(len(month_list)):
            month = month_list[month_index]
            month_info = {month: {}}

            data_nested = api_call["data"][month_index]
            data_list = [data for sublist in data_nested for data in sublist]
            data_list = [float("%.2f" % data) if isinstance(data, float) else data for data in data_list]

            for i in range(len(items_list)):
                item = items_list[i]
                if item.get("parent") >= 0 and item["label"] != "Total":
                    month_info[month][str(item["label"])] = data_list[i]
            total_data.append(month_info)

        return total_data

    def costCurrent(self):
        report = "olap_reports/cost/current"
        api_call = self.get_api_call(report, self.api_key)

        aws_accounts = api_call["dimensions"][0]["AWS-Account"]
        aws_accounts_list = [str(aws_account["label"]) for aws_account in aws_accounts]

        items_dict = api_call["dimensions"][1]["AWS-Service-Category"]
        items_list = [str(item["label"]) for item in items_dict]

        total_data = []

        for index in range(len(aws_accounts_list)):
            data_nested = api_call["data"][index]
            data_list = [data for sublist in data_nested for data in sublist]
            data_list = [float("%.2f" % data) if isinstance(data, float) else data for data in data_list]
            account_info = {aws_accounts_list[index]: dict(zip(items_list, data_list))}
            total_data.append(account_info)

        return total_data

    def get_api_call(self, report, api_key):
        uri_args = {'api_key': api_key}
        uri = urlparse.urljoin(API_ENDPOINT, report)
        r = requests.get(uri, params=uri_args)
        return r.json()

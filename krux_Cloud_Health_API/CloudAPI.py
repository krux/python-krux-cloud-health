# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import pprint
import urlparse
import json

#
# Third party libraries
#

import requests

#
# Internal libraries
#

from krux.logging import get_logger
from krux.stats import get_stats
from krux.cli import Application, get_group

NAME = 'release-monitoring'
API_ENDPOINT = "https://apps.cloudhealthtech.com/olap_reports/"


class Application(Application):

    def __init__(self, name=NAME):
        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.api_key = self.args.api_key
        self.logger = get_logger(name)

    def add_cli_arguments(self, parser):
        # Call to the superclass first
        super(Application, self).add_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            '--name',
            help="Name of user"
        )

        group.add_argument(
            '--api-key',
            help="API key to retrieve data",
        )

        group.add_argument(
            '--api-endpoint',
            help="URL to retrieve necessary data",
        )

    def get_report(self, report, time_filter, api_key):
        uri = urlparse.urljoin(API_ENDPOINT, report)
        # uri += "?" + time_filter
        uri += "?api_key=%s" % api_key
        r = requests.get(uri)
        return r.json()

    def run(self):
        select_month = "interval=monthly&filters[]=time:select:-1"
        call = self.get_report("cost/history", select_month, self.api_key)

        curr_month = "2016-06"
        months = call["dimensions"][0]["time"]
        month_index = [index for index, month in enumerate(months) if month["name"] == curr_month][0]

        items_dict = call["dimensions"][1]["AWS-Service-Category"]
        items_list = [str(item["label"]) for item in items_dict]

        data_nested = call["data"][month_index]
        data_list = [data for sublist in data_nested for data in sublist]

        data_list = [float("%.2f" % data) if isinstance(data, float) else data for data in data_list]

        curr_month_info = {curr_month: dict(zip(items_list, data_list))}

        print pprint.pformat(curr_month_info, indent=2, width=20)

def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

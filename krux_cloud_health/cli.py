# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#
"""
CLI tools for accessing Krux Cloud Health Tech
"""

#
# Standard libraries
#

from __future__ import absolute_import
import sys
import pprint

#
# Third party libraries
#

import krux.cli
from krux.cli import get_group
from krux_cloud_health.cloud_health import CloudHealth

NAME = "cloud-health-tech"


class Application(krux.cli.Application):
    def __init__(self, name=NAME):

        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.cloud_health = CloudHealth(api_key=self.args.api_key, stats=self.stats)
        self.month = self.args.month

    def add_cli_arguments(self, parser):
        # Call to the superclass first
        super(Application, self).add_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            '--api-key',
            help="API key to retrieve data",
        )

        group.add_argument(
            '--month',
            type=str,
            default='total',
            help="Retrieve cost history data for specific month from the past year. Must be in 'YYYY-MM' format.",
        )

    def run(self):
        costHistory = self.cloud_health.costHistory()

        month_index = month_index = [item.keys()[0] for item in costHistory].index(self.args.month)

        for item, data in costHistory[month_index][self.args.month].iteritems():
            self.stats.incr(item, data)

def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

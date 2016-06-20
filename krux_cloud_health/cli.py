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
from krux.logging import get_logger
from krux.cli import get_group
from krux_cloud_health.cloud_health import CloudHealth, NAME, add_cloud_health_cli_arguments, get_cloud_health


class Application(krux.cli.Application):
    def __init__(self, name=NAME):

        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.logger = get_logger(name)

        try:
            self.cloud_health = get_cloud_health(args=self.args, logger=self.logger, stats=self.stats)
        except ValueError as e:
            self.logger.warning(e.message)
            self.exit(1)

        self.month = self.args.month

    def add_cli_arguments(self, parser):
        # Call to the superclass first
        add_cloud_health_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            '--month',
            type=str,
            default='total',
            help="Retrieve cost history data for specific month from the past year. Must be in 'YYYY-MM' format.",
        )

    def run(self):
        try:
            costHistory = self.cloud_health.costHistory()
        except ValueError as e:
            self.logger.error(e.message)
            self.exit(1)

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

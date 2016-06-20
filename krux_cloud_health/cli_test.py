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
from krux.logging import get_logger
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

    def run(self):
        costHistory = self.cloud_health.costHistory()
        self.logger.debug(pprint.pformat(costHistory, indent=2, width=20))


def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

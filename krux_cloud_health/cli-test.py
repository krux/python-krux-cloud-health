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

    def add_cli_arguments(self, parser):
        # Call to the superclass first
        super(Application, self).add_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            '--api-key',
            help="API key to retrieve data",
        )

    def run(self):
        costHistory = self.cloud_health.costHistory()
        print pprint.pformat(costHistory, indent=2, width=20)
        # costCurrent = self.cloud_health.costCurrent()
        #print pprint.pformat(costCurrent, indent=2, width=20)


def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

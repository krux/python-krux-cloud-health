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
import pprint

#
# Third party libraries
#


#
# Internal libraries
#

import krux.cli
from krux.logging import get_logger
from krux.cli import get_group
from krux_cloud_health.cloud_health import CloudHealth, Interval, NAME, add_cloud_health_cli_arguments, get_cloud_health


class Application(krux.cli.Application):
    def __init__(self, name=NAME):

        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.logger = get_logger(name)

        try:
            self.cloud_health = get_cloud_health(args=self.args, logger=self.logger, stats=self.stats)
        except ValueError as e:
            self.logger.error(e.message)
            self.exit(1)

        self.interval = Interval[self.args.interval]

    def add_cli_arguments(self, parser):
        """
        Add CloudHealth-related command-line arguments to the given parser.

        :argument parser: parser instance to which the arguments will be added
        """

        add_cloud_health_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            '--interval',
            type=str,
            choices=[i.name for i in Interval],
            default=Interval.daily.name,
            help="Set time interval of data (default: %(default)s)",
        )

        group.add_argument(
            '--set-date',
            type=str,
            default=None,
            help="Retrieve cost history data for specific date, depending on interval. (ex: 'YYYY-MM-DD' for daily)",
        )

    def run(self):
        try:
            cost_history = self.cloud_health.cost_history(self.interval, self.args.set_date)
            self.logger.debug(pprint.pformat(cost_history))
        except (ValueError, IndexError) as e:
            self.logger.error(e.message)
            self.exit(1)

        # If no set_date, cost_data is most recent data available for given time interval in cost_history
        if self.args.set_date is None:
            cost_history.pop('Total')
            last_key = sorted(cost_history.keys())[-1]
            self.logger.info('Determined %s is the most recent time with data' % last_key)

            cost_data = cost_history[last_key]
        else:
            cost_data = cost_history.values()[0]

        for item, data in cost_data.iteritems():
            self.stats.incr(item, data)


def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

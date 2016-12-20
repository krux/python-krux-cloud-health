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
from datetime import datetime
import calendar

#
# Third party libraries
#

from six import iteritems

#
# Internal libraries
#

from krux.cli import get_group
import krux_cloud_health.cli


class Application(krux_cloud_health.cli.Application):
    NAME = 'cloud-health-to-graphite'

    def __init__(self, name=NAME):

        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

    def add_cli_arguments(self, parser):
        """
        Add CloudHealth-related command-line arguments to the given parser.

        :argument parser: parser instance to which the arguments will be added
        """
        # Call to the superclass first
        super(Application, self).add_cli_arguments(parser)

        group = get_group(parser, self.name)

        group.add_argument(
            'report_id',
            type=long,
            help='ID of the report to export to graphite',
        )

        group.add_argument(
            '-n', '--report-name',
            type=str,
            default='',
            help="Name of the report for stats (default: %(default)s)",
        )

        group.add_argument(
            '--set-date',
            type=str,
            default=None,
            help="Retrieve cost history data for specific date, depending on interval. (ex: 'YYYY-MM-DD' for daily)",
        )

    def run(self):
        try:
            report_data = self.cloud_health.get_custom_report(report_id=self.args.report_id, category=self.args.set_date)
            self.logger.debug(pprint.pformat(report_data))
        except (ValueError, IndexError) as e:
            self.logger.error(e.message)
            self.exit(1)

        del report_data['Total']
        for date, values in iteritems(report_data):
            date = int(calendar.timegm(datetime.strptime(date, '%Y-%m-%d').utctimetuple()))

            for category, cost in iteritems(values):
                if cost is not None:
                    print('cloud_health.{env}.{report_name}.{category} {cost} {date}'.format(
                        env=self.args.stats_environment,
                        report_name=self.args.report_name,
                        category=category,
                        cost=cost,
                        date=date,
                    ))


def main():
    app = Application()
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

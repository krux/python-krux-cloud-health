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
import re

#
# Third party libraries
#

from six import iteritems

#
# Internal libraries
#

from krux.cli import get_group
from krux_cloud_health import VERSION
import krux_cloud_health.cli


class Application(krux_cloud_health.cli.Application):
    NAME = 'cloud-health-to-graphite'

    _INVALID_STATS_PATTERN = re.compile('[ \.]+')

    def __init__(self, name=NAME):
        self._VERSIONS[self.NAME] = VERSION

        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        # XXX: Empty space and period causes issues with graphite. Replace it with underscore.
        self.report_name = Application._sanitize_stats(self.args.report_name)

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

        group.add_argument(
            '--date-format',
            type=str,
            default='%Y-%m-%d',
            help="Format string to use to parse the date passed by Cloud Health (default: %(default)s)",
        )

    @staticmethod
    def _sanitize_stats(stat_name):
        return re.sub(Application._INVALID_STATS_PATTERN, '_', stat_name)

    def run(self):
        try:
            report_data = self.cloud_health.get_custom_report(report_id=self.args.report_id, category=self.args.set_date)
            self.logger.debug(pprint.pformat(report_data))
        except (ValueError, IndexError) as e:
            self.logger.error(e.message)
            self.exit(1)
            return

        if 'Total' in report_data:
            del report_data['Total']

        for date, values in iteritems(report_data):
            date = int(calendar.timegm(datetime.strptime(date, self.args.date_format).utctimetuple()))

            for category, cost in iteritems(values):
                # XXX: Empty space and period causes issues with graphite. Replace it with underscore.
                category = Application._sanitize_stats(category)
                if cost is not None:
                    print('cloud_health.{env}.{report_name}.{category} {cost} {date}'.format(
                        env=self.args.stats_environment,
                        report_name=self.report_name,
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

# -*- coding: utf-8 -*-
#
# © 2016-2018 Salesforce.com, inc.
#
"""
Package setup for python-krux-release-monitoring
"""
######################
# Standard Libraries #
######################
from __future__ import absolute_import
from setuptools import setup, find_packages
from krux_cloud_health import __version__


# URL to the repository on Github.
REPO_URL = 'https://github.com/krux/python-krux-cloud-health'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
# We use the version to construct the DOWNLOAD_URL.
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', __version__))


setup(
    name='krux-cloud-health',
    version=__version__,
    author='Kareena Hirani',
    author_email='khirani@krux.com',
    maintainer='Peter Han',
    maintainer_email='phan@salesforce.com',
    description='Retrieves and organizes info from Cloud Health API',
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='All Rights Reserved.',
    packages=find_packages(exclude=['tests']),
    # dependencies are named in Pipfile
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cloud-health-to-graphite=bin.cloud_health_to_graphite:main',
            'krux-cloud-health-test=krux_cloud_health.cli:main',
        ],
    },
)

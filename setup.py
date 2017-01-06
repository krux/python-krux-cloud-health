# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#
"""
Package setup for python-krux-release-monitoring
"""
######################
# Standard Libraries #
######################
from __future__ import absolute_import
from setuptools import setup, find_packages

# We use the version to construct the DOWNLOAD_URL.
VERSION = '0.2.0'

# URL to the repository on Github.
REPO_URL = 'https://github.com/krux/python-krux-cloud-health'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))


setup(
    name='python-krux-cloud-health',
    version=VERSION,
    author='Kareena Hirani',
    author_email='khirani@krux.com',
    description='Retrieves and organizes info from Krux Cloud Health API',
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='All Rights Reserved.',
    packages=find_packages(),
    # dependencies are named in requirements.pip
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cloud-health-to-graphite=bin.cloud_health_to_graphite:main',
            'krux-cloud-health-test=krux_cloud_health.cli:main',
        ],
    },
)

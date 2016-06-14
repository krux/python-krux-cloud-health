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
VERSION  = '0.0.1'

# URL to the repository on Github.
REPO_URL = 'https://github.com/krux/python-krux-Cloud-Health-API'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))


setup(
    name='python-krux-Cloud-API',
    version=VERSION,
    author='Kareena Hirani',
    author_email='khirani@krux.com',
    description='',
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='All Rights Reserved.',
    packages=find_packages(),
    # dependencies are named in requirements.pip
    install_requires=[],
    entry_points={
        'console_scripts': [
            'Cloud-API-script=krux_Cloud_Health_API.CloudAPI:main',
        ],
    },
)

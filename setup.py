# -*- coding: utf-8 -*-
from setuptools import setup
import re


def get_version():
    with open('hepdata_converter_ws_client/version.py', 'r') as version_f:
        content = version_f.read()

    r = re.search('^__version__ *= *\'(?P<version>.+)\'', content, flags=re.MULTILINE)
    if not r:
        return '0.0.0'
    return r.group('version')

setup(
    name='hepdata-converter-ws-client',
    version=get_version(),
    install_requires=[
        'requests',
    ],
    tests_require=['flask-testing', 'flask', 'hepdata-converter-ws'],

    packages=['hepdata_converter_ws_client'],
    url='https://github.com/HEPData/hepdata-converter-ws-client/',
    license='GPL',
    author='Michał Szostak',
    author_email='michal.florian.szostak@cern.ch',
    description='Simple wrapper for requests, to ease use of HEPData Converter WebServices API',
    download_url='https://github.com/HEPData/hepdata-converter-ws-client/tarball/%s' % get_version(),
)
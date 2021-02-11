# -*- coding: utf-8 -*-
from setuptools import setup
import re


test_requirements = ['pyyaml>=5.3']

extras_require = {'tests': test_requirements}


def get_version():
    with open('hepdata_converter_ws_client/version.py', 'r') as version_f:
        content = version_f.read()

    r = re.search('^__version__ *= *\'(?P<version>.+)\'', content, flags=re.MULTILINE)
    if not r:
        return '0.0.0'
    return r.group('version')


# Get the long description from the README file
with open('README.md', 'rt') as fp:
    long_description = fp.read()


setup(
    name='hepdata-converter-ws-client',
    version=get_version(),
    python_requires = '~=3.6',
    install_requires=[
        'future>=0.18.2',
        'requests>=2.23.0',
    ],
    tests_require=test_requirements,
    extras_require=extras_require,
    packages=['hepdata_converter_ws_client'],
    url='https://github.com/HEPData/hepdata-converter-ws-client',
    license='GPL',
    author='HEPData Team',
    author_email='info@hepdata.net',
    description='Simple wrapper for requests, to ease use of HEPData Converter WebServices API',
    download_url='https://github.com/HEPData/hepdata-converter-ws-client/tarball/%s' % get_version(),
    long_description=long_description,
    long_description_content_type='text/markdown',
)

# -*- encoding: utf-8 -*-
import base64
import json
import os
import requests
import tarfile
import tempfile
import shutil
from io import BytesIO
from builtins import str as text
from future.utils import raise_from

__author__ = 'Michał Szostak'

ARCHIVE_NAME = 'hepdata-converter-ws-data'


class Error(Exception):
    """Generic exception for hepdata_converter_ws_client"""
    pass


def convert(url, input, output=None, options={}, id=None, extract=True, timeout=600):
    """Wrapper function around requests library providing easy way to interact
    with hepdata-converter-ws (web services).

    :param url: path to server hosting hepdata-converter-ws (web services) - url has to point to root server
    (not ``/convert`` or any other specific route) just http(s)://address:port
    :type url: str

    :param input: Input, can be either path (str / unicode) to the file / directory that should be converted, or
    a file object containing data with the content of the file that should be converted
    :type input: str / unicode / file object

    :param output: Output, can be either path (str / unicode) to the file / directory to which output should be written
    (in this case it will be automatically extracted, extract argument must be True), file object (in this case extract
    flag must be False, the response tar.gz content will be written to output file object) or None (not specified).
    If output is not specified the extract flag is not taken into consideration and the function returns the content of
    the requested tar.gz file.
    :type output: str / unicode / file object

    :param options: Options passed to the converter - the same as the ones accepted by the hepdata_converter.convert
    function (https://github.com/HEPData/hepdata-converter). Most basic keys / values are:
    'input_format': 'yaml' (if input_format has not been specified the default is YAML)
    'output_format': 'root' (if output_format has not been specified the default is YAML)
    :type options: dict

    :param id: used for caching purposes (can be any object that can be turned into a string) - if two convert calls
    have the same ID and output types the same output will be returned. Because of this if IDs are equal it implies
    equality of input files. (Note added: this caching feature has not yet been implemented.)
    :type id: str / int

    :param extract: If set to True the requested tar.gz will be extracted to the directory specified in output. If set
    to False the requested tar.gz file will be written to output. If no output has been specified this attribute is not
    taken into account. IMPORTANT: if output is a file object (not a path) extract must be set to False
    :type extract: bool

    :param timeout: the time after which the request to the webservice will be cancelled. Defaults to 600s.
    :type timeout: int

    :raise ValueError: if input values are not sane ValueError is raised

    :raise Error: if the request to the server fails or times out

    :rtype : str Binary data
    :return: Binary data containing tar.gz return type. value is returned from this function if and only if no output
    has been specified
    """
    output_defined = output is not None
    if not output_defined:
        extract = False
        output = BytesIO()

    data = _create_data(input, options)

    if id:
        data['id'] = id

    try:
        r = requests.get(url + '/convert',
                         data=json.dumps(data),
                         headers={'Content-type': 'application/json',
                                  'Accept': 'application/x-gzip'},
                         timeout=timeout)

        # Raise errors, with exception of 500 errors. We ignore 500 status
        # codes and continue, to return the full error details
        if r.status_code < 500:
            r.raise_for_status()
    except requests.RequestException as e:
        # We get here from a timeout as well as a non-500 error code
        raise_from(Error('Request to %s failed' % url), e)

    error_occurred = False
    try:
        tarfile.open(mode='r:gz', fileobj=BytesIO(r.content)).close()
    except tarfile.ReadError:
        error_occurred = True

    if extract and not error_occurred:
        if not isinstance(output, (str, text)):
            raise ValueError('if extract=True then output must be path')

        tmp_dir = tempfile.mkdtemp(suffix='hdc')
        try:
            with tarfile.open(mode='r:gz', fileobj=BytesIO(r.content)) as tar:
                tar.extractall(tmp_dir)
            content = os.listdir(tmp_dir)[0]
            shutil.move(os.path.join(tmp_dir, content), output)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        if isinstance(output, (str, text)):
            with open(output, 'wb') as f:
                f.write(r.content)
        elif hasattr(output, 'write'):
            output.write(r.content)
        else:
            raise ValueError('output is not path or file object')

    if not output_defined:
        return output.getvalue()
    elif error_occurred:
        return False
    else:
        return True


def get_data_size(input, options={}):
    """Gets the size in bytes of the json data that would be sent to the converter.

    :param input: Input, can be either path (str / unicode) to the file / directory that should be converted, or
    a file object containing data with the content of the file that should be converted
    :type input: str / unicode / file object

    :param options: Options passed to the converter - the same as the ones accepted by the hepdata_converter.convert
    function (https://github.com/HEPData/hepdata-converter). Most basic keys / values are:
    'input_format': 'yaml' (if input_format has not been specified the default is YAML)
    'output_format': 'root' (if output_format has not been specified the default is YAML)
    :type options: dict

    :return: Size in bytes of the json data
    :rtype: int
    """
    data = _create_data(input, options)
    return len(json.dumps(data).encode('utf-8'))


def _create_data(input, options):
    input_stream = BytesIO()

    archive_name = options.get('filename', ARCHIVE_NAME)

    # input is a path, treat is as such
    if isinstance(input, (str, text)):
        assert os.path.exists(input)

        with tarfile.open(mode='w:gz', fileobj=input_stream) as tar:
            if os.path.isdir(input):
                with os.scandir(input) as it:
                    for entry in it:
                        if entry.is_file():
                            if os.path.splitext(entry.name)[1] in ['.yaml', '.json']:
                                tar.add(entry.path, arcname=os.path.join(archive_name, entry.name))
            else:
                tar.add(input, arcname=archive_name)

    elif hasattr(input, 'read'):
        with tarfile.open(mode='w:gz', fileobj=input_stream) as tar:
            info = tarfile.TarInfo(archive_name)
            input.seek(0, os.SEEK_END)
            info.size = input.tell()
            input.seek(0)
            tar.addfile(info, fileobj=input)
    else:
        raise ValueError('input is not path or file object!')

    inputdata = input_stream.getvalue()

    return {
        'input': base64.b64encode(inputdata).decode('utf-8'),
        'options': options
    }

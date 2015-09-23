[![Build Status](https://travis-ci.org/HEPData/hepdata-converter-ws-client.svg?branch=master)](https://travis-ci.org/HEPData/hepdata-converter-ws-client)

[![Coverage Status](https://coveralls.io/repos/HEPData/hepdata-converter-ws-client/badge.svg?branch=master&service=github)](https://coveralls.io/github/HEPData/hepdata-converter-ws-client?branch=master)

[![PyPi](https://img.shields.io/pypi/dm/hepdata-converter-ws-client.svg)](https://pypi.python.org/pypi/hepdata-converter-ws-client/)

[![PyPi](https://img.shields.io/github/license/hepdata/hepdata-converter-ws-client.svg)](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/LICENSE.txt)


# hepdata-converter-ws-client

Light client wrapper for interaction with hepdata-converter-ws (Web Services).
It is recommended to use it instead of manually creating requests to hepdata-converter-ws.

The reason for creating this package is the fact that hepdata-converter-ws API requires compressing files into
tar.gz and then encoding it useing base64 in order to pass them as an argument in JSON request, and doing this manually
every time someone wants to call hepdata-converter-ws API was a little cumbersome, that's why this light wrapper was
born.

Additionally library provides additional variety when it comes to writing output of the convert function - instead
of receiving raw tar.gz content it is possible to extract it to specified file path.

## Sample usage

The library exposes one single function ```hepdata_converter_ws_client.convert``` which is very similar to
```hepdata_converter.convert```. It accepts one additional argument (```url```), and restricts input / output to
```str```, ```unicode``` and file objects (objects supporting ```read```, ```write```, ```seek```, ```tell```).
```options``` parameter should be the same as with ```hepdata_converter``` library (https://github.com/HEPData/hepdata-converter)
The library can be used in the following way:

### Function description

```hepdata_converter_ws_client.convert``` function has proper docstring describing its arguments and return values, here is an excerpt:

```
def convert(url, input, output=None, options={}, id=None, extract=True):
    """Wrapper function around requests library providing easy way to interact
    with hepdata-converter-ws (web services).

    :param url: path to server hosting hepdata-converter-ws (web services) - url has to point to root server
    (not /convert or any other specific route) just http(s)://address:port
    :type url: str

    :param input: Input, can be either path (str / unicode) to the file / directory that should be converted, or
    fileobject containing data with the content of the file that should be converted

    :type input: str / unicode / fileobject
    :param output: Output, can be either path (str / unicode) to the file / directory to which output should be written
    (in this case it will be automatically extracted, extract argument must be True), fileobject (in this case extract
    flag must be False, the response tar.gz content will be written to output fileobject) or None (not specified).
    If output is not specified extract flag is not taken into consideration and function returns content of the requested
    tar.gz file.

    :type output: str / unicode / fileobject

    :param options: Options passed to the converter - the same as the ones accepted by hepdata_converter.convert
    function (https://github.com/HEPData/hepdata-converter). Most basic key / values are:
    'input_format': 'yaml'
    'output_format': 'root'

    if not output_format has been specified the default is YAML
    if not input_format has been specified the default is YAML

    :type options: dict

    :param id: used for caching purposes (can be any object that can be turned into string) - if two convert calls
    have the same ID and output types same output will be returned. Because of this if IDs are equal it implies input
    files equality
    :type id: str / int

    :param extract: If set to True the requested tar.gz will be extracted to directory specified in output. If set to
    False requested tar.gz file fill be written to output. If no output has been specified this attribute is not taken
    into account.
    IMPORTANT if output is a file object (not a path) extract must be set to False
    :type extract: bool

    :raise ValueError: if input vales are not sane ValueError is raised

    :rtype : str Binary data
    :return: Binary data containing tar.gz return type. value is returned from this function if and only if no output
    has been specified
    """
```


### Convert using file paths

Arguments passed as input and output can be file paths or file objects, below is an example
of how to utilize convert function with file paths

```
import hepdata_converter_ws_client

# using path to input file, and writing output directly to ouput_path
input_path = '/path/to/input.txt'
output_path = '/path/to/output/dir'
hepdata_converter_ws_client.convert('http://hepdata-converter-ws-addr:port', input_path, output_path,
                                    options={'input_format': 'oldhepdata'})
```

### Convert using input path and output file object

Input can always be file object (as long as the input Parser supports single files). Output can be file object
only if kwarg ```extract``` is set to False (in this case binary content of returned tar.gz will be written to output
file object, it's then responsibility of the user to decompress it)

```
import hepdata_converter_ws_client
# using path to input file, writing to output stream
input_path = '/path/to/input.txt'
output = StringIO.StringIO()
hepdata_converter_ws_client.convert('http://hepdata-converter-ws-addr:port', input_path, output,
                                    options={'input_format': 'oldhepdata'}, extract=False)

```

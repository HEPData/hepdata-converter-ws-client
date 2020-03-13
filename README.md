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
```hepdata_converter.convert```. It accepts the additional argument (```url```), and restricts input / output to
```str```, ```unicode``` and file objects (objects supporting ```read```, ```write```, ```seek```, ```tell```).

The ```options``` parameter should be the same as with [```hepdata_converter``` library ](https://github.com/HEPData/hepdata-converter).

The ```timeout``` parameter can be used to set a timeout for requests (defaults to 600s)

The library defines the exception ```hepdata_converter_ws_client.Error``` which will be thrown on timeouts or other errors connecting to the server.

### Function description

[```hepdata_converter_ws_client.convert```](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/hepdata_converter_ws_client/__init__.py#L23) function has proper [docstring](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/hepdata_converter_ws_client/__init__.py#L24-L73) describing its arguments and return values.

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
from io import BytesIO
# using path to input file, writing to output stream
input_path = '/path/to/input.txt'
output = BytesIO()
hepdata_converter_ws_client.convert('http://hepdata-converter-ws-addr:port', input_path, output,
                                    options={'input_format': 'oldhepdata'}, extract=False)

```

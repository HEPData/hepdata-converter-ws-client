[![GitHub Actions Status](https://github.com/HEPData/hepdata-converter-ws-client/workflows/Continuous%20Integration/badge.svg?branch=master)](https://github.com/HEPData/hepdata-converter-ws-client/actions?query=branch%3Amaster)
[![Coveralls Status](https://coveralls.io/repos/github/HEPData/hepdata-converter-ws-client/badge.svg?branch=master)](https://coveralls.io/github/HEPData/hepdata-converter-ws-client?branch=master)
[![License](https://img.shields.io/github/license/HEPData/hepdata-converter-ws-client.svg)](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/LICENSE.txt)
[![GitHub Releases](https://img.shields.io/github/release/hepdata/hepdata-converter-ws-client.svg?maxAge=2592000)](https://github.com/HEPData/hepdata-converter-ws-client/releases)
[![PyPI Version](https://img.shields.io/pypi/v/hepdata-converter-ws-client)](https://pypi.org/project/hepdata-converter-ws-client/)
[![GitHub Issues](https://img.shields.io/github/issues/hepdata/hepdata-converter-ws-client.svg?maxAge=2592000)](https://github.com/HEPData/hepdata-converter-ws-client/issues)


# hepdata-converter-ws-client

Light client wrapper for interaction with
[hepdata-converter-ws](https://github.com/HEPData/hepdata-converter-ws)
(Web Services).  It is recommended to use this wrapper instead of
manually creating requests to
[hepdata-converter-ws](https://github.com/HEPData/hepdata-converter-ws).

The reason for creating this package is the fact that the
[hepdata-converter-ws](https://github.com/HEPData/hepdata-converter-ws)
API requires compressing files into `tar.gz` format and encoding using
Base64 in order to pass them as an argument in the JSON request.
Doing this manually every time someone wants to call the
[hepdata-converter-ws](https://github.com/HEPData/hepdata-converter-ws)
API was a little cumbersome: that's why this light wrapper was born.

Additionally, the library provides additional functionality when it
comes to writing the output of the `convert` function: instead
of receiving raw `tar.gz` content it is possible to extract to a
specified file path.

## Sample usage

The library exposes one single function
`hepdata_converter_ws_client.convert` which is very similar to
`hepdata_converter.convert`.  It accepts the additional argument `url`,
and restricts input / output to `str`, `unicode` and file objects
(objects supporting `read`, `write`, `seek`, `tell`).

The `options` parameter should be the same as with the
[`hepdata_converter`](https://github.com/HEPData/hepdata-converter)
library.

The `timeout` parameter can be used to set a timeout for requests
(defaults to 600s).

The library defines the exception `hepdata_converter_ws_client.Error`
which will be thrown on timeouts or other errors connecting to the
server.

A function `hepdata_converter_ws_client.get_data_size` gets the size
in bytes of the JSON data that would be sent to the converter.  This
could be useful in checking that a maximum payload size imposed by a
web server is not exceeded.

### Function description

[`hepdata_converter_ws_client.convert`](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/hepdata_converter_ws_client/__init__.py#L23) function has proper [docstring](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/hepdata_converter_ws_client/__init__.py#L24-L68) describing its arguments and return values.
Similarly for [`hepdata_converter_ws_client.get_data_size`](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/hepdata_converter_ws_client/__init__.py#L129) with corresponding [docstring](https://github.com/HEPData/hepdata-converter-ws-client/blob/master/hepdata_converter_ws_client/__init__.py#L130-L144).

### Convert using file paths

Arguments passed as input and output can be file paths or file objects.
Below is an example of how to utilise the `convert` function with file
paths.

```python
import hepdata_converter_ws_client

# using path to input file, and writing output directly to output_path
input_path = '/path/to/input.txt'
output_path = '/path/to/output/dir'
hepdata_converter_ws_client.convert('http://hepdata-converter-ws-addr:port', input_path, output_path,
                                    options={'input_format': 'oldhepdata'})
```

### Convert using input path and output file object

Input can always be a file object (as long as the input `Parser`
supports single files).  Output can be a file object only if the
keyword argument `extract=False`.  In this case the binary content of
the returned `tar.gz` file will be written to the output file object.
It is then the responsibility of the user to decompress it.

```python
import hepdata_converter_ws_client
from io import BytesIO
# using path to input file, writing to output stream
input_path = '/path/to/input.txt'
output = BytesIO()
hepdata_converter_ws_client.convert('http://hepdata-converter-ws-addr:port', input_path, output,
                                    options={'input_format': 'oldhepdata'}, extract=False)

```

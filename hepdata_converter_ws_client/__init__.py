# -*- encoding: utf-8 -*-
import base64
import json
import os
import requests
import tarfile
import cStringIO
import tempfile
import shutil

__author__ = 'Michał Szostak'

ARCHIVE_NAME = 'hepdata-converter-ws-data'


def convert(url, input, output, options={}, id=None, extract=True):
    input_stream = cStringIO.StringIO()

    # input is a path, treat is as such
    if isinstance(input, (str, unicode)):
        assert os.path.exists(input)

        with tarfile.open(mode='w:gz', fileobj=input_stream) as tar:
            tar.add(input, arcname=ARCHIVE_NAME)
    elif hasattr(input, 'read'):
        with tarfile.open(mode='w:gz', fileobj=input_stream) as tar:
            info = tarfile.TarInfo(ARCHIVE_NAME)
            input.seek(0, os.SEEK_END)
            info.size = input.tell()
            input.seek(0)
            tar.addfile(info, fileobj=input)
    else:
        raise ValueError('input is not path or file object!')

    data = {'input': base64.encodestring(input_stream.getvalue()),
            'options': options}

    if id:
        data['id'] = id

    r = requests.get(url+'/convert', data=json.dumps(data),
                     headers={'Content-type': 'application/json', 'Accept': 'application/x-gzip'})

    if extract:
        if not isinstance(output, (str, unicode)):
            raise ValueError('if extract=True then output must be path')

        tmp_dir = tempfile.mkdtemp(suffix='hdc')
        try:
            with tarfile.open('r:gz', fileobj=cStringIO.StringIO(r.content)) as tar:
                tar.extractall(tmp_dir)
            shutil.move(os.path.join(tmp_dir, ARCHIVE_NAME), output)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        if isinstance(output, (str, unicode)):
            with open(output, 'wb') as f:
                f.write(r.content)
        elif hasattr(output, 'write'):
            output.write(r.content)
        else:
            raise ValueError('output is not path or file object')
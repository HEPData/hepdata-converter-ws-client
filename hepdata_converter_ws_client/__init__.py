# -*- encoding: utf-8 -*-
import base64
import json
import requests
import tarfile
import cStringIO
import tempfile
import shutil

__author__ = 'Michał Szostak'


def convert(url, input, output, options={}, id=None):
    input_stream = cStringIO.StringIO()
    with tarfile.open(mode='w:gz', fileobj=input_stream) as tar:
        tar.add(input, arcname='hepdata-converter-ws-data')

    data = {'input': base64.encode(input_stream.getvalue()),
            'options': options}

    if id:
        data['id'] = id

    r = requests.get(url, data=json.dump(data),
                     headers={'Content-type': 'application/json', 'Accept': 'application/x-gzip'})

    tmp_dir = tempfile.mkdtemp(suffix='hdc')
    try:
        with tarfile.open('r:gz', fileobj=cStringIO.StringIO(r.data)) as tar:
            tar.extractall(tmp_dir)
        shutil.move(tmp_dir+'/*', output)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
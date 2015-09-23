# -*- encoding: utf-8 -*-
import requests
import tarfile
from threading import Thread
import time
import StringIO
from flask.globals import request
from hepdata_converter.testsuite import insert_path, TMPDirMixin, ExtendedTestCase, insert_data_as_file
from hepdata_converter_ws_client import ARCHIVE_NAME
from hepdata_converter_ws import create_app
import hepdata_converter_ws_client
import os

__author__ = 'Michał Szostak'


class ConvertTestCase(TMPDirMixin, ExtendedTestCase):
    PORT = 8945

    def tearDown(self):
        super(ConvertTestCase, self).tearDown()
        requests.post(self.get_server_url()+self.get_server_kill_route())
        self.server.join()

    def setUp(self):
        super(ConvertTestCase, self).setUp()
        
        class ServerThread(Thread):
            def run(self):
                app = create_app()
                app.config['TESTING'] = True
                app.config['LIVESERVER_PORT'] = ConvertTestCase.PORT

                # this route has to be added in order to ensure server is killed on
                # tearDown
                @app.route(ConvertTestCase.get_server_kill_route(), methods=['POST'])
                def shutdown():
                    request.environ.get('werkzeug.server.shutdown')()
                    return 'Server shutting down...'

                # Debug must be set to false - otherwise flask will try to bind signal,
                # which is not possible in the thread (not main process)
                app.run(port=ConvertTestCase.PORT, debug=False)

        self.server = ServerThread()
        self.server.start()
        time.sleep(1)

    def get_server_url(self):
        return 'http://localhost:%s' % self.PORT

    @classmethod
    def get_server_kill_route(cls):
        return '/__kill__'

    @insert_path('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_convert(self, oldhepdata_path, oldhepdata_yaml_path):
        # test paths
        path = os.path.join(self.current_tmp, 'yaml')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, path,
                                            options={'input_format': 'oldhepdata'})

        self.assertDirsEqual(oldhepdata_yaml_path, path)

    @insert_data_as_file('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_convert_fileobj(self, oldhepdata_file, oldhepdata_yaml_path):
        # test fileobj
        path = os.path.join(self.current_tmp, 'yaml')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_file, path,
                                            options={'input_format': 'oldhepdata'})

        self.assertDirsEqual(oldhepdata_yaml_path, path)

    @insert_data_as_file('oldhepdata/sample.input')
    def test_convert_wrong_args(self, oldhepdata_file):
        self.assertRaises(ValueError,
                          hepdata_converter_ws_client.convert,
                          self.get_server_url(), object(), self.current_tmp,
                          options={'input_format': 'oldhepdata'})

        self.assertRaises(ValueError,
                          hepdata_converter_ws_client.convert,
                          self.get_server_url(), oldhepdata_file, object(),
                          options={'input_format': 'oldhepdata'}, extract=False)



    @insert_path('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_caching(self, oldhepdata_path, oldhepdata_yaml_path):
        # test paths
        path_1 = os.path.join(self.current_tmp, 'yaml', '1')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, path_1,
                                            options={'input_format': 'oldhepdata'}, id=1)

        self.assertDirsEqual(oldhepdata_yaml_path, path_1)

        path_2 = os.path.join(self.current_tmp, 'yaml', '2')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, path_2,
                                            options={'input_format': 'oldhepdata'}, id=1)

        self.assertDirsEqual(oldhepdata_yaml_path, path_2)

        self.assertDirsEqual(path_1, path_2)

    @insert_path('oldhepdata/sample.input')
    def test_extract_error(self, oldhepdata_path):
        output = StringIO.StringIO()
        self.assertRaises(ValueError,
                          hepdata_converter_ws_client.convert,
                          self.get_server_url(), oldhepdata_path, output,
                          options={'input_format': 'oldhepdata'})

    @insert_data_as_file('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_convert_fileobj(self, oldhepdata_file, oldhepdata_yaml_path):
        # test fileobj
        path = os.path.join(self.current_tmp, 'yaml')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_file, path,
                                            options={'input_format': 'oldhepdata'})

        self.assertDirsEqual(oldhepdata_yaml_path, path)

    @insert_path('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_convert_no_extract(self, oldhepdata_path, oldhepdata_yaml_path):
        output = StringIO.StringIO()
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, output,
                                            options={'input_format': 'oldhepdata'}, extract=False)
        output.seek(0)
        tmp_path = os.path.join(self.current_tmp, '1')
        with tarfile.open(mode='r:gz', fileobj=output) as tar:
            tar.extractall(tmp_path)
        self.assertDirsEqual(os.path.join(tmp_path, ARCHIVE_NAME),
                             oldhepdata_yaml_path)

        path = os.path.join(self.current_tmp, 'data.tar.gz')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, path,
                                            options={'input_format': 'oldhepdata'}, extract=False)

        tmp_path = os.path.join(self.current_tmp, '2')

        with tarfile.open(path, mode='r:gz') as tar:
            tar.extractall(tmp_path)
        self.assertDirsEqual(os.path.join(tmp_path, ARCHIVE_NAME),
                             oldhepdata_yaml_path)
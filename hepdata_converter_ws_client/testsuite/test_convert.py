# -*- encoding: utf-8 -*-
import tarfile
from io import StringIO, BytesIO
import os
import requests

from hepdata_converter_ws_client.testsuite import insert_path, insert_data_as_binary_file, insert_data_as_extracted_dir, TMPDirMixin, ExtendedTestCase
from hepdata_converter_ws_client import ARCHIVE_NAME
import hepdata_converter_ws_client

__author__ = 'Michał Szostak'


class ConvertTestCase(TMPDirMixin, ExtendedTestCase):
    PORT = 8945

    def get_server_url(self):
        return 'http://localhost:%s' % self.PORT

    @insert_path('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_convert(self, oldhepdata_path, oldhepdata_yaml_path):
        # test paths
        path = os.path.join(self.current_tmp, 'yaml')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, path,
                                            options={'input_format': 'oldhepdata'})

        self.assertDirsEqual(oldhepdata_yaml_path, path)

    @insert_data_as_binary_file('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_convert_fileobj(self, oldhepdata_file, oldhepdata_yaml_path):
        # test fileobj
        path = os.path.join(self.current_tmp, 'yaml')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_file, path,
                                            options={'input_format': 'oldhepdata'})

        self.assertDirsEqual(oldhepdata_yaml_path, path)

    @insert_data_as_extracted_dir('testsubmission/TestHEPSubmission.zip')
    @insert_path('testsubmission/yaml')
    def test_convert_zip_with_resources(self, testsubmission_file, testsubmission_yaml_path):
        # test zip
        path = os.path.join(self.current_tmp, 'yaml')
        hepdata_converter_ws_client.convert(self.get_server_url(), testsubmission_file, path,
                                            options={'input_format': 'yaml'})
        self.assertDirsEqual(testsubmission_yaml_path, path)

    @insert_path('oldhepdata/invalidsample.oldhepdata')
    def test_convert_invalid(self, oldhepdata_path):
        # test paths
        path = os.path.join(self.current_tmp, 'yaml')
        ret = hepdata_converter_ws_client.convert(self.get_server_url(),
                                                  oldhepdata_path, path,
                                                  options={'input_format': 'oldhepdata'})

        assert(ret is False)
        with open(path, 'r') as f:
            data = f.read()
            assert('BadFormat: line can not be parsed: doi: 10.1007/JHEP03(2013)128'
                   in data)
            f.close()

    @insert_data_as_binary_file('oldhepdata/sample.input')
    def test_convert_wrong_args(self, oldhepdata_file):
        self.assertRaises(ValueError,
                          hepdata_converter_ws_client.convert,
                          self.get_server_url(), object(), self.current_tmp,
                          options={'input_format': 'oldhepdata'})

        self.assertRaises(ValueError,
                          hepdata_converter_ws_client.convert,
                          self.get_server_url(), oldhepdata_file, object(),
                          options={'input_format': 'oldhepdata'}, extract=False)

    @insert_data_as_binary_file('oldhepdata/sample.input')
    def test_convert_timeout(self, oldhepdata_file):
        broken_url = 'https://example.com:81'

        with self.assertRaises(hepdata_converter_ws_client.Error) as cm:
            hepdata_converter_ws_client.convert(
                broken_url,
                oldhepdata_file,
                self.current_tmp,
                options={'input_format': 'oldhepdata'},
                timeout=5
            )

        self.assertEqual('Request to %s failed' % broken_url,
                         str(cm.exception))
        self.assertTrue(isinstance(cm.exception.__cause__, (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError)))
        self.assertTrue(str(cm.exception.__cause__).startswith(
            "HTTPSConnectionPool(host='example.com', port=81): Max retries exceeded with url"
        ))

    @insert_data_as_binary_file('oldhepdata/sample.input')
    def test_convert_404(self, oldhepdata_file):
        broken_url = self.get_server_url() + '/notavalidurl'

        with self.assertRaises(hepdata_converter_ws_client.Error) as cm:
            hepdata_converter_ws_client.convert(
                          broken_url,
                          oldhepdata_file,
                          self.current_tmp,
                          options={'input_format': 'oldhepdata'},
                          timeout=5)

        self.assertEqual('Request to %s failed' % broken_url,
                         str(cm.exception))
        self.assertTrue(isinstance(cm.exception.__cause__, requests.exceptions.HTTPError))
        self.assertTrue(str(cm.exception.__cause__).startswith(
            "404 Client Error: NOT FOUND for url: %s" % broken_url
        ))

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
        output = StringIO()
        self.assertRaises(ValueError,
                          hepdata_converter_ws_client.convert,
                          self.get_server_url(), oldhepdata_path, output,
                          options={'input_format': 'oldhepdata'})

    @insert_data_as_binary_file('oldhepdata/sample.input')
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
        output = BytesIO()
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, output,
                                            options={'input_format': 'oldhepdata'}, extract=False)
        output.seek(0)
        tmp_path = os.path.join(self.current_tmp, '1')
        with tarfile.open(mode='r:gz', fileobj=output) as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, tmp_path)
        self.assertDirsEqual(os.path.join(tmp_path, ARCHIVE_NAME),
                             oldhepdata_yaml_path)

        path = os.path.join(self.current_tmp, 'data.tar.gz')
        hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_path, path,
                                            options={'input_format': 'oldhepdata'}, extract=False)

        tmp_path = os.path.join(self.current_tmp, '2')

        with tarfile.open(path, mode='r:gz') as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, tmp_path)
        self.assertDirsEqual(os.path.join(tmp_path, ARCHIVE_NAME),
                             oldhepdata_yaml_path)

    @insert_data_as_binary_file('oldhepdata/sample.input')
    @insert_path('oldhepdata/yaml')
    def test_return_value(self, oldhepdata_file, oldhepdata_yaml_path):
        # test fileobj
        path = os.path.join(self.current_tmp, 'yaml')
        r = hepdata_converter_ws_client.convert(self.get_server_url(), oldhepdata_file,
                                                options={'input_format': 'oldhepdata'})

        with tarfile.open(mode='r:gz', fileobj=BytesIO(r)) as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path)

        self.assertDirsEqual(oldhepdata_yaml_path, os.path.join(path, ARCHIVE_NAME))

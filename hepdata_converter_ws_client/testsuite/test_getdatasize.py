from hepdata_converter_ws_client.testsuite import insert_path, \
    insert_data_as_extracted_dir, TMPDirMixin, ExtendedTestCase
import hepdata_converter_ws_client


class GetDataSizeTestCase(TMPDirMixin, ExtendedTestCase):

    @insert_path('oldhepdata/sample.input')
    def test_get_data_size_old(self, oldhepdata_path):
        size = hepdata_converter_ws_client.get_data_size(
            oldhepdata_path, options={'input_format': 'oldhepdata'}
        )
        self.assertAlmostEqual(size, 7428, delta=10)

    @insert_data_as_extracted_dir('testsubmission/TestHEPSubmission.zip')
    def test_get_data_size_with_resources(self, testsubmission_file):
        size = hepdata_converter_ws_client.get_data_size(
            testsubmission_file, options={'input_format': 'yaml'})
        self.assertAlmostEqual(size, 4522, delta=10)

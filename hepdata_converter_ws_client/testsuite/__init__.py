# -*- encoding: utf-8 -*-

from hepdata_converter.testsuite import construct_testdata_path

__author__ = 'Michał Szostak'


class insert_data_as_binary_file(object):
    def __init__(self, *sample_file_name):
        if len(sample_file_name) > 0:
            self.sample_file_name = sample_file_name[0].split('/')

    def __call__(self, function):
        def _inner(*args, **kwargs):
            args = list(args)
            with open(construct_testdata_path(self.sample_file_name), 'rb') as f:
                args.append(f)
                function(*args, **kwargs)

        return _inner

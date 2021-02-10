# -*- encoding: utf-8 -*-

__author__ = 'Michał Szostak'

import os
from random import randint
import shutil
import tempfile
import time
import unittest
import yaml

# We try to load using the CSafeLoader for speed improvements.
try:
    from yaml import CSafeLoader as Loader
except ImportError: #pragma: no cover
    from yaml import SafeLoader as Loader #pragma: no cover


def _parse_path_arguments(sample_file_name):
    _sample_file_name = list(sample_file_name)
    sample_file_name = []
    for path_element in _sample_file_name:
        sample_file_name += path_element.split('/')

    return sample_file_name


def construct_testdata_path(path_elements):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata', *path_elements)


class TMPDirMixin(object):
    def tearDown(self):
        shutil.rmtree(self.current_tmp)

    def setUp(self):
        self.current_tmp = os.path.join(tempfile.gettempdir(), str(int(time.time()))) + str(randint(0, 10000))
        try:
            os.mkdir(self.current_tmp)
        finally:
            pass


class insert_data_as_binary_file(object):
    def __init__(self, *sample_file_name):
        self.sample_file_name = _parse_path_arguments(sample_file_name)

    def __call__(self, function):
        def _inner(*args, **kwargs):
            args = list(args)
            with open(construct_testdata_path(self.sample_file_name), 'rb') as f:
                args.append(f)
                function(*args, **kwargs)

        return _inner


class insert_data_as_extracted_dir(object):
    def __init__(self, *sample_file_name):
        self.sample_file_name = _parse_path_arguments(sample_file_name)
        self.temp_path = tempfile.gettempdir()

    def __call__(self, function):
        def _inner(*args, **kwargs):
            args = list(args)
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.unpack_archive(construct_testdata_path(self.sample_file_name), temp_dir)
                # Assume zips consist of a single directory
                unpacked_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                args.append(unpacked_dir)
                function(*args, **kwargs)

        return _inner


class insert_path(object):
    def __init__(self, *sample_file_name):
        self.sample_file_name = _parse_path_arguments(sample_file_name)

    def __call__(self, function):
        def _inner(*args, **kwargs):
            args = list(args)
            args.append(construct_testdata_path(self.sample_file_name))
            function(*args, **kwargs)

        return _inner


class ExtendedTestCase(unittest.TestCase):
    def assertMultiLineAlmostEqual(self, first, second, msg=None):
        if hasattr(first, 'readlines'):
            lines = first.readlines()
        elif isinstance(first, (str, str)):
            lines = first.split('\n')

        if hasattr(second, 'readlines'):
            orig_lines = second.readlines()
        elif isinstance(second, (str, str)):
            orig_lines = second.split('\n')

        self.assertEqual(len(lines), len(orig_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i].strip(), orig_lines[i].strip())

    def assertDirsEqual(self, first_dir, second_dir,
                        file_content_parser=lambda x: list(yaml.load_all(x, Loader=Loader)),
                        exclude=[], msg=None):
        self.assertEqual(list(os.walk(first_dir))[1:], list(os.walk(second_dir))[1:], msg)
        dirs = list(os.walk(first_dir))
        for file in dirs[0][2]:
            if file not in exclude:
                with open(os.path.join(first_dir, file)) as f1, open(os.path.join(second_dir, file)) as f2:
                    # separated into 2 variables to ease debugging if the need arises
                    d1 = file_content_parser(f1.read())
                    d2 = file_content_parser(f2.read())
                    self.assertEqual(d1, d2)

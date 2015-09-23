# -*- encoding: utf-8 -*-
import os
import subprocess
import sys
from hepdata_converter.testsuite.test_writer import WriterTestSuite

__author__ = 'Michał Szostak'

import unittest


class SetupTestCase(WriterTestSuite):
    def test_setup(self):
        # specyfing root is a hack, without it --dry-run still fails because of ACL
        r = subprocess.call([sys.executable, 'setup.py', '--dry-run', 'install', '--root', self.current_tmp])
        self.assertEqual(r, 0)

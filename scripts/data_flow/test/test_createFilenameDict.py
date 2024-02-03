#! /usr/bin/python3

import unittest
import imp
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import *

class TEST_createFilenameDict(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', os.environ['PROJ_DIR'] + '/' + 'scripts/data_flow/push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.createFilenameDict()

    def tearDown(self):
        pass

    def test_createFilenameDict(self):
        self.assertTrue(isinstance(self.fielddata.filename, dict))


if __name__ == '__main__':
    unittest.main()

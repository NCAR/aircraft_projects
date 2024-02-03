#! /usr/bin/python3

import unittest
import imp
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')

from fieldProc_setup import *

class TEST_createFileExt(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', os.environ['PROJ_DIR'] + '/' + 'scripts/data_flow/push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)

    def tearDown(self):
        pass

    def test_createFileExt(self):
        self.assertTrue(isinstance(self.fielddata.file_ext, dict))


if __name__ == '__main__':
    unittest.main()

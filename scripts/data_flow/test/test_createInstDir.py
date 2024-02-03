#! /usr/bin/python3

import unittest
import imp
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import *

class TEST_createInstDir(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', os.environ['PROJ_DIR'] + '/' + 'scripts/data_flow/push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.createInstDir(os.environ['RAW_DATA_DIR'] + '/' + os.environ['PROJECT'], '/scr/raf_data/TI3GER/', 'TI3GER', 'cf01')

    def tearDown(self):
        pass

    def test_createInstDir(self):
        self.assertTrue(isinstance(self.fielddata.inst_dir, dict))


if __name__ == '__main__':
    unittest.main()

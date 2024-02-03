#! /usr/bin/python3

import unittest
import imp
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import *

class TEST_createRate(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', os.environ['PROJ_DIR'] + '/' + 'scripts/data_flow/push_data.py')        
        self.fielddata = push_data.FieldData()
        self.fielddata.createRate()

    def tearDown(self):
        pass

    def test_createRate(self):
        self.assertTrue(isinstance(self.fielddata.rate, dict))


if __name__ == '__main__':
    unittest.main()

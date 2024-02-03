#! /usr/bin/python3

import unittest
import imp
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import *

class TEST_find_lrt_netcdf(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', os.environ['PROJ_DIR'] + '/' + 'scripts/data_flow/push_data.py')
        self.fielddata = push_data.FieldData()
        ##Added in arguments filetype, flight, data_dir, file_prefix
        self.fielddata.find_lrt_netcdf('nc', 'CAESAREMI', '/Users/srunkel/dev/projects/CAESAR/', 'pre')

    def tearDown(self):
        pass
    
    def test_find_lrt_netcdf(self):
        self.assertTrue(isinstance(self.fielddata.rate, dict))


if __name__ == '__main__':
    unittest.main()

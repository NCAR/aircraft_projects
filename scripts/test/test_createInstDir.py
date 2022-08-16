#! /usr/bin/python3

import unittest
import imp
import sys
sys.path.insert(0, '/net/jlocal/projects/TI3GER/GV_N677F/' + '/scripts')
from fieldProc_setup import *

class TEST_createInstDir(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', '/scr/tmp/taylort/aircraft_projects/scripts/push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.createInstDir('/scr/raf_Raw_Data/TI3GER/', '/scr/raf_data/TI3GER/', 'TI3GER', 'cf01')

    def tearDown(self):
        pass

    def test_createInstDir(self):
        self.assertTrue(isinstance(self.fielddata.inst_dir, dict))


if __name__ == '__main__':
    unittest.main()

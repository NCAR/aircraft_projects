#! /usr/bin/python3

import unittest
import imp
import sys
sys.path.insert(0, '/net/jlocal/projects/TI3GER/GV_N677F/' + '/scripts')
from fieldProc_setup import *

class TEST_createConfigExt(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', '/scr/tmp/taylort/aircraft_projects/scripts/push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.createConfigExt()

    def tearDown(self):
        pass

    def test_createRate(self):
        self.assertTrue(isinstance(self.fielddata.config_ext, dict))


if __name__ == '__main__':
    unittest.main()

#! /usr/bin/python3

import unittest
import imp
import sys
import os
sys.path.append('/Users/srunkel/dev/aircraft_projects/scripts/data_flow/')
import push_data

class TEST_init(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', 'push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.getProject()
        self.fielddata.getDataDir()
        self.fielddata.getRawDir()
        self.fielddata.getProjDir()

    def tearDown(self):
        pass

    def test_getProject(self):
        self.assertTrue(self.fielddata.project == 'CAESAR')

    def test_getDataDir(self):
        self.assertTrue(self.fielddata.data_dir == '/Users/srunkel/dev/projects/CAESAR/')

    def test_getRawDir(self):
        print(self.fielddata.raw_dir )
        self.assertTrue(self.fielddata.raw_dir == '/Users/srunkel/dev/projects/CAESAR/')

    def test_aircraft(self):
        self.assertTrue(self.fielddata.aircraft == 'C130_N130AR')

    def test_proj_dir(self):
        self.assertTrue(self.fielddata.proj_dir == '/Users/srunkel/dev/aircraft_projects/CAESAR/C130_N130AR/')

    def test_nc2ascBatch(self):
        self.assertTrue(self.fielddata.nc2ascBatch == '/Users/srunkel/dev/aircraft_projects/CAESAR/C130_N130AR/scripts/nc2asc.bat')

    def test_zip_dir(self):
        self.assertTrue(self.fielddata.zip_dir == '/tmp/')

    def test_qc_ftp_site(self):
        self.assertTrue(self.fielddata.qc_ftp_site == 'catalog.eol.ucar.edu')

    def test_qc_ftp_dir(self):
        self.assertTrue(self.fielddata.qc_ftp_dir == '/pub/incoming/catalog/caesar')


if __name__ == '__main__':
    unittest.main()

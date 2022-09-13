#! /usr/bin/python3

import unittest
import imp
import sys
sys.path.append('/scr/tmp/taylort/aircraft_projects/scripts/')
import push_data


class TEST_init(unittest.TestCase):

    def setUp(self):
        push_data = imp.load_source('push_data', '/scr/tmp/taylort/aircraft_projects/scripts/push_data.py')
        self.fielddata = push_data.FieldData()
        self.fielddata.getProject()
        self.fielddata.getDataDir()
        self.fielddata.getRawDir()
        self.fielddata.getProjDir()

    def tearDown(self):
        pass

    def test_getProject(self):
        self.assertTrue(self.fielddata.project == 'TI3GER')

    def test_getDataDir(self):
        self.assertTrue(self.fielddata.data_dir == '/scr/raf_data/TI3GER/')

    def test_getRawDir(self):
        self.assertTrue(self.fielddata.raw_dir == '/scr/raf_Raw_Data/TI3GER/')

    def test_aircraft(self):
        self.assertTrue(self.fielddata.aircraft == 'GV_N677F')

    def test_proj_dir(self):
        self.assertTrue(self.fielddata.proj_dir == '/net/jlocal/projects/TI3GER/GV_N677F/')

    def test_nc2ascBatch(self):
        self.assertTrue(self.fielddata.nc2ascBatch == '/net/jlocal/projects/TI3GER/GV_N677F/scripts/nc2asc.bat')

    def test_zip_dir(self):
        self.assertTrue(self.fielddata.zip_dir == '/tmp/')

    def test_qc_ftp_site(self):
        self.assertTrue(self.fielddata.qc_ftp_site == 'catalog.eol.ucar.edu')

    def test_qc_ftp_dir(self):
        self.assertTrue(self.fielddata.qc_ftp_dir == '/pub/incoming/catalog/ti3ger')


if __name__ == '__main__':
    unittest.main()

import _logging, _GDrive, _process, _setup,_NAS,_FTP,_findfiles
from Status import STATUS
import logging
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, datadump, GDRIVE, rclone_staging_dir



class FieldData():

    def __init__(self):
        self.setup = _setup.Setup()
        self.myLogger=self.setup.myLogger
        self.project = self.setup.PROJECT
        print(f'Project: {self.project}')
        self.data_dir = f'{self.setup.DATADIR}/{self.project.upper()}/'
        self.raw_dir = f'{self.setup.RAWDIR}/{self.project.upper()}/'
        self.aircraft = self.setup.AIRCRAFT#os.listdir(f'{self.setup.PROJDIR}/{self.project}')[0]
        print(f'Aircraft: {self.aircraft}')
        self.proj_dir = f'{self.setup.PROJDIR}/{self.project}/{self.aircraft}/'
        self.zip_dir = '/tmp/'
        self.qc_ftp_site = 'catalog.eol.ucar.edu'
        self.qc_ftp_dir = f'/pub/incoming/catalog/{self.project.lower()}'
        self.flight = self.setup.FLIGHT
        self.email = self.setup.EMAIL
        self.rclone_staging_dir = rclone_staging_dir
        self.process = False
        self.reprocess = False
        
        

        self.setup.setup(self.aircraft, self.project, self.raw_dir)
        self.inst_dir = self.setup.INST_DIR
        self.file_ext = self.setup.FILE_EXT
        self.filename = {}
        self.file_type = self.setup.FILE_TYPE
        self.rate = self.setup.RATE
        self.config_ext = self.setup.CONFIG_EXT
        self.status = STATUS
        self.file_prefix = self.setup.FILE_PREFIX
        self.myLogger.ensure_dir(self.data_dir)
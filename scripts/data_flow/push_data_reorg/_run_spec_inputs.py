import os
import re
import glob
import ftplib
import sys
import datetime
import smtplib
import argparse
from email.mime.text import MIMEText
from collections import OrderedDict
import logging

sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, \
    NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, \
    SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, \
    datadump, GDRIVE, rclone_staging_dir




class Project_Constants(self):
    def __init__(self):
        self.FILE_EXT = self.create_FileExt()
        self.PROJECT = self.read_env('PROJECT')
        self.AIRCRAFT = self.read_env('AIRCRAFT')
        self.DATA_DIR = f'{self.read_env('DATA_DIR')}/{self.PROJECT.upper()}/'
        self.raw_dir = f'{self.read_env('RAW_DATA_DIR')}/{self.PROJECT.upper()}/'
        self.proj_dir = f'{self.read_env('PROJ_DIR')}/{self.PROJECT}/{self.aircraft}/'
        self.QC_FTP_DIR = '/pub/incoming/catalog/' + self.PROJECT.lower()

    '''
    Create an ordered dictionary containing the file extensions by
    file type. Uses the settings from fieldProc_setup.py
    '''
    def create_FileExt(self):
        _fileExt = {'HRT': {'inc': HRT, 'ext': 'nc'}, 'SRT': {'inc': SRT, 'ext': 'nc'},
                    'ICARTT': {'inc': ICARTT, 'ext': 'ict'}, 'IWG1': {'inc': IWG1, 'ext': 'iwg'},
                    'PM2SD': {'inc': PMS2D, 'ext': '2d'}, 'threeVCPI': {'inc': threeVCPI, 'ext': '2ds'}}
        self.FILE_EXT = OrderedDict([("ADS", "ads"), ("LRT", "nc"), ("KML", "kml")])
        for type in _fileExt:
            if _fileExt[type['inc']]:
                self.FILE_EXT[type] = _fileExt[type['ext']]
        return self.FILE_EXT

    def read_env(self, env_var):
        '''
        Read and set environment var
        '''
        try:
            var = os.environ[env_var]
            return (var)
        except KeyError:
            message = 'Please set the environment variable ' + env_var
            self.logger.error(message)
            print(message)
            sys.exit(1)







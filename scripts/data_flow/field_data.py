import _logging, _GDrive, _process, _setup,_NAS,_FTP,_findfiles
from Status import STATUS
import logging
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, datadump, GDRIVE, rclone_staging_dir

setup = _setup.Setup()

class FieldData():

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler('/tmp/push_data.log')
        self.formatter = logging.Formatter('%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.project = setup.getProject()
        print(f'Project: {self.project}')
        self.data_dir = f'{setup.getDataDir()}/{self.project.upper()}/'
        self.raw_dir = f'{setup.getRawDir()}/{self.project.upper()}/'
        self.aircraft = os.listdir(f'{setup.getProjDir()}/{self.project}')[0]
        print(f'Aircraft: {self.aircraft}')
        self.proj_dir = f'{setup.getProjDir()}/{self.project}/{self.aircraft}/'
        self.nc2ascBatch = f'{self.proj_dir}scripts/nc2asc.bat'
        self.zip_dir = '/tmp/'
        self.qc_ftp_site = 'catalog.eol.ucar.edu'
        self.qc_ftp_dir = f'/pub/incoming/catalog/{self.project.lower()}'
        self.flight = setup.readFlight()
        self.email = setup.readEmail()
        self.rclone_staging_dir = rclone_staging_dir
        self.process = False
        self.reprocess = False

        setup.setup(self.aircraft, self.project, self.raw_dir)
        setup.createInstDir(self.raw_dir, self.data_dir, self.project, self.flight)
        setup.createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)
        setup.createFilenameDict()
        setup.createFileType()
        setup.createRate()
        setup.createConfigExt()
        self.status = STATUS
        setup.createFilePrefix(self.project, self.flight)
        _logging._initializeFinalMessage(self.flight, self.project)
        _logging.ensureDataDir(self.data_dir)
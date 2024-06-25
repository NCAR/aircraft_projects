from email.mime.text import MIMEText
import smtplib
import _logging, _GDrive, _process, _setup,_NAS,_FTP,_findfiles
from Status import STATUS
import logging
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import rclone_staging_dir, sendzipped



class FieldData():

    def __init__(self):
        
        ##Create the single instance of the setup class
        self.setup = _setup.Setup()
        
        #Ge the Logger 
        self.final_message = self.setup.final_message
        self.project = self.setup.PROJECT
        print(f'Project: {self.project}')
        self.data_dir = f'{self.setup.DATADIR}/{self.project.upper()}/'
        self.raw_dir = f'{self.setup.RAWDIR}/{self.project.upper()}/'
        self.aircraft = self.setup.AIRCRAFT#os.listdir(f'{self.setup.PROJDIR}/{self.project}')[0]
        print(f'Aircraft: {self.aircraft}')
        self.proj_dir = f'{self.setup.PROJDIR}/{self.project}/{self.aircraft}/'
        self.qc_ftp_site = 'catalog.eol.ucar.edu'
        self.qc_ftp_dir = f'/pub/incoming/catalog/{self.project.lower()}'
        self.flight = self.setup.FLIGHT
        self.email = self.setup.EMAIL
        self.rclone_staging_dir = rclone_staging_dir
        self.inst_dir = self.setup.INST_DIR
        self.file_ext = self.setup.FILE_EXT
        self.filename = {}
        self.file_type = self.setup.FILE_TYPE
        self.rate = self.setup.RATE
        self.config_ext = self.setup.CONFIG_EXT
        self.status = STATUS
        self.file_prefix = self.setup.FILE_PREFIX
        self.myLogger.ensure_dir(self.data_dir)
        
        self.process = False
        self.reprocess = False
        
        ##Steps to prepare for processing
        self.setup.setup_email(self.data_dir, self.email)
        self.setup.setup(self.aircraft, self.project, self.raw_dir)
        # Zip files only if set to True
        if sendzipped:
            self.setup.setup_zip(self.file_ext, self.data_dir, self.filename, self.inst_dir)
    def report(self, final_message, status, project, flight, email, file_ext):
        final_message = final_message + '\nREPORT on shipping of files. \n\n'
        final_message = final_message + 'File Type\tStor\tShip\n'

        for key in file_ext:
            final_message = final_message + key + '\t\t' + str(status[key]["stor"]) + '\t' + str(status[key]["ship"]) + '\n'

        final_message = final_message + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

        print(final_message)
        msg = MIMEText(final_message)
        msg['Subject'] = f'Process & Push message for:{project}  flight:{flight}'
        msg['From'] = 'ads@groundstation'
        msg['To'] = email

        s = smtplib.SMTP('localhost')
        s.sendmail('ads@groundstation', email, msg.as_string())
        s.quit()

        print("\r\nSuccessful completion. Close window to exit.")
        
        
        
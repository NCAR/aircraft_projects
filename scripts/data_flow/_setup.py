##Functions that help initiate push_data
from collections import OrderedDict
from email.mime.text import MIMEText
import smtplib
import sys, os
import _logging
import logging
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import  ICARTT, IWG1, HRT, SRT, PMS2D, threeVCPI, sendzipped

myLogger = _logging.MyLogger()
class Setup:
    def __init__(self):
        self.init_logger()
        self.myLogger = myLogger
        self.PROJECT = self.read_env('PROJECT')
        self.DATA_DIR = f"{self.read_env('DATA_DIR')}/{self.PROJECT.upper()}/"
        self.RAW_DIR = f"{self.read_env('RAW_DATA_DIR')}/{self.PROJECT.upper()}/"
        self.PROJDIR = self.read_env('PROJ_DIR')
        self.AIRCRAFT = self.read_env('AIRCRAFT')
        self.PROJ_DIR = f'{self.PROJDIR}/{self.PROJECT}/{self.AIRCRAFT}/'
        
        self.createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)
        self.readFlight()
        self.readEmail()
        self.createInstDir(self.RAW_DIR, self.DATA_DIR, self.PROJECT, self.FLIGHT)
        self.createRate()
        self.createConfigExt()
        self.FILENAME = {}
        self.createFilePrefix(self.PROJECT, self.FLIGHT)
        self.setup(self.AIRCRAFT,self.PROJECT, self.RAW_DIR)
        self.createFileType()
        self.initializeFinalMessage(self.FLIGHT,self.PROJECT)
        
        
        self.setup_email(self.DATA_DIR, self.EMAIL)
        self.setup(self.AIRCRAFT, self.PROJECT, self.RAW_DIR)
        self.create_status()
        # Zip files only if set to True       

    
    def create_status(self):
        self.STATUS = {"ADS": {"proc": "N/A", "ship": "No!", "stor": "No!"},
                        "LRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "KML": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "HRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "SRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "ICARTT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "IWG1": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "PMS2D": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "threeVCPI": {"proc": "No!", "ship": "No!", "stor": "No!"},
                        "QCplots": {"proc": "No!", "ship": "No!", "stor": "No!"}}

    def init_logger(self):
        logger = logging.getLogger('myLogger')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/tmp/push_data.log')
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
            
    def report(self, status, project, flight, email, file_ext,final_message):
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
            
    def initializeFinalMessage(self, flight, project):
        '''
        Prepare for final message information
        '''
        self.final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
        self.final_message = (
            f'{self.final_message}Process and Push log for Project:{project}'
        )
        self.final_message = f'{self.final_message}  Flight:{flight}' + '\r\n'

    def createFileType(self):
            '''
            NetCDF filename rate indicator
            '''
            self.FILE_TYPE = {
                "ADS": "",
                "LRT": "",
                "KML": "",
                "HRT": "h",
                "SRT": "s",
                "ICARTT": "",
                "IWG1": "",
                "PMS2D": "",
                }
    def createFilePrefix(self, project, flight):
            '''
            Create the project- and flight-specific filename prefix (e.g. WECANrf01)
            '''
            self.FILE_PREFIX= project + flight

    def createFileExt(self, HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI):
        '''
        Create an ordered dictionary containing the file extensions by
        file type. Uses the settings from fieldProc_setup.py
        '''
        self.FILE_EXT = OrderedDict([("ADS", "ads"), ("LRT", "nc"), ("KML", "kml")])
        if HRT:
            self.FILE_EXT["HRT"] = "nc"
        if SRT:
            self.FILE_EXT["SRT"] = "nc"
        if ICARTT:
            self.FILE_EXT["ICARTT"] = "ict"
        if IWG1:
            self.FILE_EXT["IWG1"] = "iwg"
        if PMS2D:
            self.FILE_EXT["PMS2D"] = "2d"
        if threeVCPI:
            self.FILE_EXT["threeVCPI"] = "2ds"

        return self.FILE_EXT

    def createRate(self):
            '''
            nimbus processing rates (for use in config files)
            '''
            self.RATE = {
                "LRT": "1",
                "HRT": "25",
                "SRT": "0",
                }

    def createConfigExt(self):
        '''
        nimbus config filename extensions
        '''
        self.CONFIG_EXT = {"LRT": "", "HRT": "h", "SRT": "s", }

    def setup(self, aircraft, project, raw_dir):
        """
        Create objects for multiple processing inputs
        """
        if aircraft == "GV_N677F":
            raircraft = 'aircraft.NSF_NCAR_GV.'
        elif aircraft == "C130_N130AR":
            raircraft = 'aircraft.NSF_NCAR_C-130.'
        else:
            message = f"Unknown aircraft {aircraft}" + " Update code\n"
            myLogger.log_and_print(message)
            sys.exit(1)
        message = f"Processing {project} from {aircraft}.\nIf incorrect, edit ~/ads3_environment.\n Expecting to find .ads files in {raw_dir}."
        myLogger.log_and_print(message)  
        return raircraft

    def readFlight(self):
        '''
        Read user input to determine the event
        '''
        self.FLIGHT = input('Input flight designation (e.g. tf01):')

    def readEmail(self):
        '''
        Read user input to determine the email address
        '''
        self.EMAIL = input('Input email address to send results:')

    def read_env(self, env_var):
        '''
        Read and set environment var
        '''
        try:
            return os.environ[env_var]
        except KeyError:
            myLogger.log_and_print(f'Please set the environment variable {env_var}')
            sys.exit(1)


    def setup_email(self, data_dir, email):
        """
            Set up email
            """
        emailfilename = 'email.addr.txt'
        emailfile = data_dir+emailfilename
        command = 'rm '+emailfile
        os.system(command)
        with open(emailfile, 'w+') as fo:
            fo.write(email+'\n')


    ##Maybe this will go in separate zip folder


                
    def createInstDir(self, raw_dir, data_dir, project, flight):
        '''
        These are directories where instrument-specific data files (not
        RAF standard data) can be found.
        '''
        self.INST_DIR= {
                "ADS": raw_dir,
                "LRT": data_dir,
                "KML": data_dir,
                "HRT": data_dir,
                "SRT": data_dir,
                "ICARTT": data_dir,
                "IWG1": data_dir,
                "PMS2D": raw_dir,
                "twods": raw_dir + '3v_cpi/2DS/' + project.upper() + '_' + flight.upper() + '/',
                "oap": raw_dir + '3v_cpi/oapfiles/',
                "cpi": raw_dir + '3v_cpi/CPI/' + project.upper() + '_' + flight.upper() + '/',
                }
    

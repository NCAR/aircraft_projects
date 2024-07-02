##Functions that help initiate push_data
from collections import OrderedDict
from email.mime.text import MIMEText
import smtplib
import sys, os
import _logging
import logging
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import  ICARTT, IWG1, HRT, SRT, PMS2D, threeVCPI

myLogger = _logging.MyLogger()
class Setup:
    """
    The Setup class is designed to initialize and prepare the push_data environment for processing and handling within a project. 
    It performs a series of steps to ensure that the project's directory structure, file naming conventions, and initial 
    status tracking are correctly established.

    Attributes:
        myLogger (MyLogger): An instance of the MyLogger class for logging purposes.
        PROJECT (str): The project name, read from the environment variable 'PROJECT'.
        DATA_DIR (str): The directory path for processed data, constructed using the 'DATA_DIR' environment variable.
        RAW_DIR (str): The directory path for raw data, constructed using the 'RAW_DATA_DIR' environment variable.
        PROJDIR (str): The project directory, read from the environment variable 'PROJ_DIR'.
        AIRCRAFT (str): The aircraft name, read from the environment variable 'AIRCRAFT'.
        PROJ_DIR (str): The full project directory path, combining 'PROJDIR', 'PROJECT', and 'AIRCRAFT'.
        FILENAME (dict): A dictionary to hold file names.
        STATUS (dict): A dictionary to track the processing, shipping, and storage status of various data types.

    Methods:
        __init__(self):
            Initializes the Setup class by setting up the logging, reading environment variables, creating necessary 
            directories and file extensions, reading flight and email information, setting up email, and initializing 
            the final message and status.
            
        init_logger(self):
            Initializes the logger with a file handler for logging messages to a file to 
            be used for debugging and error tracking in the push_data module.
        
        setup_email(self, data_dir, email):
            Sets up the email message  for sending results.
        
        read_env(self, env_var):
            Reads and returns the value of an environment variable.
        readFlight(self):
            Reads the user input to determine the flight designation.
        readEmail(self):    
            Reads the user input to determine the email address for sending results.
        
        ###The following methods are used to set up the initial constants for push_data processing###
        ###
        initializeFinalMessage(self, flight, project):
            Prepares the initial message to be sent to the user's email address with the project and flight information.
        
        createFileType(self):
            Initializes the FILE_TYPE attribute with the NetCDF filename rate indicator for different file types.

        create_status(self):
            Initializes the STATUS attribute with a predefined structure to track the status of different data types 
            (e.g., ADS, LRT, KML) in terms of processing, shipping, and storage.

        create_config_ext(self):
            Initializes the CONFIG_EXT attribute with the nimbus config filename extensions for different file types.
        
        createRate(self):
            Initializes the RATE attribute with the nimbus processing rates for different file types.
        
        createFileExt(self, HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI):
            Initializes the FILE_EXT attribute with several boolean parameters that determine which file types should be included. 
            It creates an ordered dictionary where the keys are the file types and the values are the corresponding file extensions. 
            The method checks the boolean parameters and adds the file types with their extensions to the dictionary if the corresponding parameter is True. 
            Finally, it returns the created dictionary.
        
        createFilePrefix(self, project, flight):
            Creates the FILE_PREFIX attribute with the project- and flight-specific filename prefix.
            
        createInstDir(self, raw_dir, data_dir, project, flight):
            Initializes the INST_DIR attribute with the instrument-specific data directories for different file types.
        
        check_aircraft(self, aircraft, project, raw_dir):
            Checks the aircraft variable and sets up the aircraft-specific processing environment based on the aircraft name and project information.
        
        ###The following methods are not used during initialization but are part of the Setup class###
        ###
        report(self, status, project, flight, email, file_ext, final_message):
            Generates a report of the shipping status for different file types and sends it to the user's email address.

    Note:
        This class relies on several environment variables ('PROJECT', 'DATA_DIR', 'RAW_DATA_DIR', 'PROJ_DIR', 'AIRCRAFT') 
        being set prior to instantiation. It also utilizes the external class MyLogger from _logger.
    """
    
    def __init__(self):
        self.init_logger()
        self.myLogger = myLogger
        self.PROJECT = self.read_env('PROJECT')
        self.DATA_DIR = f"{self.read_env('DATA_DIR')}/{self.PROJECT.upper()}/"
        self.RAW_DIR = f"{self.read_env('RAW_DATA_DIR')}/{self.PROJECT.upper()}/"
        self.PROJDIR = self.read_env('PROJ_DIR')
        self.AIRCRAFT = self.read_env('AIRCRAFT')
        self.PROJ_DIR = f'{self.PROJDIR}/{self.PROJECT}/{self.AIRCRAFT}/'
        
        self.create_status()
        self.createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)
        self.readFlight()
        self.readEmail()
        self.createInstDir(self.RAW_DIR, self.DATA_DIR, self.PROJECT, self.FLIGHT)
        self.createRate()
        self.createConfigExt()
        self.FILENAME = {}
        self.createFilePrefix(self.PROJECT, self.FLIGHT)
        self.createFileType()
        self.initializeFinalMessage(self.FLIGHT,self.PROJECT) 
        
        self.setup_email(self.DATA_DIR, self.EMAIL)
        self.check_aircraft(self.AIRCRAFT, self.PROJECT, self.RAW_DIR)

    def init_logger(self):
        '''Initialize the logger for logging messages.
                This method sets up a logger named 'myLogger' with the logging level set to DEBUG.
                It adds a FileHandler to log messages to the file '/tmp/push_data.log'.
                The log messages are formatted with the timestamp, filename, line number, function name,
                log level, and the actual log message.
        '''
        logger = logging.getLogger('myLogger')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('/tmp/push_data.log')
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler) 
        
    def create_status(self):
        ''' Creates the initial status dictionary with default values for each key.
            The status dictionary is used to track the processing, shipping, and storage status of different data types
        '''   
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
            
    def initializeFinalMessage(self, flight, project):
        '''
        Prepare for final message information to be sent to the user email
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
            
    def createInstDir(self, raw_dir, data_dir, project, flight):
        '''
        These are directories where instrument-specific data files (not
        RAF standard data) can be found.
        '''
        self.INST_DIR = {
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
        
    def createFilePrefix(self, project, flight):
        '''Create the project- and flight-specific filename prefix (e.g. WECANrf01)'''
        self.FILE_PREFIX= project + flight

    def createFileExt(self, HRT: bool, SRT: bool, ICARTT: bool, IWG1: bool, PMS2D: bool, threeVCPI: bool):
        '''Create an ordered dictionary containing the file extensions by
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
        '''nimbus processing rates (for use in config files) '''
        self.RATE = {
            "LRT": "1",
            "HRT": "25",
            "SRT": "0",
            }

    def createConfigExt(self):
        ''' nimbus config filename extensions'''
        self.CONFIG_EXT = {"LRT": "", "HRT": "h", "SRT": "s", }

    def check_aircraft(self, aircraft, project, raw_dir):
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
        ''' Read user input to determine the flight'''
        self.FLIGHT = input('Input flight designation (e.g. tf01):')

    def readEmail(self):
        '''Read user input to determine the email address'''
        self.EMAIL = input('Input email address to send results:')

    def read_env(self, env_var):
        '''Read environment variables and return error if not set'''
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

    

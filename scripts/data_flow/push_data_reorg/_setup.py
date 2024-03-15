##Functions that help initiate push_data
from _repetition import log_and_print
def getProject(self):
    return(self.read_env('PROJECT'))

def getDataDir(self):
    return(self.read_env('DATA_DIR'))

def getRawDir(self):
    return(self.read_env('RAW_DATA_DIR'))

def getProjDir(self):
    return(self.read_env('PROJ_DIR'))

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
        log_and_print(message)
        sys.exit(1)
    message = f"Processing {project} from {aircraft}.\nIf incorrect, edit ~/ads3_environment.\n Expecting to find .ads files in {raw_dir}."
    log_and_print(message)  
    return raircraft

def setup_email(self, data_dir, email):
        """
        Set up email
        """
        emailfilename = 'email.addr.txt'
        emailfile = data_dir+emailfilename
        command = 'rm '+emailfile
        os.system(command)
        fo = open(emailfile, 'w+')
        fo.write(email+'\n')
        fo.close()


##Maybe this will go in separate zip folder
def setup_zip(self, file_ext, data_dir, filename, inst_dir):
    """
    ZIP up the files as per expectations back home
    this only affects non-ads files
    """
    for key in file_ext:
        if (key == "ADS"):
            message = "Raw .ads file found but not zipping, if zip_ads is set, will bzip .ads file next."
            self.logger.info(message)
            print(message)
        elif (key == "PMS2D"):
            message = "Raw .2d file found but not zipping."
            self.logger.info(message)
            print(message)
        else:
            data_dir, file_name = os.path.split(filename[key])
            message = key + " filename = " + file_name
            self.logger.info(message)
            print(message)
            message = "data_dir = " + data_dir
            self.logger.info(message)
            print(message)
            self.zip_file(file_name, inst_dir[key])
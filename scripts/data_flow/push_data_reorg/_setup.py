##Functions that help initiate push_data
from scripts.data_flow.push_data_reorg._logging import log_and_print
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

def readFlight(self):
    '''
    Read user input to determine the event
    '''
    self.flight = input('Input flight designation (e.g. tf01):')
    return self.flight

def readEmail(self):
    '''
    Read user input to determine the email address
    '''
    self.email = input('Input email address to send results:')
    return(self.email)

def read_env(self, env_var):
    '''
    Read and set environment var
    '''
    try:
        return os.environ[env_var]
    except KeyError:
        log_and_print(f'Please set the environment variable {env_var}')
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
def setup_zip(self, file_ext, data_dir, filename, inst_dir):
    """
    ZIP up the files as per expectations back home
    this only affects non-ads files
    """
    for key in file_ext:
        if key == "ADS":
            log_and_print("Raw .ads file found but not zipping, if zip_ads is set, will bzip .ads file next.")
        elif key == "PMS2D":
            log_and_print("Raw .2d file found but not zipping.")
        else:
            data_dir, file_name = os.path.split(filename[key])
            message = f"{key} filename = {file_name}"
            log_and_print(message)
            message = f"data_dir = {data_dir}"
            log_and_print(message)
            self.zip_file(file_name, inst_dir[key])
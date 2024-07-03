#! /usr/bin/env python3

###############################################################################
# Script monitors ingest directories for newly written files and then syncs
# the file to the appropriate directory based on the file type.
#
# This script runs from cron on eol-rosetta as user ads.
# The crontab expects the script to be in /net/jlocal/projects/scripts.
#
###############################################################################

import logging
import logging.handlers
import argparse
import os
import sys
import smtplib
from email.mime.text import MIMEText

# set up variables
# Have to get PROJ_DIR, project and aircraft from env here even though will
# get them again when import fieldProc_setup, because need them to find
# location of fieldPro_setup.
project = os.environ['PROJECT']
aircraft = os.environ['AIRCRAFT']
PROJ_DIR = os.environ['PROJ_DIR']
full_proj_dir = PROJ_DIR + '/' + project + '/' + aircraft+'/'
sys.path.insert(0, full_proj_dir + 'scripts/')
sys.path.insert(0, full_proj_dir)
from fieldProc_setup import project, PROJ_DIR, aircraft, dat_parent_dir,\
    ftp_parent_dir, rdat_parent_dir, FTP, PMS2D, HRT, SRT, IWG1, ICARTT, NAS,\
    ship_ADS, GDRIVE, RAW_DATA_DIR
temp_dir = RAW_DATA_DIR + '/' + project + '/field_sync/'
dat_dir = dat_parent_dir + project
ftp_dir = ftp_parent_dir
rdat_dir = rdat_parent_dir + project
eol_dir = temp_dir+'/EOL_data/'

proc_dict = {'LRT': True, 'KML': True, 'HRT': HRT, 'SRT': SRT, \
            'IWG1':IWG1,'ICARTT': ICARTT,'PMS2D':PMS2D,'ADS':ship_ADS} ##Dictionary to indicate which datatypes are used in the project

def _run_and_log(command, message):   
    '''Helper function to run a command and log the message alongside it.'''
    os.system(command)
    logging.info(f'{message}: {command}')

def create_directory(dir_path):
    """
    Helper function to create a directory and handle errors.
    """
    if dir_path is tuple:
        if os.path.isdir(dir_path[0]):
            rdat_dir = dir_path[0]
            return
        elif os.path.isdir(dir_path[1]):
            rdat_dir = dir_path[1]
            return
    try:
        if not os.path.isdir(dir_path):
            logging.info(f'Directory {dir_path} does not exist. Creating...')
            os.makedirs(dir_path, exist_ok=True)
    except Exception as e:
        logging.error(f'Could not make directory {dir_path}: {e} \nBailing out')
        send_mail_and_die(f'Could not make directory {dir_path}: {e}')

def dir_check():
    """
    Function to ensure that directories exist
    make them if not
    """
    # Check to make sure the rdat + project dir exists
    rdat_dir = rdat_parent_dir + project
    ftp_dir = ftp_parent_dir
    directories = [
        rdat_dir,
        ftp_dir,
        (dat_parent_dir + project,dat_parent_dir + project.lower())
    ]
    if FTP and PMS2D:
        directories.append(rdat_dir+ '/PMS2D')
    for dir_path in directories:
        create_directory(dir_path)

def unzip():
    """
    Unzip if you have any of those pesky .zip files
    """
    logging.info('Unzipping files if they are present')
    for fname in os.listdir(eol_dir + 'RAF_data/'):

        if fname.endswith('.zip'):
            command = f'unzip -qq -o {eol_dir}RAF_data/{fname} -d {eol_dir}RAF_data'
            message= f'Unzipping files: '
            _run_and_log(command, message)

            command = f"mv {eol_dir}RAF_data/{fname} {dat_dir}/field_data"
            message= 'Moving files to dat_dir, so we dont keep unzipping'
            _run_and_log(command, message)

def _sync_data(src_dir, file_pattern, dest_dirs, base_message, recursive:bool=False):
    """
    Sync files matching pattern from src_dir to each destination in dest_dirs.
    """
    command_base = f'rsync -rqu {src_dir}/{file_pattern} ' if recursive else f'rsync -qu {src_dir}/{file_pattern} '
    for dest_dir in dest_dirs:
        command = command_base + dest_dir
        _run_and_log(command, base_message)  

def dist_raw():
    """
    Function to distribute RAF raw data from ingest to FTP plus others
    """
    logging.info('Starting distribution of RAF raw data')

    # Check the /ADS subdir for files

    if any(fname.endswith('.ads') for fname in os.listdir(eol_dir + 'RAF_data/ADS')):
        _sync_data(eol_dir + 'RAF_data/ADS', '*.ads', [rdat_dir], 'Syncing ADS files to rdat')
        # push_data.py can generate a .bz2 file, so must accommodate
    if any(fname.endswith('.bz2') for fname in os.listdir(eol_dir + 'RAF_data/ADS')):
        _sync_data(eol_dir + 'RAF_data/ADS', '*.bz2', [rdat_dir], 'Syncing zipped ADS files to rdat')

    # Check the PMS2D subdir for files
    _sync_data(eol_dir + 'RAF_data/PMS2D', '*', [rdat_dir,f'{ftp_dir}/EOL_data/RAF_data'], 'Syncing PMS2D files', recursive=True)

def dist_prod():
    """
    Function to distribute RAF prod data from ingest point to FTP plus others.
    """
    logging.info('Starting distribution of RAF prod data\n')
    data_types = [
        ('LRT', '*.nc'),
        ('HRT', '*.nc'),
        ('SRT', '*.nc'),
        ('KML', '*.kml'),
        ('ICARTT', '*.ict'),
        ('IWG1', '*.iwg')
    ]
    for data_type, file_pattern in data_types:
        src_dir = f'{eol_dir}RAF_data/{data_type}'
        dest_dirs = [
            f'{dat_dir}/field_data',
            f'{ftp_dir}/EOL_data/RAF_data/{data_type}'
        ]
        _sync_data(src_dir, file_pattern, dest_dirs, 'Syncing production data')

def distribute_data(data_type: list):
    """
    Distributes data based on the specified data types.

    Args:
        data_type (list): A list of data types to distribute.
    Returns:
        None
    """
    destinations = {
        ''' data_type: (destination, ext, source_dir, log_message, recursive)'''
        
        'PI': (f'{ftp_dir}/EOL_data', '*', 'PI_data', 'Starting distribution of PI data\n', True),
        'MTP': (f'{rdat_dir}/MTP/field','*','/RAF_data/MTP', 'Starting distribution of MTP data\n', True),
        'QAtools': ('/net/www/raf/', '*','/RAF_data/QAtools','Starting distribution of QAtools.html', True),
        'field_data': (dat_dir, '*.nc',f'{dat_dir}/field_data', 'Continuing distribution of RAF prod data', False)
    }
    for dtype in data_type:
        if dtype not in destinations:
            logging.error(f'Unknown data type: {dtype}')
            return
        destination, ext, source_dir, log_message, recursive = destinations[dtype]
        logging.info(log_message)
        _sync_data(source_dir, ext, [destination], f'Syncing {dtype} data into place',recursive)

def ingest_to_local(filetype, local_dir, start_dir):
    """
    Function to distribute data from FTP to local dirs for QAQC and backup
    to be used if no NAS in the field and data goes from Ground Station to
    FTP site directly.
    """
    logging.info('Starting distribution of data from FTP to localdirs/')
    if filetype == 'PMS2D':
        local_dir = rdat_dir
        command = 'rsync -qu ' + start_dir + '/EOL_data/RAF_data/' + filetype \
            + '/* ' + local_dir + '/' + filetype + '/.'
    elif filetype == 'ADS':
        local_dir = rdat_dir
        command = 'rsync -qu ' + start_dir + '/EOL_data/RAF_data/' + filetype \
            + '/* ' + local_dir + '/.'
    else:
        command = 'rsync -qu ' + start_dir + '/EOL_data/RAF_data/' + filetype \
            + '/* ' + local_dir
    message = 'Syncing dir into place'
    _run_and_log(command, message)


def send_mail_and_die(body):
    """
    Email function
    """
    email = 'rafsehelp@ucar.edu'
    logging.info("About to send e-mail to: " + email)
    msg = MIMEText(body)
    msg['Subject'] = 'Receive and Distribute message for:' + project
    msg['From'] = 'ads@groundstation'
    msg['To'] = email

    s = smtplib.SMTP('localhost')
    s.sendmail("ads@groundstation", email, msg.as_string())
    logging.info("Message:\n" + msg.as_string())
    s.quit()

    exit(1)
    

def sync_from_nas():
    """
    Syncs data from NAS.

    This function performs the following steps:
    1. Logs an info message indicating the start of the sync process.
    2. Calls the `dir_check` function to check the directory.
    3. Calls the `dist_raw` function to distribute raw data.
    4. Calls the `dist_prod` function to distribute production data.
    5. Calls the `distribute_data` function with the arguments ['field_data', 'MTP'].
    """
    logging.info("Syncing from NAS...\n")
    dir_check()
    dist_raw()
    dist_prod()
    distribute_data(['field_data','MTP'])
    
def sync_from_gdrive():
    logging.info("Syncing from GDRIVE...")
    for dtype in proc_dict:
        if proc_dict[dtype]:
            ingest_to_local(dtype, f'{dat_dir}/field_data', temp_dir)
    distribute_data(['field_data','QAtools'])
    
def sync_from_ftp():
    logging.info("Syncing from FTP...\n")
    dir_check()
    logging.info(f'Syncing ADS and PMS2D data from {ftp_dir} to {rdat_dir}\n')
    logging.info(f'Syncing other data from {ftp_dir} to {dat_dir}/field_data')
    for dtype in proc_dict:
        if proc_dict[dtype]:
            ingest_to_local(dtype, f'{dat_dir}/field_data', ftp_dir)
    distribute_data(['field_data'])

def parse_args():
    """ Instantiate a command line argument parser """

    # Define command line arguments which can be provided
    parser = argparse.ArgumentParser(
        description="Script to monitor ingest directories for newly written " +
        "files and sync them to the appropriate directory based on file type.")
    parser.add_argument(
        '--logfile', type=str, required=False, default=False,
        help="Optional file to save logs to (defaults to writing to screen)")
    args = parser.parse_args()

    return args


def main():
    """
    Define main function
    """
    if NAS:
        sync_from_nas()
    elif GDRIVE:
        sync_from_gdrive()
    elif FTP:
        sync_from_ftp()
    else:
        logging.error("No valid source specified for syncing.")
        exit(1)


if __name__ == '__main__':

    args = parse_args()

    # Set up logging
    logger = logging.getLogger()
    # If a logfile name is specified on the command line, set up log rotation
    if args.logfile:
        handler = logging.handlers.RotatingFileHandler(
            args.logfile, maxBytes=1000000, backupCount=9)
    else:
        handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    main()

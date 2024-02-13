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
rdat_dir = rdat_parent_dir + project+'/'
eol_dir = temp_dir+'/EOL_data/'


def dir_check():
    """
    Function to ensure that directories exist
    make them if not
    """
    # Check to make sure the rdat + project dir exists
    rdat_dir = rdat_parent_dir + project
    if not os.path.isdir(rdat_dir):
        try:
            message = 'Directory ' + rdat_dir + 'does not exist. Creating...'
            logging.info(message)
            os.mkdir(rdat_dir)
        except Exception as e:
            message = 'Could not make raw directory ' + rdat_dir + ': ' + e
            logging.error(message)
            logging.error('Bailing out')
            send_mail_and_die(message)
            exit(1)
    # ... and for FTP if there is PMS2D data that PMS2D exists under project
    if FTP is True and PMS2D is True:
        if not os.path.isdir(rdat_dir + '/PMS2D'):
            try:
                message = 'Directory ' + rdat_dir + \
                    '/PMS2D does not exist. Creating...'
                logging.info(message)
                os.mkdir(rdat_dir + '/PMS2D')
            except Exception as e:
                message = 'Could not make raw directory ' + rdat_dir + \
                    '/PMS2D: ' + e
                logging.error(message)
                logging.error('Bailing out')
                send_mail_and_die(message)
                exit(1)

    # Check to make sure the incoming ftp + project dir exists
    ftp_dir = ftp_parent_dir
    if not os.path.isdir(ftp_dir):
        try:
            message = 'Directory ' + ftp_dir + 'does not exist. Creating...'
            logging.info(message)
            os.mkdir(ftp_dir)
        except Exception as e:
            message = 'Could not make ftp directory ' + ftp_dir + ': ' + e
            logging.error(message)
            logging.error('Bailing out')
            send_mail_and_die(message)
            exit(1)

    # Check to make sure dat + project dir exists
    #   check for upper case project
    if os.path.isdir(dat_parent_dir + project):
        dat_dir = dat_parent_dir + project

    #   check for lower case project
    elif os.path.isdir(dat_parent_dir + project.lower()):
        dat_dir = dat_parent_dir + project.lower()
    #   neither exists, so create
    else:
        dat_dir = dat_parent_dir + project
        try:
            message = 'Directory ' + dat_dir + 'does not exist. Creating...'
            logging.info(message)
            os.mkdir(dat_dir)
        except Exception as e:
            message = 'Could not make product directory ' + dat_dir + ': ' + e
            logging.error(message)
            logging.error('Bailing out')
            send_mail_and_die(message)
            exit(1)


def unzip():
    """
    Unzip if you have any of those pesky .zip files
    """
    final_message = 'Unzipping files if they are present\n'
    for fname in os.listdir(eol_dir + 'RAF_data/'):

        if fname.endswith('.zip'):
            command = 'unzip -qq -o ' + eol_dir + 'RAF_data/' + fname + \
                ' -d ' + eol_dir + 'RAF_data'
            message = 'Unzipping files:' + command + '\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

            command = 'mv ' + eol_dir + 'RAF_data/' + fname + ' ' + dat_dir \
                + '/field_data'
            message = 'Moving files to dat_dir, so we dont keep unzipping'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        else:
            pass


def dist_raw():
    """
    Function to distribute RAF raw data from ingest to FTP plus others
    """
    final_message = 'Starting distribution of RAF raw data\n'

    # Check the /ADS subdir for files
    for fname in os.listdir(eol_dir + 'RAF_data/ADS'):

        if fname.endswith('.ads'):
            command = 'rsync -qu ' + eol_dir + 'RAF_data/ADS/*.ads ' + rdat_dir
            message = 'Syncing ADS files to rdat: ' + command + '\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)
        # push_data.py can generate a .bz2 file, so must accommodate
        elif fname.endswith('.bz2'):
            command = 'rsync -qu ' + eol_dir + 'RAF_data/ADS/*.bz2 ' + rdat_dir
            message = 'Syncing zipped ADS files to rdat: ' + command + '\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        else:
            pass

    # Check the PMS2D subdir for files
    command = 'rsync -rqu ' + eol_dir + 'RAF_data/PMS2D ' + rdat_dir
    message = 'Syncing PMS2D dir to rdat: ' + command + '\n'
    os.system(command)
    final_message = final_message + message

    command = 'rsync -rqu ' + eol_dir + 'RAF_data/PMS2D ' + ftp_dir + \
        '/EOL_data/RAF_data'
    message = 'Syncing PMS2D dir to incoming FTP: ' + command + '\n'
    os.system(command)

    final_message = final_message + message
    logging.info(final_message)


def dist_prod():
    """
    Function to distribute RAF prod data from ingest point to FTP plus others
    """
    final_message = 'Starting distribution of RAF prod data\n'
    # Check for the production file
    for fname in os.listdir(eol_dir + 'RAF_data/LRT'):
        command = 'rsync -qu ' + eol_dir + 'RAF_data/LRT/*.nc ' + dat_dir + \
            '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'RAF_data/LRT/*.nc ' + ftp_dir + \
            '/EOL_data/RAF_data/LRT'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
    for fname in os.listdir(eol_dir + 'RAF_data/HRT'):
        command = 'rsync -qu ' + eol_dir + 'RAF_data/HRT/*.nc ' + dat_dir + \
            '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'RAF_data/HRT/*.nc ' + ftp_dir + \
            '/EOL_data/RAF_data/HRT'
        message = 'Syncing production data to ftp: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
    for fname in os.listdir(eol_dir + 'RAF_data/SRT'):
        command = 'rsync -qu ' + eol_dir + 'RAF_data/SRT/*.nc ' + dat_dir + \
            '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'RAF_data/SRT/*.nc ' + ftp_dir + \
            '/EOL_data/RAF_data/SRT'
        message = 'Syncing production data to ftp: ' + command+'\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
    for fname in os.listdir(eol_dir + 'RAF_data/KML'):
        command = 'rsync -qu ' + eol_dir + 'RAF_data/KML/*.kml ' + dat_dir + \
            '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'RAF_data/KML/*.kml ' + ftp_dir + \
            '/EOL_data/RAF_data/KML'
        message = 'Syncing production data to ftp: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
    for fname in os.listdir(eol_dir + 'RAF_data/ICARTT'):
        command = 'rsync -qu ' + eol_dir + 'RAF_data/ICARTT/*.ict ' + \
            dat_dir + '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'RAF_data/ICARTT/*.ict ' + \
            ftp_dir + '/EOL_data/RAF_data/ICARTT'
        message = 'Syncing production data to ftp: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
    for fname in os.listdir(eol_dir + 'RAF_data/IWG1'):
        command = 'rsync -qu ' + eol_dir + 'RAF_data/IWG1/*.iwg ' + \
            dat_dir + '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'RAF_data/IWG1/*.iwg ' + \
            ftp_dir + '/EOL_data/RAF_data/IWG1'
        message = 'Syncing production data to ftp: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
    for fname in os.listdir(eol_dir + 'AVAPS_data/acsfiles'):
        command = 'rsync -qu ' + eol_dir + 'AVAPS_data/acsfiles/*.nc ' + \
            dat_dir + '/field_data'
        message = 'Syncing production data: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)
        command = 'rsync -qu ' + eol_dir + 'AVAPS_data/acsfiles/*.nc ' + \
            ftp_dir + '/EOL_data/AVAPS_data/acsfiles'
        message = 'Syncing production data to ftp: ' + command + '\n'
        os.system(command)
        final_message = final_message + message
        logging.info(final_message)


def dist_field():
    """
    Function to rsync .nc files up a dir for ingest by QAtools in Boulder
    and for reprocessing by software group internally. Leave the /field data
    directory as a copy of the incoming ftp and NAS in the field.
    """
    final_message = 'Continuing distribution of RAF prod data\n'

    for fname in os.listdir(dat_dir + '/field_data'):

        if fname.endswith('.nc'):
            command = 'rsync -qu ' + dat_dir + '/field_data/*.nc ' + dat_dir
            message = 'Syncing production data into place: ' + command + '\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        else:
            pass


def dist_PI(directory):
    """
    Function to distribute PI data from ingest to FTP
    """
    final_message = 'Starting distribution of PI data\n'

    # Rsync anything and everything in the assigned dir
    command = 'rsync -rqu ' + temp_dir+'/' + directory+' ' + ftp_dir
    message = 'Syncing dir into place: ' + command+'\n'
    os.system(command)

    final_message = final_message + message
    logging.info(final_message)


def dist_recursive(directory):

    final_message = 'Starting distribution of PI data\n'

    # Rsync anything and everything in the assigned dir
    command = 'rsync -rqu ' + eol_dir + directory+' ' + ftp_dir+'/EOL_data'
    message = 'Syncing dir into place: ' + command+'\n'
    os.system(command)

    final_message = final_message + message
    logging.info(final_message)


def dist_recursive_MTP(directory):

    final_message = 'Starting distribution of MTP data\n'

    # Rsync anything and everything in the MTP dir
    command = 'rsync -rqu ' + eol_dir + directory + ' ' + rdat_dir + \
        '/MTP/field'
    message = 'Syncing MTP dir into place: ' + command + '\n'
    os.system(command)

    final_message = final_message + message
    logging.info(final_message)


def dist_recursive_QAtools(directory):
    final_message = 'Starting distribution of QAtools.html\n'

    # Rsync anything and everything in the MTP dir
    command = 'rsync -rqu ' + eol_dir + directory + ' /net/www/raf/'
    message = 'Syncing QAtools dir into place: ' + command + '\n'
    os.system(command)
    final_message = final_message + message
    logging.info(final_message)


def ingest_to_local(filetype, local_dir, start_dir):
    """
    Function to distribute data from FTP to local dirs for QAQC and backup
    to be used if no NAS in the field and data goes from Ground Station to
    FTP site directly.
    """
    final_message = 'Starting distribution of data from FTP to localdirs/\n'

    if filetype == 'PMS2D':
        command = 'rsync -qu ' + start_dir + '/EOL_data/RAF_data/' + filetype \
            + '/* ' + local_dir + '/' + filetype + '/.'
        message = 'Syncing dir into place: ' + command + '\n'
        os.system(command)

        final_message = final_message + message
        logging.info(final_message)

    elif filetype == 'ADS':
        command = 'rsync -qu ' + start_dir + '/EOL_data/RAF_data/' + filetype \
            + '/* ' + local_dir + '/.'
        message = 'Syncing dir into place: ' + command + '\n'
        os.system(command)

        final_message = final_message + message
        logging.info(final_message)

    else:
        command = 'rsync -qu ' + start_dir + '/EOL_data/RAF_data/' + filetype \
            + '/* ' + local_dir
        message = 'Syncing dir into place: ' + command + '\n'
        os.system(command)

        final_message = final_message + message
        logging.info(final_message)


def send_mail_and_die(body):
    """
    Email function
    """
    email = 'rafsehelp@ucar.edu'
    logging.info("About to send e-mail to: " + email)
    msg = MIMEText(body)
    msg['Subject'] = 'Receive and Distribute message for:' + project + \
        ' flight:' + flight
    msg['From'] = 'ads@groundstation'
    msg['To'] = email

    s = smtplib.SMTP('localhost')
    s.sendmail("ads@groundstation", email, msg.as_string())
    logging.info("Message:\n" + msg.as_string())
    s.quit()

    exit(1)


def main():
    """
    Define main function
    """
    if NAS is True:
        logging.info("Syncing from NAS...\n")
        dir_check()
        dist_raw()
        dist_prod()
        dist_field()
        dist_recursive_MTP('/RAF_data/MTP')
    elif NAS is False and GDRIVE is True:
        logging.info("Syncing from GDRIVE...\n")
        # dist_PI('PI_data')
        ingest_to_local('LRT', dat_dir + '/field_data', temp_dir)
        ingest_to_local('KML', dat_dir + '/field_data', temp_dir)
        if ship_ADS:
            ingest_to_local('ADS', rdat_dir, temp_dir)
        if PMS2D:
            ingest_to_local('PMS2D', rdat_dir, temp_dir)
        if HRT:
            ingest_to_local('HRT', dat_dir + '/field_data', temp_dir)
        if SRT:
            ingest_to_local('SRT', dat_dir + '/field_data', temp_dir)
        if IWG1:
            ingest_to_local('IWG1', dat_dir + '/field_data', temp_dir)
        if ICARTT:
            ingest_to_local('ICARTT', dat_dir + '/field_data', temp_dir)
        dist_field()
        dist_recursive_QAtools('/RAF_data/QAtools')

    elif NAS is False and FTP is True:
        logging.info("Syncing from FTP...\n")
        dir_check()
        # dist_PI('PI_data')
        logging.info('Syncing ADS and PMS2D data from ' + ftp_dir + ' to ' +
                     rdat_dir + '\n')
        if ship_ADS:
            ingest_to_local('ADS', rdat_dir, ftp_dir)
        if PMS2D:
            ingest_to_local('PMS2D', rdat_dir, ftp_dir)

        logging.info('Syncing from ' + ftp_dir + ' to ' + dat_dir +
                     '/field_data')
        ingest_to_local('LRT', dat_dir + '/field_data', ftp_dir)
        ingest_to_local('KML', dat_dir + '/field_data', ftp_dir)
        if HRT:
            ingest_to_local('HRT', dat_dir + '/field_data', ftp_dir)
        if SRT:
            ingest_to_local('SRT', dat_dir + '/field_data', ftp_dir)
        if IWG1:
            ingest_to_local('IWG1', dat_dir + '/field_data', ftp_dir)
        if ICARTT:
            ingest_to_local('ICARTT', dat_dir + '/field_data', ftp_dir)

        dist_field()
    exit(1)


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

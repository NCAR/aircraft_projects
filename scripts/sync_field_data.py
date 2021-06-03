#! /usr/bin/env python

#############################################################################
# Script monitors ingest directories for newly written files and then syncs
# the file to the appropriate directory based on the file type.
#
# Runs from cron on tikal as user ads. 
#
# Script should be in /h/eol/ads/crontab
#############################################################################

import logging, logging.handlers
import os, sys, re, sys
import time
import smtplib
from email.mime.text import MIMEText

# Get the arguments from the command line
temp_dir = sys.argv[1]
project = sys.argv[2]
aircraft = sys.argv[3] 

# Set up directories
proj_dir = os.getenv("PROJ_DIR")+'/'+project+'/'+aircraft+'/'
sys.path.insert(0,proj_dir)
from fieldProc_setup import *

dat_dir = dat_parent_dir+project
ftp_dir = ftp_parent_dir
rdat_dir = rdat_parent_dir+project
eol_dir = temp_dir+'/EOL_data/'

#############################################################################
# Directory checks
#############################################################################
def dir_check():

    # Check to make sure the rdat + project dir exists
    rdat_dir = rdat_parent_dir+project
    if not os.path.isdir(rdat_dir):
        try:
            os.mkdir(rdat_dir)
        except:
            message = 'Could not make raw directory:'+rdat_dir
            logging.error(message)
            logging.error('Bailing out')
            # send_mail_and_die(final_message + message)
            exit(1)

    # Check to make sure the incoming ftp + project dir exists
    ftp_dir = ftp_parent_dir
    if not os.path.isdir(ftp_dir):
        try:
            os.mkdir(ftp_dir)
        except:
            message = 'Could not make ftp directory:'+ftp_dir
            logging.error(message)
            logging.error('Bailing out')
            send_mail_and_die(final_message + message)
            exit(1)

    if os.path.isdir(dat_parent_dir+project):
        dat_dir = dat_parent_dir+project

    elif os.path.isdir(dat_parent_dir+project.lower()):
        dat_dir = dat_parent_dir+project.lower()

    else:
        dat_dir = dat_parent_dir+project
        try:
            os.mkdir(dat_dir)
        except:
            logging.error('Could not make product directory:'+dat_dir)
            logging.error('Bailing out')
            send_mail_and_die(final_message+ ' Could not make product directory:'+dat_dir)

#############################################################################
# Unzip if you have any of those pesky .zip files
#############################################################################
def unzip():

    final_message = 'Unzipping files if they are present\n'
    for fname in os.listdir(eol_dir+'RAF_data/'):

        if fname.endswith('.zip'):
            command = 'unzip -qq -o '+eol_dir+'RAF_data/'+fname+' -d '+eol_dir+'RAF_data'
            message = 'Unzipping files:'+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)
 
            command = 'mv '+eol_dir+'RAF_data/'+fname+' '+dat_dir+'/field_data'
            message = 'Moving files to dat_dir, so we dont keep unzipping'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        else:
            pass

    return(final_message)

#############################################################################
# Function to distribute RAF raw data from ingest to FTP plus others
#############################################################################
def dist_raw():

    final_message = 'Starting distribution of RAF raw data\n'

    # Check the /ADS subdir for files
    for fname in os.listdir(eol_dir+'RAF_data/ADS'):
        
        if fname.endswith('.ads'):
            command = 'rsync -qu '+eol_dir+'RAF_data/ADS/*.ads '+rdat_dir
            message = 'Syncing ADS files to rdat: '+command+'\n'
            os.system(command)
            final_message = final_message + message 
            logging.info(final_message)

        # push_data.py can generate a .bz2 file, so must accommodate 
        elif fname.endswith('.bz2'):
            command = 'rsync -qu '+eol_dir+'RAF_data/ADS/*.bz2 '+rdat_dir
            message = 'Syncing zipped ADS files to rdat: '+command+'\n'
            os.system(command)
            final_message = final_message + message 
            logging.info(final_message)

        else:
            pass

    # Check the PMS2D subdir for files 
    command = 'rsync -rqu '+eol_dir+'RAF_data/PMS2D '+rdat_dir
    message = 'Syncing PMS2D dir to rdat: '+command+'\n'
    os.system(command)
    final_message = final_message + message 
    
    command = 'rsync -rqu '+eol_dir+'RAF_data/PMS2D '+ftp_dir+'/EOL_data/RAF_data'
    message = 'Syncing PMS2D dir to incoming FTP: '+command+'\n'        
    os.system(command)

    final_message = final_message + message
    logging.info(final_message)
    
    return(final_message)

#############################################################################
# Function to distribute RAF prod data from ingest point to FTP plus others
#############################################################################
def dist_prod():

    final_message = 'Starting distribution of RAF prod data\n' 
    # Check for the production file
    for fname in os.listdir(eol_dir+'RAF_data'):

        if fname.endswith('nc'):
            command = 'rsync -qu '+eol_dir+'RAF_data/*.nc '+dat_dir+'/field_data'
            message = 'Syncing production data: '+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)
       
            command = 'rsync -qu '+eol_dir+'RAF_data/*.nc '+ftp_dir+'/EOL_data/RAF_data'
            message = 'Syncing production data to ftp: '+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        elif fname.endswith('kml'):
            command = 'rsync -qu '+eol_dir+'RAF_data/*.kml '+dat_dir+'/field_data'
            message = 'Syncing production data: '+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

            command = 'rsync -qu '+eol_dir+'RAF_data/*.kml '+ftp_dir+'/EOL_data/RAF_data'
            message = 'Syncing production data to ftp: '+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        elif fname.endswith('.ict'):
            command = 'rsync -qu '+eol_dir+'RAF_data/*.ict '+dat_dir+'/field_data'
            message = 'Syncing production data: '+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

            command = 'rsync -qu '+eol_dir+'RAF_data/*.ict '+ftp_dir+'/EOL_data/RAF_data'
            message = 'Syncing production data to ftp: '+command+'\n'
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)
        else:
            pass
    
    return(final_message)

#############################################################################
# Function to rsync .nc files up a dir for ingest by QATools in Boulder
# and for reprocessing by software group internally. Leave the /field_data
# directory as a copy of the incoming ftp and the NAS in the field
#############################################################################
def dist_field():

    final_message = 'Continuing distribution of RAF prod data\n'

    for fname in os.listdir(dat_dir+'/field_data'):

        if fname.endswith('.nc'):
            command = 'rsync -qu '+dat_dir+'/field_data/*.nc '+dat_dir
            message = 'Syncing production data into place: '+command+'\n'       
            os.system(command)
            final_message = final_message + message
            logging.info(final_message)

        else:
            pass

    return(final_message)

#############################################################################
# Function to distribute PI data from ingest to FTP
#############################################################################
def dist_PI(directory):
    
    final_message = 'Starting distribution of PI data\n'
    
    # Rsync anything and everything in the assigned dir
    command = 'rsync -rqu '+temp_dir+'/'+directory+' '+ftp_dir
    message = 'Syncing dir into place: '+command+'\n'
    os.system(command)

    final_message = final_message + message
    logging.info(final_message) 
    return(final_message)

def dist_recursive(directory):

    final_message = 'Starting distribution of PI data\n'

    # Rsync anything and everything in the assigned dir
    command = 'rsync -rqu '+eol_dir+directory+' '+ftp_dir+'/EOL_data'
    message = 'Syncing dir into place: '+command+'\n'
    os.system(command)

    final_message = final_message + message
    logging.info(final_message)
    return(final_message)

#############################################################################
# Function to distribute data from FTP to local dirs for QAQC and backup
# to be used if no NAS in the field and data goes from Ground Station to 
# FTP site directly.
#############################################################################
def ftp_to_local(filetype, local_dir):
    final_message = 'Starting distribution of data from the FTP to localdirs/\n'

    if filetype == 'PMS2D':
        command = 'rsync -qu '+ftp_dir+'/EOL_data/RAF_data/'+filetype+'/* '+local_dir+'/'+filetype
        message = 'Syncing dir into place: '+command+'\n'
        os.system(command)

        final_message = final_message + message
        logging.info(final_message)

        return(final_message)

    elif filetype == 'ADS':
        command = 'rsync -qu '+ftp_dir+'/EOL_data/RAF_data/'+filetype+'/* '+local_dir
        message = 'Syncing dir into place: '+command+'\n'
        os.system(command)

    else:
        command = 'rsync -qu '+ftp_dir+'/EOL_data/RAF_data/'+filetype+'/* '+local_dir
        message = 'Syncing dir into place: '+command+'\n'
        os.system(command)

        final_message = final_message + message
        logging.info(final_message)

        return(final_message)

#############################################################################
# Email function
#############################################################################
def send_mail_and_die(body):

    emailfilename = 'email.addr.txt'
    os.chdir(cwd)
    fo = open(emailfilename, 'r+')
    email = fo.readline()
    fo.close()
    logging.info("About to send e-mail to: "+email)
    body = body + 'See /tmp/ads_data_catcher.log\n'
    msg = MIMEText(body)
    msg['Subject'] = 'Receive and Disribute message for:'+project
    msg['From'] = 'ads@groundstation'
    msg['To'] = email

    s = smtplib.SMTP('localhost')
    s.sendmail("ads@groundstation",email,msg.as_string())
    logging.info("Message:\n"+msg.as_string())
    s.quit()

    exit(1)

#############################################################################
# Define main function
#############################################################################
def main():
    if NAS == True:    
        dir_check()
        dist_raw()
        unzip()
        dist_prod()
        dist_field()
        dist_PI('PI_data')
        
        dist_recursive('HCR_data')
        dist_recursive('AVAPS_data')

    elif NAS == False and FTP == True:
        ftp_to_local('ADS', rdat_dir)
        ftp_to_local('PMS2D', rdat_dir)
        ftp_to_local('LRT', dat_dir+'/field_data')
        ftp_to_local('KML', dat_dir+'/field_data')
        dist_field()
    # send_mail_and_die(body)
    exit(1)

##############################################################################
# MAIN
##############################################################################
if __name__ == '__main__':

    try:
        # Set up logging
        logger = logging.getLogger()
        # If you want to revert to a log file uncomment
        #handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000, backupCount=9)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    except IndexError:

        # Usage statement
        print("\nUsage: %s path temp_dir logfile")
        print("path - path to script  ")
        print("(i.e. /h/eol/ads/crontab)")
        print("logfile - logfile name (i.e. /tmp/sync.log)")

    main()   

    exit(1)

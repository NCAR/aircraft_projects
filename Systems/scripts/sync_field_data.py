#!/usr/bin/env python

#############################################################################
# Script monitors ingest directories for newly written files and then syncs
# the file to the appropriate directory based on the file type.
#############################################################################
import logging, logging.handlers
import os, sys, re, sys
import time
import smtplib
from email.mime.text import MIMEText
#from fieldProc_setup import *

# Initialization
sys.path.insert(0,proj_dir)
from fieldProc_setup import *

dat_dir = dat_parent_dir+project
ftp_dir = ftp_parent_dir
rdat_dir = rdat_parent_dir+project

#############################################################################
# Directory checks
#############################################################################
def dir_check():

    rdat_dir = rdat_parent_dir + project
    if not os.path.isdir(rdat_dir):
        try:
            os.mkdir(rdat_dir)
        except:
            message = 'Could not make raw directory:'+rdat_dir
            logging.error(message)
            logging.error('Bailing out')
            send_mail_and_die(final_message + message)
            exit(1)

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
# Function to distribute RAF raw data
#############################################################################
def dist_raw():

    final_message = 'Starting distribution of RAF raw data\n'

    command = 'rsync -qu '+temp_dir+'/RAF_data/ADS/* '+rdat_dir
    message_ads = 'Syncing ADS dir into place: '+command+'\n'
    logging.info(message_ads)
    os.system(command)
    
    command = 'rsync -qu '+temp_dir+'/RAF_data/PMS2D/* '+rdat_dir+'/PMS2D'
    message_2draf = 'Syncing PMS2D dir to rdat: '+command+'\n'
    logging.info(message_2draf)
    os.system(command)

    command = 'rsync -qu '+temp_dir+'/RAF_data/PMS2D/* '+ftp_dir+'/RAF_data/PMS2D'
    message_ftp = 'Syncing PMS2D dir into place: '+command+'\n'        
    logging.info(message_ftp)
    os.system(command)

    final_message = final_message + message_ads + message_2draf + message_ftp

    return(final_message)

#############################################################################
# Function to distribute RAF prod data
#############################################################################
def dist_prod():

    final_message = 'Starting distribution of RAF prod data\n'

    command = 'rsync -qu '+temp_dir+'/RAF_data/* '+dat_dir+'/field_data'
    message_prod = 'Syncing production data into place: '+command+'\n'
    logging.info(message_prod)
    os.system(command)
    
    command = 'rsync -qu '+temp_dir+'/RAF_data/* '+ftp_dir+'/RAF_data'
    message_ftp = 'Syncing production data to rdat: '+command+'\n'
    logging.info(message_ftp)
    os.system(command)

    command = 'rsync -rqu '+dat_dir+'/field_data/* '+dat_dir
    message_field = 'Syncing production data into place: '+command+'\n'       
    logging.info(message_field)
    os.system(command)

    final_message = final_message + message_prod + message_ftp + message_field

    return(final_message)

#############################################################################
# Function to distribute PI data
#############################################################################
def dist_PI():
    
    final_message = 'Starting distribution of PI data\n'

    command = 'rsync -rqu '+temp_dir+'/PI_data '+ftp_dir
    message = 'Syncing PI_data into place: '+command+'\n'
    logging.info(message)
    os.system(command)

    final_message = final_message + message
    
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

##############################################################################
### MAIN
##############################################################################
if __name__ == '__main__':

    try:
        # Get the arguments from the command line
        temp_dir    = sys.argv[1]
        logfile = sys.argv[2]
#        print temp_dir

        # Set up logging
        logger = logging.getLogger()
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000, backupCount=9)
        formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    except IndexError:

        # Usage statement
        print "\nUsage: %s path logfile" % sys.argv[0]
        print "    path - path to data files  "
        print "         (i.e. /net/ftp/pub/data/incoming/<project>/data_synced)"
        print "    logfile - logfile name (i.e. /tmp/ads_data_catcher.log)"
        print "\nThe logfile is rotated every 1000000 bytes with a backup count of 9."

    dir_check()
    dist_raw()
    dist_prod()
    dist_PI()
   
    exit(1)

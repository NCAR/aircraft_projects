#!/usr/bin/python

"""
This script uses the pyinotify module to monitor
the creation of new files that are created in the 
incoming data' folder.  When a new file is detected it
is handled according to the type of file it is:
    Raw Data
    Product Data - form PROD_<PROJECT>_<FL##>.zip
    Camera images

"""

import logging, logging.handlers
import os, sys, pyinotify, re, sys
import time
import smtplib
from email.mime.text import MIMEText

reProdFile = re.compile("PROD_(\S+)_(\S+).zip")
reRawProjName = re.compile("project name: (\S+)")

##  Configuration for the distribution - modify the following
NAS_in_field =    False                          # Set to false for ftp 
temp_dir =        '/tmp/'                        # Where we unzip & put busy
dat_parent_dir =  '/scr/raf_data/'               # Where nc files go
rdat_parent_dir = '/scr/raf_Raw_Data/'           # where raw ads files go
ftp_parent_dir =  '/net/ftp/pub/data/download/'  # Where nc files go for PIs
##  End of Configuration


###############################################################################
#  dist_prod_file(fn) - takes a file path&name that is an RAF production 
#                       file delivered from the field either through ftp
#                       or Synced from a field NAS.
#  It expects a file name of the form PROD_<PROJ_NAME>_<FLIGHT>.zip
#  and that it will contain netCDF, kml and ancillary product files
#  that are to be copied to the raf data directory (dat_parent_dir+<PROJ_NAME)
#  and also copied to the ftp distribution area for PI acquisition.
#  
#  If the files have been ftp'd over, they will be removed so that the
#  production scripts can be rerun, generate and ftp over new ones.  If not 
#  then they won't so that the Sync function doesn't just write them again. 
#  Sync in the field will update them in the case of rerunning prduction in
#  the field.
##############################################################################
def dist_prod_file(fn):

    final_message = "Starting distribution of RAF Field Production Data\n"
    # This script is not re-entrant - bail if running
    busy_file = temp_dir+'DIST_PROD'
    if os.path.isfile(busy_file):
        st=os.stat(busy_file)
        bfiletime = st.st_mtime
        curtime = time.mktime(time.localtime())
        if (curtime-bfiletime) > 3000.0:
            logging.info(" Busy file:"+busy_file+" more than 5 minutes old, deleting.")
            os.remove(busy_file)
        else:
            logging.info("  Product Dist busy file:"+busy_file+" exists. Exiting")
            sys.exit(0)
    command = 'touch '+busy_file
    os.system(command)

    # Verify we've got the right file type
    data = None
    file_dir,file_name = os.path.split(fn)
    if not file_name.startswith('PROD_') or not file_name.endswith('.zip'):
        logging.error("Error - called w/non-product file:"+fn)
        os.remove(busy_file)
        sys.exit(1)
    message = "Got an ADS Product file:"+fn
    final_message = final_message + message + '\n'
    logging.info(message)

    # Work in the /tmp dir - If we have a NAS in the field leave file in 
    # so BTSync doesn't keep replacing it, if move it so that ftp can 
    # replace it if they choose to reprocess in the field.
    if NAS_in_field:
        command = 'cp -f '+fn+' '+temp_dir
        logging.info('copy file to temp dir: '+command)
    else: 
        command = 'mv -f '+fn+' '+temp_dir
        logging.info('Moving file to temp dir: '+command)
    os.system(command)
    os.chdir(temp_dir)
    command = 'unzip '+file_name
    logging.info('Unzipping product file: '+command)
    os.system(command)
    # Get project and flight info from file_name
    m=reProdFile.match(file_name)
    if m:
        project = m.group(1)
        flight = m.group(2)
    else:
        logging.error('Filename does not match expected pattern!!')
        logging.error('Bailing out!')
        os.remove(busy_file)
        sys.exit(1)
        

    #Make sure raf data directory exists
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
            os.remove(busy_file)
            sys.exit(1)

    logging.info('Data dir: '+dat_dir)
    command = 'cp -f '+project+'_'+flight+'* '+dat_dir
    logging.info('Copying to raf data:'+command)
    os.system(command)

    #Make sure ftp data directory exists
    if os.path.isdir(ftp_parent_dir+project):
        ftp_dir = ftp_parent_dir+project
    elif os.path.isdir(ftp_parent_dir+project.lower()):
        ftp_dir = ftp_parent_dir+project.lower()
    else:
        ftp_dir = ftp_parent_dir+project.lower()
        try:
            os.mkdir(ftp_dir)
        except:
            logging.error('Could not make ftp directory:'+ftp_dir)
            logging.error('Bailing out')
            os.remove(busy_file)
            sys.exit(1)

    logging.info('FTP dir: ' + ftp_dir)
    command = 'cp -f '+project+'_'+flight+'* '+ftp_dir
    message = "Moving files to ftpdir:"+command
    final_message = final_message+message+'\n'
    logging.info(message)
    os.system(command)
    
    # if files are being ftp'd in, then remove it so newly processed file
    #   can be written to the directory.
    if NAS_in_field != True:
        if os.path.isfile(fn):
            os.remove(fn)

    emailfilename = 'email.addr.txt'
    fo = open(emailfilename, 'r+')
    email = fo.readline()
    fo.close()
    message = "About to send e-mail to:"+email
    logging.info(message)
    msg = MIMEText(final_message)
    msg['Subject'] = 'Receive and Disribute message for:'+project+'  flight:'+flight
    msg['From'] = 'ads@groundstation'
    msg['To'] = email

    s = smtplib.SMTP('localhost')
    s.sendmail('ads@tikal.eol.ucar.edu',email,msg.as_string())

    logging.info("Message: "+msg.as_string())
    s.quit()
    os.remove(emailfilename)
    os.remove(busy_file)
    os.remove(project+'_'+flight+'*')
    sys.exit(0)

##   End of dist_prod_file

###############################################################################
#  dist_raw_file(fn) - takes a file path&name that is an RAF raw ads
#                       file delivered from the field either through ftp
#                       or Synced from a field NAS.
#  It expects a file name of the form <ads file name>.bz2
#  and that it will contain a raw ads file that's been bzipped
#  that is to be copied to the raf raw data directory 
#  (raw_parent_dir+<PROJ_NAME)
#  
#  If the files have been ftp'd over, they will be removed so that the
#  production scripts can be rerun, generate and ftp over new ones.  If not 
#  then they won't so that the Sync function doesn't just write them again. 
#  Sync in the field will update them in the case of rerunning prduction in
#  the field.
##############################################################################
def dist_raw_file(fn):

    # This script is not re-entrant - bail if running
    busy_file = temp_dir+'DIST_RAW'
    if os.path.isfile(busy_file):
        logging.info("  Product Dist busy file:"+busy_file+" exists. Exiting")
        os.remove(busy_file)
        sys.exit(0)
    command = 'touch '+busy_file
    os.system(command)

    # Raw file in bz2 form
    # Put the file in /tmp (so sync doesn't keep writing it)
    # unzip it, get project name from ascii header
    # move the file into the raw data directory
    if not fn.endswith('.bz2'):
        logging.error('File does not match expected pattern:'+fn)

    logging.info("Got an ADS Raw file:"+fn)

    #  Copy to /tmp for unzipping so rsync won't send new bz2 file
    command = 'cp '+fn+' '+temp_dir
    logging.info('copy file to temp dir: '+command)
    os.system(command)
    os.chdir(temp_dir)
    filedir,bzfilename = os.path.split(fn)
    command = 'bunzip2 '+bzfilename
    logging.info('Unzipping product file: '+command)
    os.system(command)
    bzelts = bzfilename.split('.')
    filename = bzelts[0]+'.'+bzelts[1]
    logging.info('Stepping through file:'+filename+' to get project')
    file = open(filename)
    for line in file:
        m = reRawProjName.match(line)
        if m:
            logging.info('  Found proj line:'+line)
            project = m.group(1)
            break
    raw_ads_dir = rdat_parent_dir + project
    if not os.path.isdir(raw_ads_dir):
        try:
            os.mkdir(raw_ads_dir)
        except:
            logging.error('Could not make ftp directory:'+ftp_dir)
            logging.error('Bailing out')
            os.remove(busy_file)
            sys.exit(1)

    logging.info('Raw Data Dir: '+raw_ads_dir)
    command = 'mv -f '+filename+' '+raw_ads_dir
    logging.info(' Moving raw file into place:'+command)
    os.system(command)
    os.remove(busy_file)
## End of dist_raw_data  ###


if __name__ == '__main__':
    try:
        path    = sys.argv[1]
        logfile = sys.argv[2]

        # setup logging
        logger = logging.getLogger()
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=8192, backupCount=10)
        formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logging.info('Catch ads field data deposited to:'+path)

    except IndexError:
        print "\nUsage: %s path logfile" % sys.argv[0]
        print "    path    - path to data files  (i.e. /net/ftp/pub/data/ads/ads)"
        print "    logfile - logfile name (i.e. /tmp/ads_data_catcher.log)"
        print "\nThe logfile is rotated every 8192 bytes with a backup count of 10."
        os.remove(busy_file)
        sys.exit(1)

    if not os.path.isdir(path):
        logging.critical("exiting, folder: '%s' does not exist." % path)
        os.remove(busy_file)
        sys.exit(1)

    # Look for files > 1 minute old and < 11 minutes old
     
    one_min_ago = time.time() - 60
    one_hour_ago = time.time() - 3600
    logging.info('Looking for new files in:'+path)
    for file in os.listdir(path):
        fullfile = path+file
        if os.path.isfile(fullfile):
            st=os.stat(fullfile)
            mtime=st.st_mtime
            logging.info('file:'+file+'  mtime = '+str(mtime)+'  - one:'+str(mtime - one_min_ago)+ '  - hour:'+str(mtime - one_hour_ago))
            if mtime > one_hour_ago and mtime < one_min_ago:
                logging.info('file met time criteria'+fullfile)

                # If we find a file - fork off process to deal with it
                if file.startswith('PROD_') and file.endswith('.zip'):
                    newpid = os.fork()
                    if newpid == 0:
                        dist_prod_file(fullfile)
                    else:
                        pids = (os.getpid(), newpid)
                        logging.info("parent: %d, child: %d" % pids)

                elif file.endswith('.bz2'):
                    newpid = os.fork()
                    if newpid == 0:
                        dist_raw_file(fullfile)
                    else:
                        pids = (os.getpid(), newpid)
                        logging.info("parent: %d, child: %d" % pids)

                else:
                    logging.info('  - Does not match naming convetions')
                    logging.info('  - skipping')

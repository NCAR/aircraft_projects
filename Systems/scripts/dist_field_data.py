#!/usr/bin/env python
#
# Runs in cron on tikal as user ads

"""
This script uses the pyinotify module to monitor
the creation of new files that are created in the 
incoming data' folder.  When a new file is detected it
is handled according to the type of file it is:
    Raw Data - ads files, form .ads or .ads.bz2
    Product Data - form <PROJECT><FL##>.ext.zip or <PROJECT><FL##>.ext
    Camera images - flight_number_<FL##>.tar - NOT YET IMPLEMENTED
    qc/ is not distributed because those images are in the field catalog too.
    PMS2D files - 20160210_115216_rf10.2d 
    2DS files - base170301134744.2DS - NOT YET IMPLEMENTED
Right now, the patterns assume that product files begin with the project name.
If they don't, then the beginning of the filename will be assumed to be the 
project and the files are written to DATA_DIR/<bad_project>, e.g. /scr/raf_data/picarro_
for files named picarro_rf01.zip.

When complete, this script sends an email to address in email.addr.txt
"""

import logging, logging.handlers
import os, sys, pyinotify, re, sys
import time
import smtplib
from email.mime.text import MIMEText

# regex to match files we want this script to handle. Can't count on files being
# zipped so handle all sorts of pattern variations.
reZip = re.compile("zip")
reRawFile = re.compile("(\d+)_(\d+)_(\S\S\d\d).[ads|2d]")
reProdFile = re.compile("(\S+)(\Sf\d\d)\S*\.(\S+)")
reRawProjName = re.compile("project name: (\S+)")
reRawProjName2d = re.compile("<Project>(\S+)</Project>")

###  Configuration for the distribution - modify the following
cronTime = 60*24	# How often (in mins) script is run from crontab
# SOCRATES - Since ads files take 7 hours+ to transfer but are timestamped 
# at start of transfer, need to go back 8 hours.
NAS_in_field =    True                            # Set to false for ftp 
temp_dir =        '/tmp/'                         # Where we unzip & put busy
dat_parent_dir =  os.environ["DATA_DIR"] + '/'    # Where nc files go
rdat_parent_dir = os.environ["RAW_DATA_DIR"] + '/'# Where raw ads files go
ftp_parent = False				  # Set to true to copy to ftp
ftp_parent_dir =  '/net/ftp/pub/data/download/'   # Where nc files go for PIs
busy_file = temp_dir+'DIST_PROD'  # Temp file that exists if program is running. 
                                  # Allows script to not clobber itself
###  End of Configuration

# Initialize some blank strings
final_message = ""
project = ""
flight = ""
found_data = False


###############################################################################
#  dist_prod_file(fn) - takes a file path&name that is an RAF production 
#                       file delivered from the field either through ftp
#                       or Synced from a field NAS.
#  It expects a file name of the form reProdFile (defined above)
#  that are to be copied to the raf data directory (dat_parent_dir+<PROJ_NAME>)
#  and also copied to the ftp distribution area for PI acquisition (if requested).
#  
#  If the files have been ftp'd over, they will be removed so that the
#  production scripts can be rerun, generate and ftp over new ones.  If not 
#  then they won't so that the NAS Sync function doesn't just write them again. 
#  Sync in the field will update them in the case of rerunning production in
#  the field.
##############################################################################
def dist_prod_file(fn,mtime,found_data):

    final_message = "Starting distribution of RAF Field Production Data\n"
    # This script is not re-entrant - bail if running
#    if os.path.isfile(busy_file):
#        st=os.stat(busy_file)
#        bfiletime = st.st_mtime
#        curtime = time.mktime(time.localtime())
#        if (curtime-bfiletime) > 3000.0:
#            logging.info(" Busy file:"+busy_file+" more than 5 minutes old, deleting.")
#            os.remove(busy_file)
#        else:
#            logging.info("  Product Dist busy file:"+busy_file+" exists. Exiting")
#	    final_message = final_message + "  Product Dist busy file:"+busy_file+" exists. Exiting\n"
#            send_mail_and_die(final_message)
#	    exit(1)
#    command = 'touch '+busy_file
#    os.system(command)

    # Verify we've got the right file type
    data = None
    file_dir,file_name = os.path.split(fn)
    m=reProdFile.match(file_name)
    if not m:
	message = "Error - called w/non-product file:"+fn
        logging.error(message)
#	if os.path.isfile(busy_file):
#            os.remove(busy_file)
	send_mail_and_die(final_message + message)
    message = "Got an ADS Product file: "+fn
    final_message = final_message + message + '\n'
    logging.info(message)

    # Get project and flight info from file_name
    m=reProdFile.match(file_name)
    if m:
        project = m.group(1)
        flight = m.group(2)
    else:
        logging.error('Filename does not match expected pattern!!')
        logging.error('Bailing out!')
#	if os.path.isfile(busy_file):
#            os.remove(busy_file)
        send_mail_and_die(final_message + ' Filename does not match expected pattern!!')

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
#	    if os.path.isfile(busy_file):
#                os.remove(busy_file)
	    send_mail_and_die(final_message+ ' Could not make product directory:'+dat_dir)

    # Check if file has already been copied
    try:
        if os.stat(dat_dir+"/"+file_name).st_mtime < mtime:
            # File is updated, so copy it.
            logging.info("File is updated. Copy it.")
            found_data=True
        else:
            # File is not new - abort
            message = "File already copied. Refusing to recopy.\n"
            logging.info(message)
            final_message = final_message + message

            # if files are being ftp'd in, then remove it so newly processed file
            # can be written to the directory.
            if NAS_in_field != True:
               if os.path.isfile(fn):
                    os.remove(fn)

            return(final_message)
    except:
        # File doesn't exist, so copy it.
        logging.info("File is new. Copy it.")
        found_data=True

    # Work in the /tmp dir - If we have a NAS in the field leave file in 
    # so BTSync doesn't keep replacing it, if move it so that ftp can 
    # replace it if they choose to reprocess in the field.
    if NAS_in_field:
        command = '/bin/cp -f '+fn+' '+temp_dir
        logging.info('copy file to temp dir: '+command+'\n')
    else: 
        command = 'mv -f '+fn+' '+temp_dir
        logging.info('Moving file to temp dir: '+command)
    os.system(command)

    # Now that file has been copied to temp_dir, work there.
    os.chdir(temp_dir)

    # If file is zipped, unzip it
    m = reZip.match(file_name)
    if m:
	command = 'unzip -o '+file_name
        logging.info('Unzipping product file: '+command)
        os.system(command)

    logging.info('Data dir: '+dat_dir)
    command = '/bin/cp -f '+file_name+' '+dat_dir
    logging.info('Copying to raf data:'+command)
    os.system(command)

    #Make sure ftp data directory exists
    if ftp_parent:	# If requested
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
#                if os.path.isfile(busy_file):
#                    os.remove(busy_file)
                send_mail_and_die(final_message)

        logging.info('FTP dir: ' + ftp_dir)
        command = '/bin/cp -f '+project+flight+'* '+ftp_dir
        message = "Moving files to ftpdir: "+command
        final_message = final_message+message+'\n'
        logging.info(message)
        os.system(command)
    
    # if files are being ftp'd in, then remove it so newly processed file
    # can be written to the directory.
    if NAS_in_field != True:
        if os.path.isfile(fn):
            os.remove(fn)

    return(final_message)
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
def dist_raw_file(fn,mtime,found_data,project):

    final_message = "Starting distribution of RAF Field Raw Data\n"
    # This script is not re-entrant - bail if running
#    busy_file = temp_dir+'DIST_RAW'
#    if os.path.isfile(busy_file):
#        logging.info("  Product Dist busy file:"+busy_file+" exists. Exiting")
#        os.remove(busy_file)
#	send_mail_and_die(final_message+ "  Product Dist busy file:"+busy_file+" exists. Exiting")
#    command = 'touch '+busy_file
#    os.system(command)

    # Raw file in bz2 form
    # Put the file in /tmp (so sync doesn't keep writing it)
    # unzip it, get project name from ascii header
    # move the file into the raw data directory
#    if not fn.endswith('.bz2'):
#        logging.error('File does not match expected pattern:'+fn)

    logging.info("Got an PMS2D or ADS Raw file:"+fn)

    #  Copy to /tmp for unzipping so rsync won't send new bz2 file
    command = '/bin/cp '+fn+' '+temp_dir
    message = "copy file to temp dir: "+command+'\n'
    logging.info(message)
    final_message = final_message + message
    os.system(command)

    os.chdir(temp_dir)

    if fn.endswith('.bz2'):
        filedir,bzfilename = os.path.split(fn)
        command = 'bunzip2 -f '+bzfilename
        message = 'Unzipping product file: '+command
        logging.info(message)
        final_message = final_message + message
        os.system(command)
        bzelts = bzfilename.split('.')
        filename = bzelts[0]+'.'+bzelts[1]
    else:
	filedir,filename = os.path.split(fn)

    if fn.endswith(".ads"):
      message = 'Stepping through file:'+filename+' to get project\n'
      logging.info(message)
      final_message = final_message + message

      file = open(filename)
      for line in file:
          m = reRawProjName.match(line)
          if m:
              message = '  Found proj line:'+line
              logging.info(message)
              final_message = final_message + message
              project = m.group(1)
              break

    if fn.endswith(".2d"):
      message = 'Stepping through file:'+filename+' to get project\n'
      logging.info(message)
      final_message = final_message + message

      file = open(filename)
      for line in file:
          m = reRawProjName2d.search(line)
          if m:
              message = '  Found proj line:'+line
              logging.info(message)
              final_message = final_message + message
              project = m.group(1)
              break

      # Find or create project dir under RAW_DATA_DIR
      raw_ads_dir = rdat_parent_dir + project
      if not os.path.isdir(raw_ads_dir):
          try:
              os.mkdir(raw_ads_dir)
          except:
	      message = 'Could not make ftp directory:'+ftp_dir
              logging.error(message)
              logging.error('Bailing out')
#	      if os.path.isfile(busy_file):
#                  os.remove(busy_file)
  	      send_mail_and_die(final_message + message)
	      exit(1)

      logging.info('Raw Data Dir: '+raw_ads_dir)
    
    if fn.endswith(".2d"):
       raw_ads_dir = rdat_parent_dir + project + "/PMS2D"
    else:
       raw_ads_dir = rdat_parent_dir + project
    
    # Check if file has already been copied
    try:
        if os.stat(raw_ads_dir+"/"+filename).st_mtime < mtime:
            # File is new, so copy it.
            logging.info("File is updated. Copy it.")
            found_data=True
        else:
            # File is not new - abort
            message = "ADS/PMS2D raw file already copied. Refusing to recopy.\n"
            logging.info(message)
            return(final_message+message)
    except:
        # File doesn't exist, so copy it.
        logging.info("File is new. Copy it.")
        found_data=True

    command = 'mv -f '+filename+' '+raw_ads_dir
    message = ' Moving raw file into place: '+command
    logging.info(message)
    final_message = final_message + message
    os.system(command)

#    if os.path.isfile(busy_file):
#        os.remove(busy_file)

    return(final_message)
## End of dist_raw_data  ###

##############################################################################
def send_mail_and_die(body):

    emailfilename = 'email.addr.txt'
    os.chdir(cwd)
    fo = open(emailfilename, 'r+')
    email = fo.readline()
    fo.close()
    logging.info("About to send e-mail to: "+email)
    body = body + 'See /tmp/ads_data_catcher.log\n'
    msg = MIMEText(body)
    msg['Subject'] = 'Receive and Disribute message for:'+project+'  flight:'+flight
    msg['From'] = 'ads@groundstation'
    msg['To'] = email

    s = smtplib.SMTP('localhost')
    s.sendmail("ads@groundstation",email,msg.as_string())
    logging.info("Message:\n"+msg.as_string())
    s.quit()

    if os.path.isfile(busy_file):
        os.remove(busy_file)
    if os.path.isfile(project+flight+'*'):
        os.remove(project+flight+'*')

    exit(1)

## End of send_mail_and_die ##

##############################################################################
### MAIN
##############################################################################

if __name__ == '__main__':

    cwd = os.getcwd()

    try:
        path    = sys.argv[1]
        logfile = sys.argv[2]

        # setup logging
        logger = logging.getLogger()
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000, backupCount=9)
        formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logging.info('########################################################')
        logging.info('# Catch ads field data deposited to:'+path)
        logging.info('########################################################')

    except IndexError:
	# Usage statement
        print "\nUsage: %s path logfile" % sys.argv[0]
        print "    path - path to data files  "
	print "         (i.e. /net/ftp/pub/data/incoming/<project>/data_synced)"
        print "    logfile - logfile name (i.e. /tmp/ads_data_catcher.log)"
        print "\nThe logfile is rotated every 1000000 bytes with a backup count of 9."
        if os.path.isfile(busy_file):
            os.remove(busy_file)
	exit(1)

    # Confirm that path to uploaded data files (as entered on command line) exists
    if not os.path.isdir(path):
	message = "exiting, folder: '%s' does not exist." % path
        logging.critical(message)
        if os.path.isfile(busy_file):
            os.remove(busy_file)
	send_mail_and_die(message)
	exit(1)

    # This script runs in cron every cronTime minutes, so look for files > 1 minute 
    # old # and < cronTime+ 1 minutes old
    one_min_ago = time.time() - 60
    one_hour_ago = time.time() - cronTime*60
    logging.info('Looking for new files in:'+path+' that were written in last '
	    +str(cronTime)+' minutes so after '+str(one_hour_ago))
    found = False
    for root, dirs, files in os.walk(path):
     if not re.search(r'\.sync',root):
      #print "ROOT: "+root
      for name in dirs:
       if not re.search(r'\.sync',name):
	#print "NAME: " +root+name
        for filename in os.listdir(root+"/"+name):
         if not re.search(r'\.sync',name):
	  #print "FILENAME: " +root+name+"/"+filename
          fullfile = root+name+"/"+filename
	  #print fullfile
          if os.path.isfile(fullfile):
            st=os.stat(fullfile)
            mtime=st.st_mtime
            #logging.info('File '+filename+' has time '+str(mtime))
            if mtime > one_hour_ago and mtime < one_min_ago and not filename.endswith('.bts'): # bts files are mid-transfer
                logging.info('file met time criteria '+fullfile)
		found = True

                # If we find a file - fork off process to deal with it
		a=reRawFile.match(filename)
                m=reProdFile.match(filename)
                if a or filename.endswith('.bz2'): # Sometimes ads files are bzipped
		                               # to make them quicker to transfer
                    #newpid = os.fork()
                    #if newpid == 0:
                    final_message = final_message + dist_raw_file(fullfile,mtime,found_data,project)
                    #else:
                    #    pids = (os.getpid(), newpid)
                    #    logging.info("parent: %d, child: %d" % pids)
		elif m:
                    #newpid = os.fork()
                    #if newpid == 0:
                    final_message = final_message + dist_prod_file(fullfile,mtime,found_data)
                    #else:
                    #    pids = (os.getpid(), newpid)
                    #    logging.info("parent: %d, child: %d" % pids)

                else:
                    logging.info('  - Does not match naming conventions')
                    logging.info('  - skipping')
    if not found:
	message = "No files found that meet criteria"
	logging.info(message)
	final_message = final_message + message

    # Only send email from here if copied new files successfully. 
    # Failure messages are sent as errors encountered above.
    if found_data:
        send_mail_and_die(final_message)

    exit(1)

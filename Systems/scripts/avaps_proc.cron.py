#!/usr/bin/python
#
# This script performs the processing of AVAPS D files received on the server
# based on descriptions in the "(Remote) AVAPS Operator's Manual" 
# written by Nick Potts and found here: 
# https://docs.google.com/document/d/17jvRVrBkD8IKH5rnYvBAqNNfawaADW8DPDsNQbmlMNk/
#
# Configuration for the script is found at the top and should be the only thing
# you need to modify for fulfilling any of the 3 types of transfers indicated:
#  Bare Minimum
#  Bare Monty and Full Monty are treated the same (we just always make skew-T's)
#
# The dropsonde file(s) are compressed for transfer.
#
# If the transfer fails then the file is uncompressed.
#
# This is set up to run out of a cron job every minute
# * * * * * /home/local/Systems/scripts/avaps_proc.cron.py
#
import os
import sys
import glob
import ftplib
import syslog

####################  CONFIGURATION #######################################
send_Dfiles = 'false'
send_prodfiles = 'true'
# The following probably won't change
Aspen_QC_exe = '/home/local/src/aspenqc/bin/Aspen-QC'
d_file_re = 'D????????_??????_P.?'
raw_data_dir = '/mnt/r1/dropsondes/'
ads_web_dir = '/var/www/html/skewt/'
grnd_ftp_host = 'catalog.eol.ucar.edu'
grnd_skewt_dir = '/pub/incoming/AVAPS/skewt'
grnd_wmo_dir = '/pub/incoming/AVAPS/bufr'
###################  END OF CONFIGURATION #################################
# Clean up name of script for logging
ident = sys.argv[0][sys.argv[0].rfind("/")+1:]

os.chdir(raw_data_dir)

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile('BUSY'):
    syslog.syslog('exiting, BUSY')
    syslog.closelog()
    sys.exit(1)
os.system('touch BUSY')

list=glob.glob(d_file_re)

# bail out if no files are found
if (not list):
    # syslog.syslog('exiting, nothing to send')
    os.remove('BUSY')
    syslog.closelog()
    sys.exit(1)

# Put in sequential order to support catalog maps
list = sorted(list)
for file in list:

    # Make product files (skewt and tempdrop) 
    os.putenv('ASPENCONFIG', '/home/local/src/aspenqc')
    os.system('/bin/cp '+file+' tmp')
    skewt_fn = file+'.svg'
    wmo_fn = file+'.wmo'
    cmd = Aspen_QC_exe + ' -i '+file+ ' -g '+skewt_fn+' -w '+wmo_fn
    os.system(cmd)

    # Put new skewt into ads web space
    copy(skewt_fn, ads_web_dir_)

    if (send_Dfiles):
        try:
            syslog.syslog(ident+':compressing and PQinserting:'+file)
            cmd='bzip2 '+file
            os.system(cmd)
            file_bz2=file+'.bz2'

            # mv file to another folder then insert it
            cmd = '/home/ldm/bin/pqinsert '+file_bz2
            os.system(cmd)
            os.rename(file_bz2, 'inserted/'+file_bz2)

        except:
            syslog.syslog(ident+':failed to compress/PQinsert:'+file)
            cmd='bunzip2 '+file_bz2
            os.system(cmd)

    if (send_prodfiles)
    
        try:
            syslog.syslog(ident+'opening FTP connection for:'+skewt_fn+ \
                          ' and '+wmo_fn)
    
            ftp = ftplib.FTP('grnd_ftp_host')
            ftp.login('anonymous', '')
            ftp.cwd(grnd_skewt_dir)
            ftp.storbinary('stor '+skewt_fn, open(skewt_fn, 'rb'))
            syslog.syslog(ident+':'+skewt_fn+' sent')
            os.rename(skewt_fn, 'sent/'+skewt_fn)
            ftp.cwd(grnd_wmo_dir)
            ftp.storbinary('stor '+wmo_fn, open(wmo_fn, 'rb'))
            syslog.syslog(ident+':'+wmo_fn+' sent')
            os.rename(wmo_fn, 'sent/'+wmo_fn)
    
        except ftplib.all_errors, e:
            syslog.syslog('Error putting file: %s' % e)
    
        ftp.quit() 


# remove busy flag
os.remove('BUSY')
syslog.closelog()
# in raf/GoogleEarth/avaps2kml directory.
os.system('avaps2kml')

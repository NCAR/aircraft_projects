#!/usr/bin/python
#
# This script attempts to send the dropsonde files to the ground via FTP.
#
# The dropsonde file(s) are compressed for transfer.
#
# If the transfer fails then the file is uncompressed.
#
# This is set up to run out of a cron job every minute
# */1 * * * * /home/local/Systems/scripts/send_avaps.cron.py
#
import os
import sys
import glob
import ftplib
import syslog

# Clean up name of script for logging
ident = sys.argv[0][sys.argv[0].rfind("/")+1:]
syslog.openlog(ident, 0, syslog.LOG_CRON)

os.chdir('/home/tmp/send_to_grnd/')

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile('BUSY'):
    syslog.syslog('exiting, BUSY')
    syslog.closelog()
    sys.exit(1)
os.system('touch BUSY')

list=glob.glob('D????????_??????_P.?')

# bail out if no files are found
if (not list):
    # syslog.syslog('exiting, nothing to send')
    os.remove('BUSY')
    syslog.closelog()
    sys.exit(1)

# sort files by creation time in reverse order
list.sort(lambda y, x: cmp(os.path.getmtime(x),os.path.getmtime(y)))

# Send the latest file first
for file in list:

    # bzip2/bunzip2 doesn't modify the creation date of the file!
    cmd='bzip2 --best '+file
    os.system(cmd)
    file_bz2=file+'.bz2'

    while True:
        try:
            syslog.syslog('opening FTP connection')

            ftp = ftplib.FTP('eol-rt-data.guest.ucar.edu')
            ftp.login('ads', 'blue;spruce')
            ftp.cwd('avaps')
            ftp.cwd('c130')

            ftp.storbinary('stor '+file_bz2, open(file_bz2, 'r'))
            syslog.syslog(file_bz2+' sent')
            break

        except ftplib.all_errors, e:
            syslog.syslog('Error putting file: %s' % e)

            cmd='bunzip2 '+file_bz2
            os.system(cmd)
            os.remove('BUSY')
            syslog.closelog()
            sys.exit(1)

    ftp.quit() 

# remove busy flag
os.remove('BUSY')
syslog.closelog()

#!/usr/bin/python
#
# This script attempts to send the dropsonde files to the ground via FTP.
#
# The dropsonde file(s) are compressed for transfer.
#
# If the transfer fails then the file is uncompressed.
#
# This is set up to run out of a cron job every minute
# * * * * * /home/local/Systems/scripts/send_avaps.cron.py
#
import os
import sys
import glob
import ftplib
import syslog

# Clean up name of script for logging
ident = sys.argv[0][sys.argv[0].rfind("/")+1:]

os.chdir('/mnt/r1/dropsondes/')

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

    # Make a skewt and put in web space.
    os.putenv('ASPENCONFIG', '/home/local/src/aspenqc');
    os.system('/bin/cp '+file+' tmp');
    os.system('/home/local/src/aspenqc/Aspen-QC -i '+file+' -g /var/www/html/skewt/'+file+'.svg');

    # bzip2/bunzip2 doesn't modify the creation date of the file!
    syslog.syslog('compressing '+file)
    cmd='bzip2 --best '+file
    os.system(cmd)
    file_bz2=file+'.bz2'

    try:
        syslog.syslog('opening FTP connection for '+file_bz2)

        ftp = ftplib.FTP('data.eol.ucar.edu')
        ftp.login('anonymous', '')
        ftp.cwd('/pub/incoming/predict/gv/')

        ftp.storbinary('stor '+file_bz2, open(file_bz2, 'r'))
        syslog.syslog(file_bz2+' sent')

    except ftplib.all_errors, e:
        syslog.syslog('Error putting file: %s' % e)

        cmd='bunzip2 '+file_bz2
        os.system(cmd)
        os.remove('BUSY')
        syslog.closelog()
        sys.exit(1)

    ftp.quit() 

    # exit for loop early... only send one per minute.
    break

# remove busy flag
os.remove('BUSY')
syslog.closelog()
os.chdir('tmp')
# in raf/GoogleEarth/avaps2kml directory.
os.system('avaps2kml')

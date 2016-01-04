#!/usr/bin/python
#
# This script attempts to send the compressed dropsonde files to ingest via ldm.
#
# This is set up to run out of a cron job every minute
# */1 * * * * /home/local/Systems/scripts/send_avaps_to_ingest.cron.py
#
import os
import sys
import glob
import stat
import syslog
import tarfile

# Clean up name of script for logging
script = sys.argv[0][sys.argv[0].rfind("/")+1:]

os.chdir('/mnt/r1/tmapper/')

# This cron script is not re-entrant, bail out if still running.
if os.path.isfile('BUSY'):
  syslog.syslog(script+': exiting, BUSY')
  sys.exit(1)
os.system('touch BUSY')

os.system('mkdir -p inserted')

files=glob.glob('*.tif')
for file in files:
    os.system('bzip2 '+file);

files=glob.glob('*.bz2')

# bail out if no files are found
if (not files):
# syslog.syslog(script+': exiting, nothing to send')
  os.remove('BUSY')
  sys.exit(1)

# sort files by creation time
files.sort(lambda x, y: cmp(os.path.getmtime(x),os.path.getmtime(y)))

for file in files:
  try:
    # ensure that file is complete before inserting
#    tarball = tarfile.open(file, 'r:bz2')
#    tarfiles = tarball.getnames()
#    tarball.close()
    syslog.syslog(script+': '+file+' is complete.')

    # mv file to another folder then insert it
    os.rename(file, 'inserted/'+file)
    os.system("/home/ldm/bin/pqinsert inserted/"+file)

  except:
    syslog.syslog(script+': '+file+' is incomplete... must still be FTPing down.')

# remove busy flag
os.remove('BUSY')

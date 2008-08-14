#!/usr/bin/python
#
# Sends the compressed dropsonde files to ingest via ldm.
#
# This script is intended to be run by ads on eol-rt-data.
# This script complements send_avaps.cron.py.
#
# This is set up to run out of a cron job every minute
# */1 * * * * /home/local/Systems/scripts/send_avaps_to_ingest.cron.py
#
import os
import sys
import glob
import stat
import time
import syslog

# Clean up name of script for logging
script = sys.argv[0][sys.argv[0].rfind("/")+1:]

os.chdir('/home/ads/avaps/nrlp3/')

# This cron script is not re-entrant, bail out if still running.
if os.path.isfile('BUSY'):
  syslog.syslog(script+': exiting, BUSY')
  sys.exit(1)
os.system('touch BUSY')

os.system('mkdir -p inserted')

# get the start time of this script
starttime=time.time()

files=glob.glob('D20*.tar.bz2')

# bail out if no files are found
if (not files):
  syslog.syslog(script+': exiting, nothing to send')
  os.remove('BUSY')
  sys.exit(1)

# sort files by creation time
files.sort(lambda x, y: cmp(os.path.getmtime(x),os.path.getmtime(y)))

# ensure that the last file is complete before proceeding
file=files[len(files)-1]
while True:
  aaa = os.stat(file)[stat.ST_SIZE]
  time.sleep(2)
  bbb = os.stat(file)[stat.ST_SIZE]
  if (aaa==bbb):
    break

  # time out after 2 minutes while waiting for file completion
  if ( (time.time() - starttime) > 120):
    syslog.syslog(script+': exiting, timed out waiting for last file')
    os.remove('BUSY')
    sys.exit(1)

# mv files to another folder then insert them
for file in files:
  os.rename(file, 'inserted/'+file)
  os.system("pqinsert inserted/"+file)

# remove busy flag
os.remove('BUSY')

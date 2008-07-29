#!/usr/bin/python
#
# This script attempts to send the dropsonde files to the ground via FTP.
#
# The dropsonde file(s) are archived and compressed for transfer.
#
# If the transfer fails then the archive is discarded and then recreated
# (and possibly appended to) the next time the script runs.
#
# This is set up to run out of a cron job every 5 minutes
# 5 * * * * /home/local/Systems/scripts/send_avaps.cron.py
#
import os
import sys
import glob
import stat
import time
import ftplib

os.chdir('/home/tmp/send_to_grnd/')

# This cron script is not re-entrant, bail out if still running.
if os.path.isfile('BUSY'):
# print 'exiting.  send_avaps.cron.py is still running...'
  sys.exit(1)
os.system('touch BUSY')

os.system('mkdir -p inserted')

# get the start time of this script
starttime=time.time()

files=glob.glob('D20*')

# bail out if no files are found
if (not files):
# print 'nothing to send!'
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

# time out after 4.5 minutes,  this cron tab is scheduled for 5 min (paranoid check)
if ( (time.time() - starttime) > 270):
  os.remove('BUSY')
  sys.exit(1)

# create a compressed tar file named after the first file in the archive
tarfile=files[0]+'.tar.bz2'
tarcmd='tar -cjf '+tarfile
for file in files:
# print 'send file:', file, os.stat(file)[stat.ST_SIZE]
  tarcmd=tarcmd+' '+file
os.system(tarcmd)

# keep trying to sent the tar file until we run out of time
while True:
  try:
#   print 'opening FTP connection'

    # send the tar file to the ground
    ftp = ftplib.FTP('eol-rt-data.guest.ucar.edu')
    ftp.login('ads', 'blue;spruce')
    ftp.cwd('avaps')
    ftp.cwd('nrlp3')

#   print 'sending', tarfile, '...'

    # the following is equivalent to: 'put my_local_file.foo destination_file'
    ftp.storbinary('stor '+tarfile, open(tarfile, 'r'))
#   print 'ftp put successful'

    # move the sent files to a seperate folder
    os.remove(tarfile)
    for file in files:
      os.rename(file, 'inserted/'+file)
    break

  except ftplib.all_errors, e:
#   print 'Error putting file: ', e

    # time out after 4.5 minutes,  this cron tab is scheduled for 5 min
    if ( (time.time() - starttime) > 270):

      # well try this again sometime
#     print 'running out of time... give up'
      os.remove(tarfile)
      os.remove('BUSY')
      sys.exit(1)

#   print 'try again'

ftp.quit() 

# remove busy flag
os.remove('BUSY')

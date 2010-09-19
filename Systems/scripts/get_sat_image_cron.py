#!/usr/bin/python
#
# This script attempts to get the latest satellite image from the ground.
#  It does so by getting a listing of available files, and finding the most recent
#  file.  It then compares the file name with the latest gotten file name stored
#  in the db and if it's different, it pulls the file and stores its name in the DB.
#
#  NOTE:  this script assumes that latest image will be lexographically greater than all
#         previous images.
#
# This is set up to run out of a cron job every N minutes
# N * * * * /home/local/Systems/scripts/get_sat_image.cron.py
#
#  TODO:  replace all prints with syslog.syslog()
#	  set up to take arguments:
#             Image type (IR, VIS, lightning, radar, etc)
#             filename convention on ftp site (e.g. ir_image_*.jpg)
#             "latest" name on acserver (e.g. latest_ira.jpg)
#

import os
import sys
import glob
import ftplib
import syslog
import time
from pg import DB

print "Starting get_sat_image_cron.py for getting IR imagery"

gmt=time.gmtime()
year=gmt[0]
month=gmt[1]
yesterday=gmt[2]-1
today=gmt[2]
tomorrow=gmt[3]+1

#override real date stuff for now - numbers to strings in python needed.
year='2010'
month='09'
yesterday='13'
today='14'
tomorrow='15'

os.chdir('/var/www/html/flight_data/images/')
#os.chdir('/tmp/')

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile('BUSY_IR'):
    print 'exiting, BUSY_IR'
    sys.exit(1)
os.system('touch BUSY_IR')

cnx = DB('real-time')

# Get current IR image name from database
try:
    # Validate that images table exists in database
    images = cnx.query("SELECT * from images")
except :
    print "error accessing images table - assume it doesn't exist"
    print "create table"
    cnx.query("""CREATE TABLE images (type varchar(80), name varchar(80))""")

# Get current IR image name from database
try:
    # Validate that images table exists in database
    image = cnx.query("SELECT name from images where type = 'IR'")
    imagelist=image.getresult()
    imageitem=imagelist[0]
    imagename=imageitem[0]

except :
    print "could not get latest IR image from images table"
    imagename = ""

# Get list of current images from ftp site
#form = "ops.goes-13."+year+month+day+"*"
try:
    print 'opening FTP connection '

    ftp = ftplib.FTP('data.eol.ucar.edu')
    ftp.login('anonymous', '')
    ftp.cwd('/pub/incoming/predict/mc_sat/')

    ftplist = []
    form="ops.goes-13." + year + month + yesterday + "*"
    ftp.dir(form, ftplist.append)
    form="ops.goes-13." + year + month + today + "*"
    ftp.dir(form, ftplist.append)
    form="ops.goes-13." + year + month + tomorrow + "*"
    ftp.dir(form, ftplist.append)

except ftplib.all_errors, e:
    print 'Error Getting ftp listing'
    os.remove('BUSY_IR')
    ftp.quit()
    sys.exit(1)

print "list of files"
filelist = []
for line in ftplist:
    linelist = line.split()
    filelist.append(linelist[len(linelist)-1])

print filelist
latest = filelist[len(filelist)-1]
print "last file on ftp site is: " + latest
print "database file is:" +  imagename

# Check to see if we've got the most recent file
if latest == imagename:
    print "Already have file" + latest
    os.remove('BUSY_IR')
    ftp.quit()
    sys.exit(1)

print "Don't have most recent file"

# Get the latest image 

try:
    command = "wget ftp://data.eol.ucar.edu:/pub/incoming/predict/mc_sat/"+latest
    os.system(command)
    print 'file retrieved'
    command = "cp "+latest+" latest_ir.jpg"
    os.system(command)

except:
    print "problems getting file, exiting"
    os.remove('BUSY_IR')
    ftp.quit()
    sys.exit(1)

#try:
#    print 'opening FTP connection for '+ latest
#
#    ftp = ftplib.FTP('data.eol.ucar.edu')
#    ftp.login('anonymous', '')
#    ftp.cwd('/pub/incoming/predict/mc_sat/')
#
#    file = open(latest)
#    ftp.retrbinary("RETR " + latest, file.write)
#    file.close
#    print 'file retrieved'
#
#except ftplib.all_errors, e:
#    print 'Error getting file:' + e
#
#    os.remove('BUSY_IR')
#    ftp.quit()
#    sys.exit(1)

# Update the entry in the images table
try:
    # Validate that images table exists in database
    cnx.query("DELETE from images where type = 'IR'")
    qstring = "INSERT INTO images VALUES ( 'IR', '"+latest+"')"
    cnx.query(qstring)

except :
    print "error updating images table - bummer situation!"

os.remove('BUSY_IR')
ftp.quit() 
sys.exit(1)

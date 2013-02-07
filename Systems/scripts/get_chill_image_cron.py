#!/usr/bin/python
#
# This script attempts to get the latest CHILL radar image(s) from the ground.
# We need to only obtain this data if the Region is Colorado so check the DB for that.
# 
#  It does so by getting a listing of available files, and finding the most 
#  recent file.  It then compares the file name with the most recently obtained
#  file from a listing and if it's different, it pulls the ground file.
#  It does no backfill.
#
#  NOTE:  this script assumes that most recent image will be lexographically 
#  greater than all other images.
#
# This is set up to run out of a cron job every N minutes
# N * * * * /home/local/Systems/scripts/get_chill_image.cron.py
#
#  TODO:  
#         Refactor into python modules for better coding practice
#         replace all prints with syslog.syslog()
#	  set up to take arguments:
#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2010-2012
#

import os
import sys
import glob
import ftplib
import syslog
import time
import datetime
import pg 

# Initialization based on environment variables
try:
    air_tail = os.environ['AIRCRAFT']
except:
    print "AIRCRAFT envirnment variable not defined - exit!"
    sys.exit()

aircraft = air_tail.split('_')[0]

try: 
    database = os.environ['PGDATABASE']
except:
    database = "real-time"

try: 
    dbhost = os.environ['PGHOST']
except:
    dbhost = "localhost"

# Initialization 
#  *******************  Modify The Following *********************
local_image_dir  = '/var/www/html/flight_data/images/'
image_type       = 'chill_radar'
busy_file        = local_image_dir+'BUSY_'+image_type
ftp_site         = 'catalog1.eol.ucar.edu'
ftp_login        = 'anonymous'
ftp_passwd       = ''
ftp_dir          = '/pub/incoming/OSM/'+aircraft+'/'
#Assumes filename form is prefix.YYYYMMDDHHMM.postfix
prefix           = 'research.CHILL.'
postfix		 = '.DBZ.png' 
osm_file_name    = "latest_chill.DBZ.png"
min_of_imgs      = 10

# End of Initialization section

print "Starting get_chill_image.py for getting " + image_type + " imagery"

# Get Region information from the database
con = pg.connect(dbname=database, host=dbhost, user='ads')
querres = con.query("select value from global_attributes where key='region'")
regionlst = querres.getresult()
if len(regionlst) == 0:
    print "Database has not been initialized by MC for region, etc."
    print "Must Exit!"
    # TODO need a nagios call here to alert operator 
    con.close()
    if os.path.isfile(busy_file):
        os.remove(busy_file)
    sys.exit(1)
region = (regionlst[0])[0]
con.close()

# Only get data if the region is Colorado
if region != 'CO':
     sys.exit(1)

# Change directory to the right place
os.chdir(local_image_dir)

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile(busy_file):
    print 'exiting, ' + busy_file + ' exists.  Already running.'
    sys.exit(1)
cmd = 'touch ' + busy_file
os.system(cmd)

# create portion of filename based on date/time
timesecs = []
curtimesecs=time.time()
timesecs.append(curtimesecs-(min_of_imgs*60))
timesecs.append(curtimesecs)

timestr = []

for x in timesecs:
    gmt = time.gmtime(x)
    year=gmt[0]
    month=gmt[1]
    day=gmt[2]
    hour=gmt[3]
    min_ten=(int(gmt[4]/10))
    if month<10:
        monthstr = "0"+str(month)
    else:
        monthstr = str(month)
    if day<10:
        daystr = "0" + str(day)
    else:
        daystr = str(day)
    if hour<10:
        hourstr = "0" + str(hour)
    else:
        hourstr = str(hour)
    timestr.append(str(year)+monthstr+daystr+hourstr+str(min_ten)+"*")


#  Get the listing of image files from the directory
listing=os.listdir('.')

# Get list of current images from ftp site
#  TODO: use ftp.nlst to reduce size of listing significantly
try:
    print 'opening FTP connection '

    ftp = ftplib.FTP(ftp_site)
    ftp.login(ftp_login, ftp_passwd)
    ftp.cwd(ftp_dir)

    ftplist = []
    for ts in timestr:
        form=prefix + ts + postfix
        print "looking for files on ftp server: " + form
        templist = ftp.nlst(form)
        if len(templist) > 0:
            for i in templist:
                print i
                ftplist.append(i)

    print "ftplist:"
    print ftplist

except ftplib.all_errors, e:
    print 'Error Getting ftp listing'
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

if len(ftplist) == 0:  # didn't get any file names, bail out
    print "didn't find any files on ftp server with form: " 
    print prefix + "+"
    print timestr 
    print "+" + postfix
 
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

print "Size of the ftp listing: " + str(len(ftplist))
#print ftplist

latest = ftplist[len(ftplist)-1]
print "last file on ftp site is: " + latest

# Check to see if we've got the most recent file
if latest in listing:
    print "Already have file" + latest
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

# Get the latest image 
try:
    command = "wget ftp://"+ftp_site+":"+ftp_dir+latest
    os.system(command)
    print 'file retrieved: '+latest
    print 'setting it as overlay image for OSM.'
    command = "cp "+latest+" "+osm_file_name
    os.system(command)

except:
    print "problems getting file, exiting."
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

print "Done."
os.remove(busy_file)
ftp.quit() 
sys.exit(1)

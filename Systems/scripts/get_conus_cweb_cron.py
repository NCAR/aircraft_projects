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
image_type       = 'conus_cweb'
busy_file        = local_image_dir+'BUSY_'+image_type
ftp_site         = 'www.eol.ucar.edu'
ftp_login        = 'anonymous'
ftp_passwd       = ''
ftp_dir          = '/flight_data/display/'
filename         = 'conus_radar.png'
tempfilename     = 'temp_conus_radar.png'

# End of Initialization section

print "Starting get_conus_cweb.py for getting " + image_type + " imagery"

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile(busy_file):
    print 'exiting, ' + busy_file + ' exists.  Already running.'
    sys.exit(1)
cmd = 'touch ' + busy_file
os.system(cmd)

# Get Region information from the database
# Turns out for nexrad, we don't care about region
con = pg.connect(dbname=database, host=dbhost, user='ads')
#querres = con.query("select value from global_attributes where key='region'")
#regionlst = querres.getresult()
#if len(regionlst) == 0:
#    print "Database has not been initialized by MC for region, etc."
#    print "Must Exit!"
#    # TODO need a nagios call here to alert operator 
#    con.close()
#    os.remove(busy_file)
#    sys.exit(1)
#region = (regionlst[0])[0]

# Get delay indication from the database if not off, then check time of most recent image
#  and if enough time has passed, continue, else quit.
#querres = con.query("select value from global_attributes where key='cappi'")
#cappilst = querres.getresult()
#if len(cappilst) == 0:
#    print "Database has not been initialized by MC for region etc."
#    print "Must Exit!"
#    # TODO need a nagios call here to alert operator 
#    con.close()
#    os.remove(busy_file)
#    sys.exit(1)
#cappi = (cappilst[0])[0]
#if cappi == 'off':
#    print "MC has turned cappi acquisition off"
#    con.close()
#    os.remove(busy_file)
#    sys.exit(1)
#con.close()

# Change directory to the right place
os.chdir(local_image_dir)

# create portion of filename based on date/time
timesecs = []
curtimesecs=time.time()
timesecs.append(curtimesecs)

timestr = []

for x in timesecs:
    gmt = time.gmtime(x)
    year=gmt[0]
    month=gmt[1]
    day=gmt[2]
    hour=gmt[3]
    min_ten=gmt[4]
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
    timestr.append(str(year)+monthstr+daystr+hourstr+str(min_ten))


# Get the latest image 
try:
    command = "wget http://"+ftp_site+":"+ftp_dir+filename + " -O " + tempfilename
    os.system(command)
    print 'file retrieved: '+tempfilename
    command = "mv "+tempfilename+" "+filename
    print "Command: " + command
    os.system(command)
    command = "cp "+filename +" NEXRAD.conus." + timestr[0] + ".png"
    print 'Copying it to loop: ' + command
    os.system(command)

except:
    print "problems getting file, exiting."
    os.remove(busy_file)
    sys.exit(1)

print "Done."
os.remove(busy_file)
sys.exit(1)

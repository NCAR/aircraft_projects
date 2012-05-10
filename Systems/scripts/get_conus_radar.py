#!/usr/bin/python
#
# This script attempts to get the latest conus radar image from the national
#  weather service and convert it to a form usable by the OSM system.
#
# Since the image is big and costly to bring to the aircraft, make sure that
#  the Mission Coordinator has asked for it.
#
# This is set up to run out of a cron job every 10 minutes
#  which appears to be the frequency that they update it.
# 10 * * * * /home/local/Systems/scripts/get_sat_image.cron.py
#
#  TODO:  
#         Refactor into python modules for better coding practice
#         replace all prints with syslog.syslog()
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
image_type       = 'conus_radar'
busy_file        = local_image_dir+'BUSY_'+image_type
#Assumes filename form is prefix.YYYYMMDDHHMM.ALTSTRING_postfix
http_site        = 'http://radar.weather.gov'
http_dir         = '/ridge/Conus/RadarImg/'
http_gifname     = 'latest_radaronly.gif'
http_gfwname     = 'latest_radaronly.gfw'


# End of Initialization section

print "Starting get_conus_radar.py for getting " + image_type + " imagery"

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile(busy_file):
    print 'exiting, ' + busy_file + ' exists.  Already running.'
    sys.exit(1)
cmd = 'touch ' + busy_file
os.system(cmd)

# Do our DB stuff
con = pg.connect(dbname=database, host=dbhost, user='ads')

# Get delay indication from the database if not off, then check time of most recent image
#  and if enough time has passed, continue, else quit.
# NOTE: right now we're using the cappi indicator for both cappi and conus radar
#   may wish to separate these out.
querres = con.query("select value from global_attributes where key='cappi'")
cappilst = querres.getresult()
if len(cappilst) == 0:
    print "Database has not been initialized by MC for region etc."
    print "Must Exit!"
    # TODO need a nagios call here to alert operator 
    con.close()
    os.remove(busy_file)
    sys.exit(1)
cappi = (cappilst[0])[0]
if cappi == 'off':
    print "MC has turned cappi/conus radar acquisition off"
    con.close()
    os.remove(busy_file)
    sys.exit(1)
# There is no CAPPI imagery over Colorado - why bother?
querres = con.query("select value from global_attributes where key='region'")
regionlst = querres.getresult()
if len(regionlst) == 0:
    print "Database has not been initialized by MC for region."
    print "Must Exit!"
    # TODO need a nagios call here to alert operator 
    con.close()
    sys.exit(1)
region = (regionlst[0])[0]

#Done with our DB stuff
con.close()

os.chdir(local_image_dir)

#  Now we need to warp the image to the right projection
print "Getting the tmp_radar.gif from the Weather Service"
command = "/usr/bin/curl " + http_site + http_dir + http_gifname + " -o /tmp/tmp_radar.gif"
print command
os.system(command)
command = "/usr/bin/curl " + http_site + http_dir + http_gfwname + " -o /tmp/tmp_radar.gfw"
print command
os.system(command)
# convert latest conus radar from rectangular to sm
command = "/usr/bin/gdalwarp -rcs -s_srs '+proj=longlat +ellps=clrk80 +no_defs' -t_srs '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs' /tmp/tmp_radar.gif /tmp/tmp_radar.tiff"
print command
os.system(command)
# convert to png, and add transparency back in
command = "/usr/bin/convert /tmp/tmp_radar.tiff -transparent white /tmp/tmp_radar.png"
print command
os.system(command)

# copy to webdir and cleanup.
command = "/bin/cp /tmp/tmp_radar.png /var/www/html/flight_data/images/conus_radar.png"
print command
os.system(command)
#command = "/bin/rm -f /tmp/tmp_radar.{gif,tiff,png}"
#rint command
#os.system(command)


#***********************************************************************
# Radar images are huge!  Don't backfill!
#**********************************************************************

print "Done."
os.remove(busy_file)
sys.exit(1)

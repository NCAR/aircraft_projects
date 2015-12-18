#!/usr/bin/python
#
# This script attempts to get the latest South East Asia satellite image 
# from the Japanese Meteorological Agency site.
#  It does so by checking the most recently obtained image for date/time
#  incrementing by one hour and trying a wget of the associated image.
#  If it fails to find the next image, it exits, otherwise if it is
#  successful in pulling the image, it crops it to the area of interest for
#  CONTRAST rf14 and puts a copy of it in place for use by the mission 
#  coordinator software.
#
# This is set up to run out of a cron job every N minutes
# N * * * * /home/local/Systems/scripts/get_sat_image.cron.py
#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2010-2014
#

import os
import sys
import glob
import ftplib
import syslog
import time
import datetime

# Initialization - change this for different file types/names/locations.
# Plane
#local_image_dir  = '/var/www/html/flight_data/GV/images/'
# Ground
local_image_dir  = '/net/www/docs/flight_data/GV/images/'
image_type       = 'SEAIR'
busy_file        = 'BUSY_'+image_type
http_dir        =  'www.jma.go.jp/en/gms/imgs/4/infrared/0/'
label            = 'sat_sea_ir_label.jpg'
#Assumes filename form is prefixYYYYMMDD*postfix
prefix           = ''  
postfix		 = '.png' 
osm_file_name    = "latest_sea_irj.jpg"
num_imgs_to_get  = 10 # Script will backfill this many images for loops
# End of Initialization section


print "Starting get_sea_ir_image_cron.py for getting " + image_type + " imagery"

gmt=time.gmtime()

year=gmt[0]
month=gmt[1]
yesterday=gmt[2]-1
today=gmt[2]
tomorrow=gmt[2]+1
if month<10:
    monthstr = "0"+str(month)
else:
    monthstr = str(month)
if yesterday<10:
    yesterdaystr = "0" + str(yesterday)
else:
    yesterdaystr = str(yesterday)
if today<10:
    todaystr = "0" + str(today)
else:
    todaystr = str(today)
if tomorrow<10:
    tomorrowstr = "0" + str(tomorrow)
else:
    tomorrowstr = str(tomorrow)

hour=gmt[3]
if hour<10:
    hourstr = "0"+str(hour)
else:
    hourstr = str(hour)
prevhour = hour - 1

print monthstr+"/"+todaystr+"/"+str(year)+" "+str(gmt[3])+":"+str(gmt[4])

os.chdir(local_image_dir)

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile(busy_file):
    print 'exiting, ' + busy_file + ' exists.  Already running.'
    sys.exit(1)
cmd = 'touch ' + busy_file
os.system(cmd)

#  Get the listing of image files from the directory
listing=os.listdir('.')

# Create latest image name given what we know of web site form
#  i.e.  yyyymmddhh00-00.png
latest = str(year)+monthstr+todaystr+hourstr+"00-00.png"
previous = str(year)+monthstr+todaystr+str(prevhour)+"00-00.png"

# Check to see if we've got the most recent file
if latest in listing:
    print "Already have file: " + latest
    os.remove(busy_file)
    sys.exit(1)

# Get the latest image 
try:
    command = "wget  "+http_dir+latest
    os.system(command)
    print 'file retrieved: '+latest

except:
    print "problems getting file, exiting."
    os.remove(busy_file)
    sys.exit(1)

try: 
    print "Cropping image to OSM size"
# Plane:
#    command = "convert "+latest+" -crop 400x400+150+200 "+osm_file_name
# Ground
    command = "convert "+latest+" -crop 400x400+150+150 "+osm_file_name
    print "Using command: "+command
    os.system(command)

except:
    print "problem cropping file, exiting."
    os.remove(busy_file)
    sys.exit(1)

#*****************************************************************
#   Bailing out here now
#*****************************************************************

# Ground only
os.remove(previous)
os.remove(busy_file)
sys.exit(1)


#TODO: get earlier images?
# Make sure that we're not missing any earlier images say 10 images worth
print 'Checking on images earlier in time.'
got_old='false'
i=2
filename=filelist[len(filelist)-i]
while i<num_imgs_to_get:
    if filename not in listing:
        print "Don't have earlier image:"+filename
        try:
            command = "wget ftp://"+ftp_site+":"+ftp_dir+filename
            os.system(command)
            print 'file retrieved: '+filename
            got_old='true'

        except:
            print "problems getting file, exiting"
            os.remove(busy_file)
            ftp.quit()
            sys.exit(1)
    i = i+1
    filename=filelist[len(filelist)-i]

# If we got an older image it's date/time will be out of sequence for 
# time series veiwing (which is done based on date/time of file) so we need
# to correct for that by touching the files based on time sequence.
if got_old == 'true':
    print 'cleaning up dates of image files'
    listing=glob.glob(prefix+'*')
    i = 0
    while i < len(listing):
        dt = listing[i].split('.')
        os.system('touch -t '+dt[2]+' '+listing[i])
        i = i + 1


print "Done."
os.remove(busy_file)
ftp.quit() 
sys.exit(1)

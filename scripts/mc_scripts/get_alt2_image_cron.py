#!/usr/bin/python
#
# This script attempts to get the latest satellite image from the ground.
#  It does so by getting a listing of available files, and finding the most
#  recent file.  It then compares the file name with the latest gotten file
#  name stored in the db and if it's different, it pulls the file and stores
#  its name in the DB.  It also checks the listing of files on the plane
#  in case the DB somehow got a name for which the file was not pulled.  Finally
#  it compares the ground listing with the plane listing and if any files
#  exist on the ground, but not on the plane, it pulls those.
#
#  NOTE:  this script assumes that most recent image will be lexographically
#  greater than all other images.
#
# This is set up to run out of a cron job every N minutes
# N * * * * /home/local/Systems/scripts/get_alt_image.cron.py
#
#  TODO:
#         Refactor into python modules for better coding practice
#         replace all prints with syslog.syslog()
#	  set up to take arguments:
#             Image type (IR, VIS, lightning, radar, etc)
#             filename convention on ftp site (e.g. ir_image_*.jpg)
#             "latest" name on acserver (e.g. latest_ira.jpg)
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
import re

# Get information from AIRCRAFT environment variable
try:
    aircraft = os.environ['AIRCRAFT']
except:
    print "AIRCRAFT environment variable not defined - exit!"
    sys.exit()

plane,tail = aircraft.split("_",1)

# Initialization - change this for different file types/names/locations.
local_image_dir  = '/var/www/html/flight_data/images/'
image_type       = 'ALT2'
busy_file        = 'BUSY_'+image_type
ftp_site         = 'catalog.eol.ucar.edu'
ftp_login        = 'anonymous'
ftp_passwd       = ''
ftp_dir          = '/pub/incoming/OSM/'+plane+'/'
#Assumes filename form is prefixYYYYMMDD*postfix
prefix           = 'alternate.satellite2.'
postfix      = '.jpg'
osm_file_name    = "alternate.satellite2.jpg"

num_imgs_to_get  = 10 # Script will backfill this many images for loops
# End of Initialization section
print "Starting " + __file__ + " for getting " + image_type + " imagery"

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

# Get list of current images from ftp site
print 'opening FTP connection'
try:
    ftp = ftplib.FTP(ftp_site)
except:
    print 'Error Connecting to ftp server: ' + ftp_site
    os.remove(busy_file)
    sys.exit(1)

try:
    ftp.login(ftp_login, ftp_passwd)
    ftp.cwd(ftp_dir)

    ftplist = []
    formy=prefix + str(year) + monthstr + yesterdaystr + "[0-9][0-9][0-9][0-9]*" + postfix
    ftp.dir(formy, ftplist.append)
    formt=prefix + str(year) + monthstr + todaystr + "[0-9][0-9][0-9][0-9]*" + postfix
    ftp.dir(formt, ftplist.append)
    formtm=prefix + str(year) + monthstr + tomorrowstr + "[0-9][0-9][0-9][0-9]*" + postfix
    ftp.dir(formtm, ftplist.append)

except ftplib.all_errors, e:
    print 'Error Getting ftp listing'
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

if len(ftplist) == 0:  # didn't get any file names, bail out
    print "didn't find any files on ftp server with form: " +formy
    print "didn't find any files on ftp server with form: " +formt
    print "didn't find any files on ftp server with form: " +formtm
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

print "Size of the ftp listing: " + str(len(ftplist))
filelist = []
for line in ftplist:
    linelist = line.split()
    filelist.append(linelist[len(linelist)-1])

latest = filelist[len(filelist)-1]
print "last file on ftp site is: " + latest

# Check to see if we've got the most recent file
if latest in listing:
  print "Already have file: " + latest
#    os.remove(busy_file)
else:
# Get the latest image and its label
  try:
    command = "wget ftp://"+ftp_site+":"+ftp_dir+latest
    os.system(command)
    print 'file retrieved: '+latest
    print 'setting it as overlay image for OSM.'
    command = "cp "+latest+" "+osm_file_name
    os.system(command)
    # Using make_label.py now.
    #    command = "wget ftp://"+ftp_site+":"+ftp_dir+label+" -O " + label
    #    os.system(command)
    #    print 'obtained image label: '+label

    #
    # copy to CatalogIngest
    #
    catalog_ingest_dir = '/home/catalog/products/incoming/' + plane.lower()
    if os.path.isdir(catalog_ingest_dir):
        #
        # munge filename into catalog-friendly form:
        #     satellite.alt-satellite-2.<datetime>.composite-2.jpg
        # get datetime from regex: (\d{12})
        #
        regex_string = re.escape(prefix) + '(\d{12})' + re.escape(postfix)
        match = re.match(regex_string, latest)

        if match:
            dest_file = catalog_ingest_dir+"/satellite.alt-satellite-2." + match.group(1) + ".composite-2.jpg"
            command = "cp "+latest+" "+dest_file
            os.system(command)

  except:
    print "problems getting file, exiting."
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

# Make sure that we're not missing any earlier images say 10 images worth
print 'Checking on images earlier in time.'
got_old='false'
i=2
filename=filelist[len(filelist)-i]
num_imgs_to_get = min(num_imgs_to_get, len(filelist))
while i<num_imgs_to_get:
    if filename not in listing:
        print "Don't have earlier image: "+filename
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

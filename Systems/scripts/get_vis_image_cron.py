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
# N * * * * /home/local/Systems/scripts/get_sat_image.cron.py
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
import pg

# Get information from AIRCRAFT environment variable
try:
    aircraft = os.environ['AIRCRAFT']
except:
    print "AIRCRAFT envirnment variable not defined - exit!"
    sys.exit()

plane,tail = aircraft.split("_",1)

try: 
    database = os.environ['PGDATABASE']
except:
    database = "real-time"

try: 
    dbhost = os.environ['PGHOST']
except:
    dbhost = "localhost"

# Initialization - change this for different file types/names/locations.
local_image_dir  = '/var/www/html/flight_data/images/'
image_type       = 'vis'
busy_file        = 'BUSY_'+image_type
ftp_site         = 'catalog1.eol.ucar.edu'
ftp_login        = 'anonymous'
ftp_passwd       = ''
#ftp_dir          = '/pub/incoming/OSM/C130/'
ftp_dir          = '/pub/incoming/OSM/'+plane+'/'
#Assumes filename form is prefixYYYYMMDD*.region_postfix where region is drawn from DB
prefix           = 'ops.goes-13.'  
postfix		 = '1km_ch1_vis.jpg' 
osm_label            = 'sat_vis_label.jpg'
#osm_file_name    = "latest_vis.jpg"  # NOTE: defined once we have region name
num_imgs_to_get  = 10 # Script will backfill this many images for loops
# End of Initialization section

print "Starting get_vis_image_cron.py for getting " + image_type + " imagery"

os.chdir(local_image_dir)

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile(busy_file):
    print 'exiting, ' + local_image_dir + busy_file + ' exists.  Already running.'
    sys.exit(1)
cmd = 'touch ' + busy_file
os.system(cmd)

# Set up time strings
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


# Get Region information from the database
con = pg.connect(dbname=database, host=dbhost, user='ads')
querres = con.query("select value from global_attributes where key='region'")
regionlst = querres.getresult()
if len(regionlst) == 0:
    print "Database has not been initialized by MC for region, etc."
    print "Must Exit!"
    # TODO need a nagios call here to alert operator 
    con.close()
    os.remove(busy_file)
    sys.exit(1)
region = (regionlst[0])[0]
con.close()

if region=='off':
    print "Mission Coordinator has left region selection to off."
    print "Exiting"
    sys.exit(1)

#  Define the latest filename and label filename
osm_file_name = "latest_" + region + "_vis.jpg"
label_name = "sat_vis_label_" + region + ".jpg"

#  Get the listing of image files from the directory
listing=os.listdir('.')

# Get list of current images from ftp site
try:
    print 'opening FTP connection '

    ftp = ftplib.FTP(ftp_site)
    ftp.login(ftp_login, ftp_passwd)
    ftp.cwd(ftp_dir)

    ftplist = []
    form=prefix + str(year) + monthstr + yesterdaystr + "*" + region + "_" + postfix
    print "form1 = "+form
    ftp.dir(form, ftplist.append)
    form=prefix + str(year) + monthstr + todaystr + "*" + region + "_" + postfix
    print "form1 = "+form
    ftp.dir(form, ftplist.append)
    form=prefix + str(year) + monthstr + tomorrowstr + "*" + region + "_" + postfix
    print "form1 = "+form
    ftp.dir(form, ftplist.append)

except ftplib.all_errors, e:
    print 'Error Getting ftp listing'
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

if len(ftplist) == 0:  # didn't get any file names, bail out
    print "didn't find any files on ftp server with form: " +prefix+str(year)+monthstr+"{"+yesterdaystr+"|"+todaystr+"|"+tomorrowstr+"}*"+postfix
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
    print "Already have file" + latest
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

# Get the latest image and label
try:
    command = "wget ftp://"+ftp_site+":"+ftp_dir+latest
    os.system(command)
    print 'file retrieved: '+latest
    print 'setting it as overlay image for OSM.'
    command = "cp "+latest+" "+osm_file_name
    os.system(command)
    command = "wget ftp://"+ftp_site+":"+ftp_dir+label_name + " -O " + label_name
    os.system(command)
    print 'obtained image label: '+label_name
    command = "rm " + osm_label
    os.system(command)
    command = "ln -s " + label_name + " " + osm_label
    os.system(command)

except:
    print "problems getting file, exiting."
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

# Make sure that we're not missing any earlier images say 5 hours worth
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

#!/usr/bin/python
#
# This script attempts to get the latest radar image(s) from the ground.
#  Lightning data will be grouped according to the region of the 
#  detector network and images will be generated for elevation ranges.
#  Therefore we will need to determine the elevation of the aircraft from 
#  the database, and we must know the region (which will be encoded in the
#  filename we're ftping from the ground).  
# 
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
image_type       = 'radar_at_level'
busy_file        = local_image_dir+'BUSY_'+image_type
ftp_site         = 'catalog1.eol.ucar.edu'
ftp_login        = 'anonymous'
ftp_passwd       = ''
ftp_dir          = '/pub/incoming/OSM/'+aircraft+'/'
#Assumes filename form is prefix.YYYYMMDDHHMM.ALTSTRING_postfix
prefix           = 'radar.NEXRAD_3D_mosaic_map.'
postfix		 = '_CAPPI.png' 
osm_file_name    = "latest_radar_at_elev.png"
min_of_imgs	 = 10 # Script will backfill this many minutes for loops
num_imgs_to_get  = 10 # Script will backfill this many images for loops

# End of Initialization section

print "Starting get_radar_at_elev_cron.py for getting " + image_type + " imagery"

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
    print "MC has turned cappi acquisition off"
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

# Get Pressure Altitude from the database
querres = con.query("select value from global_attributes where key='EndTime'")
fultimlst = querres.getresult()
fultim = (fultimlst[0])[0]
endtim = fultim.split('.')[0]
querstr = "select paltf from raf_lrt where datetime='"+endtim+"'"
querres = con.query(querstr)
paltflst = querres.getresult()
paltfstr = (paltflst[0])[0]
paltf = float(paltfstr)

#Done with our DB stuff
con.close()

# Create portion of filename based on paltf 
# note: assumes that files are at 06,12,18,24,30,36,42 and 48 K ft
if paltf<9000:
    altstr = "06kft"
elif paltf<15000:
    altstr = "12kft"
elif paltf<21000:
    altstr = "18kft"
elif paltf<27000:
    altstr = "24kft"
elif paltf<33000:
    altstr = "30kft"
elif paltf<39000:
    altstr = "36kft"
elif paltf<45000:
    altstr = "42kft"
elif paltf<51000:
    altstr = "48kft"
else: 
    altstr = "54kft"

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

os.chdir(local_image_dir)

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
        form=prefix + ts + altstr + postfix
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
    print "didn't find any files on ftp server with forms: " 
    print prefix+"+"
    print timestr
    print "+"+altstr+postfix
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

print "Size of the ftp listing: " + str(len(ftplist))
#print ftplist

#filelist = []
#for line in ftplist:
#    linelist = line.it()
#    filelist.append(linelist[len(linelist)-1])

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
    command = "wget ftp://"+ftp_site+":"+ftp_dir+latest+" -O /tmp/latest_radar_at_elev_from_ground.png"
    print command
    os.system(command)
    print 'file retrieved: '+latest

except:
    print "problems getting file, exiting."
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)


#  Now we need to warp the image to the right projection
print "doing the warping"
command = "gdal_translate -a_ullr -112.074 45 -74.4591 28 /tmp/latest_radar_at_elev_from_ground.png /tmp/cappi.gtiff"
print command
os.system(command)
command = "gdalwarp -t_srs '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs' /tmp/cappi.gtiff /tmp/cappi_warped.gtiff"
print command
os.system(command)
command = "gdal_translate -of png /tmp/cappi_warped.gtiff /tmp/cappi_final.png"
print command
os.system(command)
command = "cp /tmp/cappi_final.png " + latest
print command
os.system(command)
print 'setting it as overlay image for OSM.'
command = "cp "+latest+" "+osm_file_name
os.system(command)



#***********************************************************************
# CAPPI images are huge!  Don't backfill!
#**********************************************************************
# Make sure we've got the num_imgs_to_get most recent images
#print 'Checking on images earlier in time.'
#got_old='false'
#i=2
#filename=ftplist[len(ftplist)-i]
#while i<num_imgs_to_get and i<len(ftplist):
#    if filename not in listing:
#        print "Don't have earlier image:"+filename
#        try:
#            command = "wget ftp://"+ftp_site+":"+ftp_dir+filename
#            os.system(command)
#            print 'file retrieved: '+filename
#            got_old='true'
#
#        except:
#            print "problems getting file, exiting"
#            os.remove(busy_file)
#            ftp.quit()
#            sys.exit(1)
#    i = i+1
#    filename=ftplist[len(ftplist)-i]

# If we got an older image it's date/time will be out of sequence for 
# time series veiwing (which is done based on date/time of file) so we need
# to correct for that by touching the files based on time sequence.
#if got_old == 'true':
#    print 'cleaning up dates of image files'
#    listing=glob.glob(prefix+'*')
#    i = 0
#    while i < len(listing):
#        dt = listing[i].split('.')
#        os.system('touch -t '+dt[2]+' '+listing[i])
#        i = i + 1
#

print "Done."
os.remove(busy_file)
ftp.quit() 
sys.exit(1)

#!/usr/bin/python
#
# This script attempts to get the latest lightning image(s) from the ground.
#  Lightning data will be grouped according to the region of the 
#  detector network and images will be generated for elevation ranges.
#  Therefore we will need to determine the elevation of the aircraft from 
#  the database,  the region will also be in the database (matching component of filename)
#  and frequency of acquisition will also be in the database (0 = don't, 5 = get them all and 
#  15 means only every 15 minutes) 
# 
#  It does so by getting a listing of available files, and finding the most 
#  recent file.  It then compares the file name with the latest gotten file 
#  name in the directory and if it's different, it pulls the file.
#
#  NOTE:  this script assumes that most recent image will be lexographically 
#  greater than all other images of the same basic naming convention.
#
# This is set up to run out of a cron job every N minutes
# N * * * * /home/local/Systems/scripts/get_ltng_at_elev_cron.py
#
#  TODO:  
#         Refactor into python modules for better coding practice
#         replace all prints with syslog.syslog()
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

# Get Region information from the database
con = pg.connect(dbname=database, host=dbhost, user='ads')
querres = con.query("select value from global_attributes where key='region'")
regionlst = querres.getresult()
region = (regionlst[0])[0]
con.close()

# Initialization 
#  *******************  Modify The Following *********************
local_image_dir     = '/var/www/html/flight_data/images/'
image_type          = 'lghtng'
busy_file           = local_image_dir+'BUSY_'+image_type
ftp_site            = 'catalog1.eol.ucar.edu'
ftp_login           = 'anonymous'
ftp_passwd          = ''
ftp_dir             = '/pub/incoming/OSM/'+aircraft+'/'
#Assumes filename form is prefix.YYYYMMDDHHMM.midfix_ALTSTRING.postfix
prefix              = 'research.' + region + '_' + "LMA."
midfix              = '10minute_'
postfix		    = '.png' 
compositpostfix     = 'composite.png'
levelpostfix        = 'kft.png'
osm_file_name_level = "LMA_"+region+"_COMP.png"
osm_file_name_comp  = "LMA_"+region+"_FLTLEV.png"
min_of_imgs	    = 10 # Script will backfill this many minutes for loops
num_imgs_to_get     = 10 # Script will backfill this many images for loops

# End of Initialization section

print "Starting get_lghtng_at_elev_cron.py for getting " + image_type + " imagery"

# This cron script is not re-entrant, bail out if its still running.
if os.path.isfile(busy_file):
    print 'exiting, ' + busy_file + ' exists.  Already running.'
    sys.exit(1)
cmd = 'touch ' + busy_file
os.system(cmd)

#Do our other DB stuff
con = pg.connect(dbname=database, host=dbhost, user='ads')

# Get delay indication from the database if not off, then check time of most recent image
#  and if enough time has passed, continue, else quit.
querres = con.query("select value from global_attributes where key='cappi'")
cappilst = querres.getresult()
cappi = (cappilst[0])[0]
if cappi == 'off':
    print "MC has turned cappi acquisition off"
    con.close()
    sys.exit(1)

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
#  TODO: use ftp.nlist to reduce size of listing significantly
try:
    print 'opening FTP connection '

    ftp = ftplib.FTP(ftp_site)
    ftp.login(ftp_login, ftp_passwd)
    ftp.cwd(ftp_dir)

    ftplist = []
    for ts in timestr:
        form=prefix + ts + midfix + altstr + postfix
        print "looking for files on ftp server: " + form
        templist = ftp.nlst(form)
        if len(templist) > 0:
            for i in templist:
                ftplist.append(i)
        form=prefix + ts + midfix + compositpostfix
        print "looking for files on ftp server: " + form
        templist = ftp.nlst(form)
        if len(templist) > 0:
            for i in templist:
                ftplist.append(i)

except ftplib.all_errors, e:
    print 'Error Getting ftp listing'
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

if len(ftplist) == 0:  # didn't get any file names, bail out
    print "didn't find any files on ftp server with forms: " 
    print prefix+"+"
    print timestr
    print "+"+midfix+altstr+postfix+" OR"
    print "+"+midfix+altstr+compositpostfix
    os.remove(busy_file)
    ftp.quit()
    sys.exit(1)

print "Size of the ftp listing: " + str(len(ftplist))

#filelist = []
#for line in ftplist:
#    linelist = line.it()
#    filelist.append(linelist[len(linelist)-1])

latestcomp = ""
latestlevel = ""
for filename in ftplist:
    if filename.find('composite') != -1:
        latestcomp = filename
    if filename.find('kft') != -1:
        latestlevel = filename


# Check to see if we've got the most recent composite file
if latestcomp != "":
    print "last composite file on ftp site is: " + latestcomp
    if latestcomp in listing:
        print "Already have file" + latestcomp

    else:
        # Get the latest composite image
        try:
            command = "wget ftp://"+ftp_site+":"+ftp_dir+latestcomp
            os.system(command)
            print 'file retrieved: '+latestcomp
            print 'setting it as overlay image for OSM.'
            command = "cp "+latestcomp+" "+osm_file_name_comp
            os.system(command)
        
        except:
            print "problems getting file, exiting."
            os.remove(busy_file)
            ftp.quit()
            sys.exit(1)
    
# Check to see if we have the most recent at level file
if latestlevel != "":
    print "last flight level file on ftp site is: " + latestlevel
    if latestlevel in listing:
        print "Already have file" + latestlevel
    
    else:
        # Get the latest at flight level image
        try:
            command = "wget ftp://"+ftp_site+":"+ftp_dir+latestlevel
            os.system(command)
            print 'file retrieved: '+latestlevel
            print 'setting it as overlay image for OSM.'
            command = "cp "+latestlevel+" "+osm_file_name_level
            os.system(command)
    
        except:
            print "problems getting file, exiting."
            os.remove(busy_file)
            ftp.quit()
            sys.exit(1)
    

# *****************************************************************
#        NO BACKFILL of DATA for frequent Flight level types!
#******************************************************************
#
# Make sure we've got the num_imgs_to_get most recent images
#print 'Checking on images earlier in time.'
#got_old='false'
#i=2
#filename=filelist[len(filelist)-i]
#while i<num_imgs_to_get:
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
#    filename=filelist[len(filelist)-i]
#
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


print "Done."
ftp.quit() 
os.remove(busy_file)
sys.exit(1)

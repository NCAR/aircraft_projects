#!/usr/bin/python
#
# This script takes a flight number designation and then using it gets raw ads file and
# netCDF file for that flight number (verifying with the user) and does several things:
#  1: runs NC2ASC using the ICART configuraiton and generates a file for NASA
#  2: ftps that file to both the local store and to the ftp site that NASA wants it at
#  3: ftps the netCDF file to the local store where it's supposed to go for discemination to the catalog
#  4: generates the raw serial VCSEL data using a data_dump command
#  5: ftps that VCSEL data to the local store.
#
#

import os
import sys
import glob
import ftplib
import syslog
import time
import datetime
import pg 
import glob

# Get the tf number
flight = raw_input('Input flight designation (e.g. tf01):')
print flight


# Initialization 
#  *******************  Modify The Following *********************
nc_dir    = '/home/data/DC3/'
raw_dir   = '/home/data/Raw_Data/DC3/'
# End of Initialization section

# Get the netCDF and raw ADS files for working with
nclist = glob.glob(nc_dir+'*'+flight+'*.nc')
if nclist.__len__() == 1:
  ncfile = nclist[0]
else:
  print "More than one file found.  Stepping through files, please select the right one"
  ncfile = ''
  i = 0
  while ncfile == '' :
    ans = raw_input(nclist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      ncfile = nclist[i]
    if i < nclist.__len__() - 1: 
      i = i + 1
    else:
      i = 0
rawlist = glob.glob(raw_dir+'*'+flight+'*.ads')
if rawlist.__len__() == 1:
  rawfile = rawlist[0]
else:
  print "More than one file found.  Stepping through files, please select the right one"
  rawfile = ''
  i = 0
  while rawfile == '' :
    ans = raw_input(rawlist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      rawfile = rawlist[i]
    if i < rawlist.__len__() - 1:
      i = i + 1
    else:
      i = 0

print "NetCDF file = "+ncfile
print "Raw ADS file = "+rawfile


# Produce the ICARTT formated file for NASA
nc2ascTemp = '/home/data/DC3_ICARTT_Template'
nc2ascBatch = '/home/data/DC3_ICARTT'

command = "rm -f "++nc2ascBatch
os.system(command)

temp = ncfile.split('.')
icfile = temp[0]
while i < temp.__len__() -1:
  icfile = icfile + '.' + temp[i]
  i = i + 1
icfile = icfile + '.asc'

bf = open(nc2ascBatch, 'wb')
for line in open(nc2ascTemp).readlines():
  if re.match('if=',line):
    newline='if='+ncfile
  elif re.match('of=',line):
    newline='of='+icfile
  else:
    newline=line
  bf.write(newline)  


sys.exit(1)
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

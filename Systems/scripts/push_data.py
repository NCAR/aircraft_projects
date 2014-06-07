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
#import pg 
import glob


# Initialization 
#  *******************  Modify The Following *********************
#  NOTE: assumes that Raw_Data is subdirectory of data_dir + project
project =        'CONTRAST'
data_dir =       '/home/data/'
ftp_site =       'ftp.eol.ucar.edu'
#ftp_site =       '192.168.1.43'
user =           'anonymous'
password =      ''
#password  =      'tbaltzer@ucar.edu'
ftp_data_dir =   '/pub/data/incoming/contrast/'
#ftp_data_dir =   '/FieldStorage/Temporary Items'
ftp_raw_dir  =   '/pub/data/incoming/contrast/Raw_Data/'
#ftp_raw_dir  =   '/FieldStorage/Temporary Items'
local_ftp_site = '192.168.1.43'
local_user     = 'anonymous'
local_password = 'tbaltzer@ucar.edu'
local_ftp_dir  = '/FieldStorage/DataFiles/CONTRAST/GVnc'
#local_ftp_dir  = '/FieldStorage/Temporary Items'
# ******************  End of Modification Section ****************

nc_dir    = data_dir + project + '/'
raw_dir   = data_dir + 'Raw_Data/' + project + '/'

# End of Initialization section

# Get the flight designation
flight = raw_input('Input flight designation (e.g. tf01):')
print flight

# Get the netCDF, kml  and raw ADS files for working with
# First netCDF
nclist = glob.glob(nc_dir+'*'+flight+'*.nc')
if nclist.__len__() == 1:
  ncfile = nclist[0]
elif nclist.__len__() == 0:
  print "No files found matching form: "+nc_dir+'*'+flight+'*.nc'
  print "aborting..."
  sys.exit(0)
else:
  print "More than one netCDF file found."
  print "Stepping through files, please select the right one"
#  print nclist
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
if ncfile == '' : 
  print "No NetCDF file identified!"
  print "Aborting"
  sys.exit(0)

#KML file
kmllist = glob.glob(nc_dir+'*'+flight+'.kml')
if kmllist.__len__() == 1:
  kmlfile = kmllist[0]
elif kmllist.__len__() == 0:
  print "No files found matching form: "+nc_dir+'*'+flight+'*.kml'
  print "aborting..."
  sys.exit(0)
else:
  print "More than one file found.  Stepping through files, please select the right one"
  kmlfile = ''
  i = 0
  while kmlfile == '' :
    ans = raw_input(kmllist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      kmlfile = kmllist[i]
    if i < kmllist.__len__() - 1: 
      i = i + 1
    else:
      i = 0
if kmlfile == '' :
  print "No KML file identified!"
  print "Aborting..."
  sys.exit(0)

#IWG1 file
iwg1list = glob.glob(nc_dir+'*'+flight+'.iwg1')
if iwg1list.__len__() == 1:
  iwg1file = iwg1list[0]
elif iwg1list.__len__() == 0:
  print "No files found matching form: "+nc_dir+'*'+flight+'*.iwg1'
  print "aborting..."
  sys.exit(0)
else:
  print "More than one file found.  Stepping through files, please select the right one"
  iwg1file = ''
  i = 0
  while iwg1file == '' :
    ans = raw_input(iwg1list[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      iwg1file = iwg1list[i]
    if i < iwg1list.__len__() - 1: 
      i = i + 1
    else:
      i = 0
if iwg1file == '' :
  print "No IWG1 file identified!"
  print "Aborting..."
  sys.exit(0)

#Raw Data File
rawlist = glob.glob(raw_dir+'*'+flight+'*.ads')
if rawlist.__len__() == 1:
  rawfile = rawlist[0]
elif rawlist.__len__() == 0:
  print "No Raw files found matching the form: raw_dir+'*'+flight+'*.ads'"
  print "aborting..."
  sys.exit(0)
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
if rawfile == '' :
  print "No Raw file identified!"
  print "Aborting! "
  sys.exit(0)

print "**************************"
print "NetCDF file = "+ncfile
print "KML file = "+kmlfile
print "IWG1 file = "+iwg1file
print "Raw ADS file = "+rawfile
print "**************************"
print ""

# ZIP up the files as per expectations back home
# First the nc file and the kml file go into one zip file (note want the files
#   to exist at the diretory level of the zip file)

data_dir,ncfilename = os.path.split(ncfile)
data_dir,kmlfilename = os.path.split(kmlfile)
data_dir,iwg1filename = os.path.split(iwg1file)
zip_data_filename = project+flight+".zip"
print "data_dir = "+data_dir
print "ncfilename = "+ncfilename
print "kmlfilename = "+kmlfilename
print "iwg1filename = "+iwg1filename
# Make sure that there is not a zip file already there ("overwrite")
command = "cd "+data_dir+"; rm "+project+flight+".zip"
os.system(command)
command = "cd "+data_dir+"; zip " + zip_data_filename + " " + ncfilename + " " + kmlfilename + " " + iwg1filename
print ""
print "Zipping up netCDF and kml files with command:"
print command
os.system(command)

# Now ZiP up the rawfile - again with the file existing at the same directory
#  level as the zip file
raw_dir,rawfilename = os.path.split(rawfile)
zip_raw_filename = rawfilename+".zip"
print "rawfilename = "+rawfilename
# remove zip file if it exists
command = "cd "+raw_dir+"; rm "+rawfilename+".zip"
os.system(command)
command = "cd "+raw_dir+"; zip "+zip_raw_filename+ " " +rawfilename
print ""
print "Zipping up raw data file with command:"
print command
os.system(command)

# Put zipped files to EOL server
try:
    print 'opening FTP connection to: ' + ftp_site

    ftp = ftplib.FTP(ftp_site)
    ftp.login(user, password)
    ftp.cwd(ftp_data_dir)
    print ""
    print "Putting file:"+zip_data_filename
    os.chdir(data_dir)
    file = open(zip_data_filename, 'r')
    ftp.storbinary('STOR ' + zip_data_filename, file)
    file.close()
    print "Finished putting data file"
    print ""
    ftp.quit()

except ftplib.all_errors as e:
    print ""
    print 'Error writing nc/kml data file to eol server'
    print e
    ftp.quit()
    sys.exit(1)

# Put zipped raw files to EOL server
try: 
    print ""
    print 'opening FTP connection to: ' + ftp_site

    ftp = ftplib.FTP(ftp_site)
    ftp.login(user, password)
    ftp.cwd(ftp_raw_dir)
    print "Putting file: "+zip_raw_filename
    os.chdir(raw_dir)
    file = open(zip_raw_filename, 'r')
    ftp.storbinary('STOR ' + zip_raw_filename, file)
    file.close()
    print "Finished putting raw data file"
    print ""
    ftp.quit()

except ftplib.all_errors as e:
    print 'Error writing raw data file to eol server'
    print e
    ftp.quit()
    sys.exit(1)

# Put unzipped data files to field server
try: 
    print ""
    print 'Local Data Store: opening FTP connection to: ' + local_ftp_site

    ftp = ftplib.FTP(local_ftp_site)
    ftp.login(local_user, local_password)
    ftp.cwd(local_ftp_dir)
    print "Putting file: "+ncfilename
    print "from directory: "+data_dir
    os.chdir(data_dir)
    file = open(ncfilename, 'r')
    ftp.storbinary('STOR ' + ncfilename, file)
    file.close()
    print "Putting file: "+kmlfilename
    file = open(kmlfilename, 'r')
    ftp.storbinary('STOR ' + kmlfilename, file)
    file.close()
    print "Done Putting data files to local ftp server"
    print ""
    ftp.quit()

except ftplib.all_errors as e:
    print 'Error writing data file to local ftp server'
    print e
    ftp.quit()
    sys.exit(1)

sys.exit(1)


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

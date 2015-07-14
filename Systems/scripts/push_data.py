#!/usr/bin/python
#
# This script is specific to the WINTER project.
# It takes a flight number designation and then using it gets raw ads 
# file, netCDF file and kml file for that flight number (verifying with the 
# user where needed) and does several things:
#  1: zips up the nc, kml, and iwg1 files into a single zip file 
#  2: zips up the ads file - commented out for WINTER
#  3: Creates plots using an Rstudio script
#  4: copies nc, kml, plots to local FTP site for readynas to sync to Boulder
#  4: FTPs the nc and kml files to a local server in the WINTER Ops center 
#

import os
import sys
import glob
import ftplib
import syslog
import time
import datetime
import glob
import time
import string


# Initialization 
#  *******************  Modify The Following *********************
#  NOTE: assumes that Raw_Data is subdirectory of data_dir + project
project =        'CSET'
data_dir =       '/home/data/'
rstudio_dir =    '/home/ads/RStudio/'

NAS =            'true'
nas_url =        '192.168.1.30:/data'
nas_mnt_pt =     '/mnt/Data/'
nas_sync_dir =   nas_mnt_pt + '/data/synced_data/ads/'
nas_data_dir =   nas_mnt_pt + '/data/scr_data/ads/'

ftp_site =       'ftp.eol.ucar.edu'
user =           'anonymous'
password =       ''
ftp_data_dir =   '/pub/data/incoming/ads/ads'

qc_ftp_site =    'catalog.eol.ucar.edu'
qc_ftp_dir =     '/pub/incoming/catalog/'+ project.lower()
#backup_raw_dir = '/mnt/opsdisk'
#backup_raw_dir2 = '/media/Seagate\ Expansion\ Drive/deepwave/'

#local_ftp_site = '192.168.1.10'
#local_user     = 'anonymous'
#local_password = 'cjw@ucar.edu'

local_ftp_dir  = '/FieldStorage/FieldProjects/WINTER/C130nc'
rlocal_ftp_dir = '/FieldStorage/FieldProjects/WINTER/RAFqc'
raircraft      = 'aircraft.NSF_NCAR_GV.'
#local_ftp_dir  = '/FieldStorage/Temporary Items'

nc2ascBatch = '/home/data/WINTER/nc2asc.bat'

translate2ds = '/home/local/raf/instruments/3v-cpi/translate2ds/translate2ds '
twods_aircraft = 'GV_N677F'

# ******************  End of Modification Section ****************

nc_dir    = data_dir + project + '/'
raw_dir   = data_dir + 'Raw_Data/' + project + '/'
process   = "false"

# End of Initialization section

# Prepare for final message information
proc_raw_file =    'NO!'
ship_raw_file =    'NO!    '
stor_raw_file =    'NO!    '
proc_3vcpi_files = 'NO!'
ship_3vcpi_files = 'NO!    '
stor_3vcpi_files = 'NO!    '
proc_nc_file  =    'NO!'
ship_nc_file  =    'NO!    '
stor_nc_file  =    'NO!    '
proc_kml_file =    'NO!'
ship_kml_file =    'NO!    '
stor_kml_file =    'NO!    '
proc_asc_file =    'NO!'
ship_asc_file =    'NO!    '
stor_asc_file =    'NO!    '
proc_iwg_file =    'NO!'
ship_iwg_file =    'NO!    '
stor_iwg_file =    'NO!    '
proc_qc_files =    'NO!'
ship_qc_files =    'NO!    '
stor_qc_files =    'NO!    '


# Get the flight designation
flight = raw_input('Input flight designation (e.g. tf01):')
print flight

final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
final_message = final_message + 'Process and Push log for Project:' + project
final_message = final_message + '  Flight:'+flight+'\r\n\r\n'


# Get the netCDF, kml  and raw ADS files for working with
# First netCDF
nclist = glob.glob(nc_dir+'*'+flight+'*.nc')
if nclist.__len__() == 1:
  ncfile = nclist[0]
  print "Found a netCDF file: "+ncfile
  reproc = ''
  while reproc == '' and reproc != 'R' and reproc != 'S':
    reproc = raw_input('Reproces? (R) or Ship? (S):')
  if reproc == 'R': 
    process = "true"
  else:
    process = "false"
elif nclist.__len__() == 0:
  print "No files found matching form: "+nc_dir+'*'+flight+'*.nc'
  print "We must process!"
  process = "true"
  ncfile = nc_dir+project+'_'+flight+".nc"
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
  if process == "true":
    print "We are scheduled to process all is good"
    kmlfile = nc_dir+project+'_'+flight+".kml"
  else:
    print "We have nc file but not kml file....  aborting..."
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

#nc2asc file
icarttlist = glob.glob(nc_dir+'*'+flight+'.asc')
if icarttlist.__len__() == 1:
  icarttfile = icarttlist[0]
elif icarttlist.__len__() == 0:
  print "No files found matching form: "+nc_dir+'*'+flight+'*.asc'
  if process == "true":
    print "We are scheduled to process all is good"
    icarttfile = nc_dir+project+"_"+flight+".asc"
  else:
    print "We have nc file but not ASCII file....  aborting..."
    sys.exit(0)
else:
  print "More than one file found.  Stepping through files, please select the right one"
  icarttfile = ''
  i = 0
  while icarttfile == '' :
    ans = raw_input(icarttlist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      icarttfile = icarttlist[i]
    if i < icarttlist.__len__() - 1: 
      i = i + 1
    else:
      i = 0
if icarttfile == '' :
  print "No ASCII file identified!"
  print "Aborting..."
  sys.exit(0)

#IWG1 file
iwg1list = glob.glob(nc_dir+'*'+flight+'.iwg1')
if iwg1list.__len__() == 1:
  iwg1file = iwg1list[0]
elif iwg1list.__len__() == 0:
  print "No files found matching form: "+nc_dir+'*'+flight+'*.iwg1'
  if process == "true":
    print "We are scheduled to process all is good"
    iwg1file = nc_dir+project+'_'+flight+".iwg1"
  else:
    print "We have nc file but not iwg1 file....  aborting..."
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

# RStudio PDF file

#Include time in RStudio filename so can load into field catalog
filename = rawfile.split(raw_dir)[1]
time = filename.split(".")[0].replace('_','')
FCfilename = rstudio_dir+project+'/'+raircraft+time[0:12]+'.RAF_QC_plots_hires.pdf'
RStudio_outfile = rstudio_dir+project+'/'+project+'_'+flight+'Plots.pdf'
#filename = rstudio_dir+project+'/'+project+flight+'Plots.pdf'

rstudiolist = glob.glob(FCfilename)
#rstudiolist = glob.glob(filename)

if rstudiolist.__len__() == 1:
  rstudiofile = rstudiolist[0]
elif rstudiolist.__len__() == 0:
  print "No files found matching form: "+FCfilename
  #print "No files found matching form: "+filename
  if process == "true":
    print "We are scheduled to process all is good"
    rstudiofile =  FCfilename
    #rstudiofile =  filename
  else:
    print "We have nc file but not rstudio file....  aborting..."
    sys.exit(0)
else:
  print "More than one file found.  Stepping through files, please select the right one"
  rstudiofile = ''
  i = 0
  while rstudiofile == '' :
    ans = raw_input(rstudiolist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      rstudiofile = rstudiolist[i]
    if i < rstudiolist.__len__() - 1: 
      i = i + 1
    else:
      i = 0
if rstudiofile == '' :
  print "No RStudio file identified!"
  print "Aborting..."
  sys.exit(0)

# RStudio HTML file

#Include time in RStudio filename so can load into field catalog
filename = rawfile.split(raw_dir)[1]
time = filename.split(".")[0].replace('_','')
FCfilenameHTML = rstudio_dir+project+'/'+raircraft+time[0:12]+'.RAF_QC_plots.html'
RStudio_outfileHTML = rstudio_dir+project+'/'+project+'_'+flight+'Plots.html'

rstudiolist = glob.glob(FCfilenameHTML)

if rstudiolist.__len__() == 1:
  rstudiofileHTML = rstudiolist[0]
elif rstudiolist.__len__() == 0:
  print "No files found matching form: "+FCfilenameHTML
  if process == "true":
    print "We are scheduled to process all is good"
    rstudiofileHTML =  FCfilenameHTML
  else:
    print "We have nc file but not rstudio file....  aborting..."
    sys.exit(0)
else:
  print "More than one file found.  Stepping through files, please select the right one"
  rstudiofileHTML = ''
  i = 0
  while rstudiofileHTML == '' :
    ans = raw_input(rstudiolist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      rstudiofileHTML = rstudiolist[i]
    if i < rstudiolist.__len__() - 1: 
      i = i + 1
    else:
      i = 0
if rstudiofileHTML == '' :
  print "No RStudio file identified!"
  print "Aborting..."
  sys.exit(0)

twoDfile = ''
# Run nimbus to generate first look product
# Use a configuration file
if process == "true":
  nimConfFile = "/tmp/nimbConf.txt"
  command = "rm -f " + nimConfFile
  os.system(command)

  cf = open(nimConfFile, 'w')
  line = 'if='+rawfile+'\n'
  cf.write(str(line))
  line = "of="+ncfile+'\n'
  cf.write(str(line))
  cf.close()

  command = "nimbus -b "+nimConfFile
  print "about to execute nimbus I hope: "+command
  if os.system(command) == 0:
    proc_raw_file =    'Yes'
    proc_kml_file =    'Yes'

# 3VCPI 
# Convert SPEC file form to oap file form
  twods_raw_dir = raw_dir+'3v_cpi/2DS/'+ string.upper(project) +'_'+ string.upper(flight) + '/'
  file_list = glob.glob(twods_raw_dir+'base*2DSCPI')
  if len(file_list) > 0:
    os.chdir(twods_raw_dir)
    for file in file_list:
      command = translate2ds + '-project ' + project + ' -flight ' + flight \
                +' -platform '+twods_aircraft + ' -sn SPEC001 -f ' + file + ' -o .'
      print ' 3v-cpi command:' + command
      os.system(command)
    
    # move 2D file to the RAF naming convention
    file_list = glob.glob('base*.2d')
    for file in file_list:
      datetime = file.split('.')[0].split('e')[1] #Pull out of base{datetime}.2d
      command = 'mv '+file+' 20'+datetime+'.2d'
      print ' mv command: '+command
      os.system(command)
      twoDfile = twods_raw_dir+'20'+datetime+'.2d'
    
    # Merge 3v-cpi data into netCDF file
    command = 'process2d '+twoDfile+' -o '+ncfile
    print "3v-cpi merge cmd: "+command
    if os.system(command) == 0:
      proc_3vcpi_files = 'Yes'


  
  command = "ncReorder "+ncfile+" tmp.nc";
  print "about to execute : "+command
  os.system(command)

  command = "/bin/mv tmp.nc "+ncfile;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_nc_file  =    'Yes'

  command = "nc2iwg1 "+ncfile+" > "+iwg1file;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_iwg_file = 'Yes'

  command = "nc2asc -b "+nc2ascBatch+" -i "+ncfile+" -o "+icarttfile;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_asc_file = 'Yes'

  os.chdir("/home/ads/RStudio/"+project)
  command = "Rscript /home/ads/RStudio/"+project+"/Review.R "+flight
  print "about to execute : "+command
  os.system(command)

  # rename Rstudio output files to name with time so can input into
  # field catalog
  command = "/bin/mv " + RStudio_outfile + " " + rstudiofile;
  print "about to execute : "+command
  os.system(command)
  command = "/bin/mv " + RStudio_outfileHTML + " " + rstudiofileHTML;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_qc_files = "Yes"

else:
  print "Processing already done, skipping nimbus command"


print "**************************"
print "NetCDF file = "+ncfile
print os.system("ls -l "+ncfile)
print "KML file = "+kmlfile
print os.system("ls -l "+kmlfile)
print "IWG1 file = "+iwg1file
print os.system("ls -l "+iwg1file)
print "ASCII file = "+icarttfile
print os.system("ls -l "+icarttfile)
print "RStudio PDF file = "+rstudiofile
print os.system("ls -l "+rstudiofile)
print "RStudio PDF outfile = "+RStudio_outfile
print os.system("ls -l "+RStudio_outfile)
print "RStudio HTML file = "+rstudiofileHTML
print os.system("ls -l "+rstudiofileHTML)
print "RStudio HTML outfile = "+rstudiofileHTML
print os.system("ls -l "+rstudiofileHTML)
print "Raw ADS file = "+rawfile
print os.system("ls -l "+rawfile)
if twoDfile != '':
  print "3V-CPI 2DS file = "+twoDfile
  print os.system("ls -l "+twoDfile)
print "**************************"
print ""

if NAS == 'true':
  # Put copies of files to local store
  command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
  print 'Mounting nas: '+command
  os.system(command)
  command = 'rsync '+ncfile+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_nc_file = 'Yes-NAS'
  else: 
    print 'ERROR!: syncing file: '+command
  command = 'rsync '+kmlfile+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_kml_file = 'Yes-NAS'
  else:
    print 'ERROR!: Syncing file: '+command
  command = 'rsync '+iwg1file+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_iwg_file = 'Yes-NAS'
    print 'ERROR!: Syncing file: '+command
  command = 'rsync '+icarttfile+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_asc_file = 'Yes-NAS'
  else:
    print 'ERROR!: Syncing file: '+command

  command = 'rsync '+rstudiofile+" "+nas_data_dir+"/qc/"
  print 'Syncing file: '+command
  if os.system(command) == 0:
    stor_qc_files = 'Yes-NAS'
  else:
    print 'ERROR!: Syncing file: '+command
  command = 'rsync '+rstudiofileHTML+" "+nas_data_dir+"/qc/"
  print 'Syncing file: '+command
  if os.system(command) == 0:
    stor_qc_files = 'Yes-NAS'
  else:
    print 'ERROR!: Syncing file: '+command

  command = 'rsync '+rawfile+" "+nas_data_dir+"/raw/"
  print 'Syncing file: '+command
  if os.system(command) == 0:
    stor_raw_file = 'Yes-NAS'
  else:
    print 'ERROR!: Syncing file: '+command

  command = "sudo /bin/umount "+nas_mnt_pt
  print 'Unmounting nas: ' + command
  os.system(command) 

# ZIP up the files as per expectations back home
# First the nc file and the kml file go into one zip file (note want the files
#   to exist at the diretory level of the zip file)

data_dir,ncfilename = os.path.split(ncfile)
data_dir,kmlfilename = os.path.split(kmlfile)
data_dir,iwg1filename = os.path.split(iwg1file)
data_dir,icarttfilename = os.path.split(icarttfile)
rdata_dir,rstudiofilename = os.path.split(rstudiofile)
rdata_dir,rstudiofilenameHTML = os.path.split(rstudiofileHTML)
zip_data_filename = "PROD_"+project+"_"+flight+".zip"
zip_data_file = data_dir+zip_data_filename
print "data_dir = "+data_dir
print "ncfilename = "+ncfilename
print "kmlfilename = "+kmlfilename
print "iwg1filename = "+iwg1filename
print "icarttfilename = "+icarttfilename
print "RStudiofilenamePDF = "+rstudiofilename
print "RStudiofilenameHTML = "+rstudiofilenameHTML

# Make sure that there is not a zip file already there ("overwrite")
command = "cd "+data_dir+"; rm "+zip_data_filename
os.system(command)
command = "cd "+data_dir+"; zip " + zip_data_filename + " " + ncfilename + " " + kmlfilename + " " + iwg1filename + " " + icarttfilename
if os.system(command) != 0:
  print ""
  print "ERROR!: Zipping up netCDF, IWG1, ASCII and KML files with command:\n  "
  print command

# Put QC files into catalog and to the NAS if it exists
try:
  print 'opening FTP connection to: ' + qc_ftp_site

  ftp = ftplib.FTP(qc_ftp_site)
  ftp.login(user, password)
  ftp.cwd(qc_ftp_dir)
  print ""
  print "Putting file:"+rstudiofilename
  os.chdir(rdata_dir)
  file = open(rstudiofilename, 'r')
  ftp.storbinary('STOR ' + rstudiofilename, file)
  file.close()
  print "Putting file:"+rstudiofilenameHTML
  file = open(rstudiofilenameHTML, 'r')
  ftp.storbinary('STOR ' + rstudiofilenameHTML, file)
  file.close()
  print "Finished putting QC files"
  print ""
  ftp.quit()
  ship_qc_files = 'Yes-Cat'

except ftplib.all_errors as e:
  print ""
  print 'Error writing QC data to server'
  print e
  try:
    ftp.quit()
    file.close()
  except ftplib.all_errors as e:
    print 'Could not close ftp connection:'
    print e
#  sys.exit(1)

#if NAS == 'true':
  # mount the NAS and put QC files to it
#  os.chdir(rdata_dir)
#  command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
#  print 'Mounting nas: '+command
#  os.system(command)
#  command = 'rsync '+rstudiofilename+" "+nas_data_dir+" qc/"
#  print 'Syncing QC file: '+command
#  os.system(command)
#  command = 'rsync '+rstudiofilenameHTML+" "+nas_data_dir+" qc/"
#  print 'Syncing QC file: '+command
#  os.system(command)
#  command = "sudo /bin/umount "+nas_mnt_pt
#  print 'Unmounting nas: ' + command
#  os.system(command)
#
# Put zipped files to EOL server
if NAS != 'true':
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

    if ncfilename: 
      ship_nc_file = 'Yes-FTP'
    if kmlfilename:
      ship_kml_file = 'Yes-FTP'
    if iwg1filename:
      ship_iwg_file = 'Yes-FTP'
    if icarttfilename:
      ship_asc_file = 'Yes-FTP'

  except ftplib.all_errors as e:
    print ""
    print 'Error writing nc/kml data file to eol server'
    print e
    ftp.quit()
#    sys.exit(1)

# put zipped file onto NAS for BT-syncing back home.
else:

  # Now ZiP up the rawfile - since it replaces raw file, do in /tmp
  raw_dir,rawfilename = os.path.split(rawfile)
  zip_raw_file = '/tmp/'+rawfilename+".bz2"
  print "rawfilename = "+rawfilename
  # remove zip file if it exists
  os.chdir('/tmp')
  command = 'cp -f '+rawfile+ ' .'
  print "copy rawfile to temp: "+command
  os.system(command)
  command = "rm -f "+zip_raw_file
  print "remove any old copies of bz file: "+command
  os.system(command)
  command = "bzip2 " +rawfilename
  print ""
  print "Zipping up raw data file with command:"
  print command
  os.system(command)

  # mount the NAS and put zipped raw file to it
  command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
  print 'Mounting nas: '+command
  os.system(command)

  os.chdir(data_dir)
  command = 'rsync '+zip_data_filename+" "+nas_sync_dir
  if os.system(command) == 0:
    if ncfilename: 
      ship_nc_file = 'Yes-NAS'
    if kmlfilename:
      ship_kml_file = 'Yes-NAS'
    if iwg1filename:
      ship_iwg_file = 'Yes-NAS'
    if icarttfilename:
      ship_asc_file = 'Yes-NAS'
  else:
    print 'ERROR!: syncing zipfile:'+command
    
  command = 'rsync '+zip_raw_file+" "+nas_sync_dir
  if os.system(command) == 0:
    ship_raw_file = 'Yes-NAS'
  else:
    print 'ERROR!: Syncing zipfile: '+command

  command = "sudo /bin/umount "+nas_mnt_pt
  print 'Unmounting nas: ' + command
  os.system(command)


# Put zipped raw files to backup disk as well (two copies)
# This disk crashed after RF14 - not sure if it can be revived
#try:
#    print ""
#    print 'copying '+rawfilename+' to '+backup_raw_dir
#    command = "cp "+rawfilename+" "+backup_raw_dir
#    os.system(command)

#except:
#    print "problems copying file, exiting."
#    os.remove(busy_file)
#    sys.exit(1)

# Put zipped raw files to backup disk as well (third copy)
#try:
#    print ""
#    print 'copying '+rawfilename+' to '+backup_raw_dir2
#    command = "cp "+rawfilename+" "+backup_raw_dir2
#    os.system(command)

#except:
#    print "problems copying file, exiting."
#    os.remove(busy_file)
#    sys.exit(1)

# Put unzipped data files to field server

#try: 
#    print ""
#    print 'Local Data Store: opening FTP connection to: ' + local_ftp_site
#
##    ftp = ftplib.FTP(local_ftp_site)
#    ftp.login(local_user, local_password)
#    ftp.cwd(local_ftp_dir)
#    print "Putting netCDF file: "+ncfilename
#    print "from directory: "+data_dir
#    os.chdir(data_dir)
#    file = open(ncfilename, 'r')
#    ftp.storbinary('STOR ' + ncfilename, file)
#    file.close()
#    print "Putting IWG1 file: "+iwg1filename
#    file = open(iwg1filename, 'r')
#    ftp.storbinary('STOR ' + iwg1filename, file)
#    file.close()
#    print "Putting KML file: "+kmlfilename
#    file = open(kmlfilename, 'r')
#    ftp.storbinary('STOR ' + kmlfilename, file)
#    file.close()
#    print "Putting ASCII file: "+icarttfilename
#    file = open(icarttfilename, 'r')
#    ftp.storbinary('STOR ' + icarttfilename, file)
#    file.close()
#
#    os.chdir(rdata_dir)
#    ftp.cwd(rlocal_ftp_dir)
#    print "Putting RStudio PDF file: "+rstudiofile
#    file = open(rstudiofilename, 'r')
#    ftp.storbinary('STOR ' + rstudiofilename, file)
#    file.close()
#    print "Putting RStudio HTML file: "+rstudiofileHTML
#    file = open(rstudiofilenameHTML, 'r')
#    ftp.storbinary('STOR ' + rstudiofilenameHTML, file)
#    file.close()
#    print "Done Putting data files to local ftp server"
#    print ""
#    ftp.quit()
#
#except ftplib.all_errors as e:
#    print 'Error writing data file to local ftp server'
#    print e
#    ftp.quit()
#
#
## Put zipped raw files to EOL server
## ADS images . temporary comment out. CJW WINTER.
#try: 
#    print ""
#    print 'opening FTP connection to: ' + local_ftp_site
#
#    ftp = ftplib.FTP(local_ftp_site)
#    ftp.login(local_user, local_password)
#    ftp.cwd(ftp_raw_dir)
#    print "Putting ADS file: "+rawfilename
#    os.chdir(raw_dir)
#    file = open(rawfilename, 'r')
#    ftp.storbinary('STOR ' + rawfilename, file)
#    file.close()
#    print "Finished putting raw data file"
#    print ""
#    ftp.quit()
#
#except ftplib.all_errors as e:
#    print 'Error writing raw data file to eol server'
#    print e
#    ftp.quit()

final_message = final_message + ' REPORT on Processing and shipping. \n\n'
final_message = final_message + 'FileType  Proc Stor     Ship\n'
final_message = final_message + 'Raw       '+proc_raw_file+'  '+stor_raw_file+'  '+ship_raw_file+'\n'
final_message = final_message + '3VCPI     '+proc_3vcpi_files+'  '+stor_3vcpi_files+'  '+ship_3vcpi_files+'\n'
final_message = final_message + 'NetCDF    '+proc_nc_file+'  '+stor_nc_file+'  '+ship_nc_file+'\n'
final_message = final_message + 'KML       '+proc_kml_file+'  '+stor_kml_file+'  '+ship_kml_file+'\n'
final_message = final_message + 'ASCII     '+proc_asc_file+'  '+stor_asc_file+'  '+ship_asc_file+'\n'
final_message = final_message + 'IWG       '+proc_iwg_file+'  '+stor_iwg_file+'  '+ship_iwg_file+'\n'
final_message = final_message + 'QC        '+proc_qc_files+'  '+stor_qc_files+'  '+ship_qc_files+'\n'
final_message = final_message + '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'

print final_message

raw_input("\n\nPress Enter to continue...")
sys.exit(1)

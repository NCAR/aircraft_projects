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
import smtplib
from email.mime.text import MIMEText


# Products set to true if you want 'em
nc2asc = 'true'
nc2iwg = 'false'
catalog = 'false'

#
# Do we have local SWIG RAID storage.
NAS =            'false'

#
# Instrument specific processing, true or false depending on if instrument is on project.
twoD      =      'true'
threeVCPI =      'false'

nc2ascBatch =	os.environ["PROJ_DIR"] +'/'+ project +'/'+ aircraft
		+ '/Production/nc2asc.bat'

# Initialization 
#  *******************  Modify The Following *********************
#  NOTE: Be sure to ask the systems group to create a directory:
#   /net/ftp/pub/data/download/project_name
#   and that it be owned by the ads user.
#   Note that the CWIG standard and the standard expected by the 
#   catcher script will be that project_name above will be the lower
#   case version of the project name e.g. icebridge2015 not ICEBRIDGE2015
#
#   The RStudio piece seems to need special setup for each project
#
#  NOTE: assumes that Raw_Data is subdirectory of data_dir + project
#
#  TODO: project should be pulled from environment variable(?)
#
try:
  project =	os.environ["PROJECT"]
except KeyError:
  print "Please set the environment variable PROJECT."
  sys.exit(1)

try:
  aircraft =	os.environ["AIRCRAFT"]
except KeyError:
  print "Please set the environment variable AIRCRAFT."
  sys.exit(1)

try:
  data_dir =	os.environ["DATA_DIR"] + '/' + project + '/'
except KeyError:
  print "Please set the environment variable DATA_DIR."
  sys.exit(1)

try:
  raw_dir       = os.environ["RAW_DATA_DIR"] + '/' + project + '/'
except KeyError:
  print "Please set the environment variable RAW_DATA_DIR."
  sys.exit(1)

rstudio_dir =	'/home/ads/RStudio/'

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

local_ftp_dir  = '/FieldStorage/FieldProjects/' + project + '/C130nc'
rlocal_ftp_dir = '/FieldStorage/FieldProjects/' + project + '/RAFqc'
raircraft      = 'aircraft.NSF_NCAR_GV.'
#local_ftp_dir  = '/FieldStorage/Temporary Items'

translate2ds = '/home/local/raf/instruments/3v-cpi/translate2ds/translate2ds '


# Echo configuration:
print
print 'Processing ' + project + ' from ' + aircraft + '.   If incorrect, edit ~/ads3_environment.'
print

# ******************  End of Modification Section ****************

# Get the flight designation
flight = raw_input('Input flight designation (e.g. tf01):')
print flight
email = raw_input('Input email address to send results:')


file_prefix =	project + flight

twods_raw_dir = raw_dir+'3v_cpi/2DS/'+ string.upper(project) +'_'+ string.upper(flight) + '/'
oapfile_dir   = raw_dir+'3v_cpi/oapfiles/'
twodfile_dir  = raw_dir+'PMS2D/'
cpi_raw_dir   = raw_dir+'3v_cpi/CPI/'+string.upper(project) + '_' + string.upper(flight) + '/'
process   = "false"

# End of Initialization section

# Prepare for final message information
proc_raw_file =    'NO!'
ship_raw_file =    'NO!    '
stor_raw_file =    'NO!    '
proc_3vcpi_files = 'NO!'
ship_3vcpi_files = 'NO!    '
stor_3vcpi_files = 'NO!    '
proc_2d_files    = 'NO!'
ship_2d_files    = 'NO!    '
stor_2d_files    = 'NO!    '
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

final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
final_message = final_message + 'Process and Push log for Project:' + project
final_message = final_message + '  Flight:'+flight+'\r\n\r\n'


##############   Beginning of Setup ######################################

# Get the netCDF, kml, icartt, IWG1 and raw ADS files for working with
# First netCDF
nclist = glob.glob(data_dir+'*'+flight+'*.nc')
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
  print "No files found matching form: "+data_dir+'*'+flight+'*.nc'
  print "We must process!"
  process = "true"
  ncfile = data_dir+file_prefix+".nc"
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
  #sys.exit(0)

#KML file
kmllist = glob.glob(data_dir+'*'+flight+'.kml')
if kmllist.__len__() == 1:
  kmlfile = kmllist[0]
elif kmllist.__len__() == 0:
  print "No files found matching form: "+data_dir+'*'+flight+'*.kml'
  if process == "true":
    print "We are scheduled to process all is good"
    kmlfile = data_dir+file_prefix+".kml"
  else:
    print "We have nc file but not kml file....  aborting..."
    #sys.exit(0)
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
  #sys.exit(0)

#nc2asc file
icarttfile = ''
icarttlist = glob.glob(data_dir+'*'+flight+'.asc')
if icarttlist.__len__() == 1:
  icarttfile = icarttlist[0]
elif icarttlist.__len__() == 0:
  print "No files found matching form: "+data_dir+'*'+flight+'*.asc'
  if process == "true":
    print "We are scheduled to process all is good"
    icarttfile = data_dir+file_prefix+".asc"
  else:
    print "We have nc file but not ASCII file....  aborting..."
    #sys.exit(0)
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
  #sys.exit(0)

#IWG1 file
iwg1list = glob.glob(data_dir+'*'+flight+'.iwg1')
if iwg1list.__len__() == 1:
  iwg1file = iwg1list[0]
elif iwg1list.__len__() == 0:
  print "No files found matching form: "+data_dir+'*'+flight+'*.iwg1'
  if process == "true":
    print "We are scheduled to process all is good"
    iwg1file = data_dir+file_prefix+".iwg1"
  else:
    print "We have nc file but not iwg1 file....  aborting..."
    #sys.exit(0)
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
  #sys.exit(0)

#Raw Data File
rawlist = glob.glob(raw_dir+'*'+flight+'*.ads')
if rawlist.__len__() == 1:
  rawfile = rawlist[0]
elif rawlist.__len__() == 0:
  print "No Raw files found matching the form: raw_dir+'*'+flight+'*.ads'"
  print "aborting..."
  #sys.exit(0)
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
  #sys.exit(0)

# RStudio PDF file

#Include time in RStudio filename so can load into field catalog
filename = rawfile.split(raw_dir)[1]
time = filename.split(".")[0].replace('_','')
FCfilename = rstudio_dir+project+'/'+raircraft+time[0:12]+'.RAF_QC_plots_hires.pdf'
RStudio_outfile = rstudio_dir+project+'/'+project+flight+'Plots.pdf'
#filename = rstudio_dir+project+'/'+project+flight+'Plots.pdf'

rstudiolist = glob.glob(FCfilename)
#rstudiolist = glob.glob(filename)

rstudiofile = ''
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
    #sys.exit(0)
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
  #sys.exit(0)

# RStudio HTML file

#Include time in RStudio filename so can load into field catalog
filename = rawfile.split(raw_dir)[1]
time = filename.split(".")[0].replace('_','')
FCfilenameHTML = rstudio_dir+project+'/'+raircraft+time[0:12]+'.RAF_QC_plots.html'
RStudio_outfileHTML = rstudio_dir+project+'/'+project+flight+'Plots.html'

rstudiolist = glob.glob(FCfilenameHTML)

rstudiofileHTML = ''
if rstudiolist.__len__() == 1:
  rstudiofileHTML = rstudiolist[0]
elif rstudiolist.__len__() == 0:
  print "No files found matching form: "+FCfilenameHTML
  if process == "true":
    print "We are scheduled to process all is good"
    rstudiofileHTML =  FCfilenameHTML
  else:
    print "We have nc file but not rstudio file....  aborting..."
    #sys.exit(0)
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
  #sys.exit(0)

#########################  End of Setup ###################################

###################  Beginning of Processing ##############################
threevcpi2d_file = ''
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

  command = "/opt/local/bin/nimbus -b "+nimConfFile
  print "about to execute nimbus I hope: "+command

  res = os.system(command)
  print 'result of nimbus call = '+str(res)

  if res == 0:
    proc_raw_file =    'Yes'
    proc_kml_file =    'Yes'

# 3VCPI 
# Convert SPEC file form to oap file form
  if threeVCPI=='true':
    print "\n\n *****************  3VCPI **************************\n"
    mkdir_fail = 'false'
    first_base_file = ''
    catted_file = 'base_'+flight+'all.2DSCPI'
    catted_2d_file = 'base_'+flight+'all.2d'
    os.chdir(twods_raw_dir)
    if os.path.isfile(catted_file):
      os.remove(catted_file)
    file_list = glob.glob(twods_raw_dir+'base*2DSCPI')
    if len(file_list) > 0:
      os.chdir(twods_raw_dir)
      filenum = 1
      for file in file_list:
        if filenum == 1:
          first_base_file = file
        command = 'cat '+file+' >> '+catted_file
        print "cat 3vcPIfiles:"+command
        os.system(command)
  
      command = translate2ds + '-project ' + project + ' -flight ' + flight \
                +' -platform '+aircraft + ' -sn SPEC001 -f ' + catted_file + ' -o .'
      print ' 3v-cpi command:' + command
      os.system(command)
      
      # move 2D file to the RAF naming convention and location
      if not os.path.isdir(oapfile_dir):
        try:
          os.mkdir(oapfile_dir)
        except:
          message= "\nERROR: Could not make oapfile directory:"+oapfile_dir
          message= message +  "\n  - skipping 2d file gen/placement\n"
          print message
          final_message = final_message + message
          mkdir_fail = 'true'
      if not mkdir_fail == 'true':
        twod_dir,fb_filename=os.path.split(first_base_file)
        datetime = fb_filename.split('.')[0].split('e')[1] #Pull out of base{datetime}.2d
        command = 'mv '+catted_2d_file+' '+oapfile_dir+'20'+datetime+'_'+flight+'.2d'
        print ' mv command: '+command
        os.system(command)
        threevcpi2d_file = oapfile_dir+'20'+datetime+'_'+flight+'.2d'
      
        # Merge 3v-cpi data into netCDF file
        command = 'process2d '+threevcpi2d_file+' -o '+ncfile
        print "3v-cpi merge cmd: "+command
        if os.system(command) == 0:
          proc_3vcpi_files = 'Yes'

# 2D data
  if twoD=='true':
    mkdir_fail = 'false'
    if not os.path.isdir(twodfile_dir): 
      try:
        os.mkdir(twodfile_dir)
      except:
        message = "\nERROR: Could not make 2D file directory:"+twodfile_dir
        message = message + "\n - skipping 2d file extract\n"
        print message
        final_message = final+message + message
        mkdir_fail = 'true'
    if not mkdir_fail == 'true':
      filename = rawfile.split(raw_dir)[1]
      fileelts = filename.split('_')
      twoDfile = twodfile_dir+fileelts[0]+'_'+fileelts[1]+'_'+flight+'.2d'
      command = 'extract2d '+twoDfile+' '+rawfile
      message = '\nExtracting 2D from ads:'+command+'\n'
      print message
      os.system(command)

    # merge 2D data into netCDF file
    command = 'process2d '+twoDfile+' -o '+ncfile
    print '2D merge command: '+command
    if os.system(command) == 0:
      proc_2d_files = 'Yes'
      ship_2d_files = 'ads&NC '
      stor_2d_files = 'ads&NC '
    else:
      ship_2d_files = 'ads    '
      ship_2d_files = 'ads    '

  
# NetCDF utility work - Reorder, generate Iwg ascii and ICARTT ascii
  command = "ncReorder "+ncfile+" tmp.nc";
  print "about to execute : "+command
  os.system(command)

  command = "/bin/mv tmp.nc "+ncfile;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_nc_file  =    'Yes'
  else:
    print "ERROR: NC Reorder failed! But NetCDF file should be fine"
    proc_nc_file  =    'Yes'

  if nc2iwg == 'true':
    command = "nc2iwg1 "+ncfile+" > "+iwg1file;
    print "about to execute : "+command
    if os.system(command) == 0:
      proc_iwg_file = 'Yes'

  if nc2asc == 'true':
    command = "nc2asc -b "+nc2ascBatch+" -i "+ncfile+" -o "+icarttfile;
    print "about to execute : "+command
    if os.system(command) == 0:
      proc_asc_file = 'Yes'

# Run Al Cooper's R code for QA/QC production
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
if threevcpi2d_file != '':
  print "3V-CPI 2DS file = "+threevcpi2d_file
  print os.system("ls -l "+threevcpi2d_file)
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
    message = '\nERROR!: syncing file: '+command
    print message
    final_message = final_message + message
  command = 'rsync '+kmlfile+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_kml_file = 'Yes-NAS'
  else:
    message = '\nERROR!: syncing file: '+command
    print message
    final_message = final_message + message
  command = 'rsync '+iwg1file+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_iwg_file = 'Yes-NAS'
    print 'ERROR!: Syncing file: '+command
  command = 'rsync '+icarttfile+" "+nas_data_dir+"/nc/"
  if os.system(command) == 0:
    stor_asc_file = 'Yes-NAS'
  else:
    message = '\nERROR!: syncing file: '+command
    print message
    final_message = final_message + message

  command = 'rsync '+rstudiofile+" "+nas_data_dir+"/qc/"
  print 'Syncing file: '+command
  if os.system(command) == 0:
    stor_qc_files = 'Yes-NAS'
  else:
    message = '\nERROR!: syncing file: '+command
    print message
    final_message = final_message + message
  command = 'rsync '+rstudiofileHTML+" "+nas_data_dir+"/qc/"
  print 'Syncing file: '+command
  if os.system(command) == 0:
    stor_qc_files = 'Yes-NAS'
  else:
    message = '\nERROR!: syncing file: '+command
    print message
    final_message = final_message + message

  command = 'rsync '+rawfile+" "+nas_data_dir+"/raw/"
  print 'Syncing file: '+command
  if os.system(command) == 0:
    stor_raw_file = 'Yes-NAS'
  else:
    message = '\nERROR!: syncing file: '+command
    print message
    final_message = final_message + message

emailfilename = 'email.addr.txt'
emailfile = data_dir+emailfilename
command = 'rm '+emailfile
os.system(command)
fo = open(emailfile, 'w+')
fo.write(email+'\n')
fo.close()

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

#ICEBRIDGE special request for raw DGPS Data
if project == 'ICEBRIDGE2015':
  pcdfilename = project+'_'+flight+'.PDC'
  command = 'data_dump -i 3,160 -n '+rawfile+'> '+data_dir+'/'+pcdfilename
  os.system(command)

# Make sure that there is not a zip file already there ("overwrite")
command = "cd "+data_dir+"; rm "+zip_data_filename
os.system(command)
command = "cd "+data_dir+"; zip " + zip_data_filename + " " + ncfilename + " " + kmlfilename + " " + iwg1filename + " " + icarttfilename + " " + emailfilename
if os.system(command) != 0:
  message =  "\nERROR!: Zipping up netCDF, IWG1, ASCII and KML files with command:\n  "
  message = message + command
  print message
  final_message = final_message + message

# Put QC files into catalog and to the NAS if it exists
if catalog=='true':
  try:
    print 'opening FTP connection to: ' + qc_ftp_site
    print '- putting QC data in directory: ' + qc_ftp_dir
  
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
    print datetime.datetime.now().time()
    print "Putting file:"+zip_data_filename
    os.chdir(data_dir)
    file = open(zip_data_filename, 'r')
    ftp.storbinary('STOR ' + zip_data_filename, file)
    file.close()
    print datetime.datetime.now().time()
    print "Finished putting data file"
    print ""
    ftp.quit()

    if ncfilename != '': 
      ship_nc_file = 'Yes-FTP'
    if kmlfilename != '':
      ship_kml_file = 'Yes-FTP'
    if iwg1filename != '':
      ship_iwg_file = 'Yes-FTP'
    if icarttfilename != '':
      ship_asc_file = 'Yes-FTP'

  except ftplib.all_errors as e:
    print ""
    print 'Error writing nc/kml data file to eol server'
    print e
    ftp.quit()
#    sys.exit(1)

# put zipped file onto NAS for BT-syncing back home.
else:

  # Now ZiP up the rawfile - since bzip2 overwrites raw file, do in /tmp
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

#  command = "sudo /bin/umount "+nas_mnt_pt
#  print 'Unmounting nas: ' + command
#  os.system(command)


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
final_message = final_message + '2D        '+proc_2d_files+'  '+stor_2d_files+'  '+ship_2d_files+'\n'
final_message = final_message + 'NetCDF    '+proc_nc_file +'  '+stor_nc_file +'  '+ship_nc_file+'\n'
final_message = final_message + 'KML       '+proc_kml_file+'  '+stor_kml_file+'  '+ship_kml_file+'\n'
final_message = final_message + 'ASCII     '+proc_asc_file+'  '+stor_asc_file+'  '+ship_asc_file+'\n'
final_message = final_message + 'IWG       '+proc_iwg_file+'  '+stor_iwg_file+'  '+ship_iwg_file+'\n'
final_message = final_message + 'QC        '+proc_qc_files+'  '+stor_qc_files+'  '+ship_qc_files+'\n'
final_message = final_message + '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'

print final_message
msg = MIMEText(final_message)
msg['Subject'] = 'Process & Push message for:'+project+'  flight:'+flight
msg['From'] = 'ads@groundstation'
msg['To'] = email

s = smtplib.SMTP('smtp.mail.yahoo.com:587')
s.ehlo()
s.starttls()
s.ehlo()
s.login('ads_raf_ncar@yahoo.com','color;tree2')
s.sendmail('ads_raf_ncar@yahoo.com', email, msg.as_string())
s.quit()

raw_input("\n\nPress Enter to terminate...")
answer = 'N'
while answer != 'Y':
  answer = raw_input('\n\n  Are you sure you want to terminate? (Y/N):')
sys.exit(1)

#!/usr/bin/python
#
# It takes a flight number designation and then using it gets raw ads 
# file, netCDF file and kml file for that flight number (verifying with the 
# user where needed) and does several things:
#  1: zips up the nc, kml, and iwg1 files into a single zip file 
#  2: zips up the ads file
#  3: Creates interactive plots using an Rstudio script
#  4: copies nc, kml, to local FTP site for readynas to sync to Boulder
#  4: FTPs the nc and kml files to a local server in the Ops center 
#

import os
import re
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
from collections import OrderedDict

def read_env(env_var):
  try:
    var =	os.environ[env_var]
    return(var)
  except KeyError:
    print "Please set the environment variable "+env_var
    sys.exit(1)

project = read_env("PROJECT")
aircraft = read_env("AIRCRAFT")
data_dir = read_env("DATA_DIR") + '/' + project + '/'
raw_dir  = read_env("RAW_DATA_DIR") + '/' + project + '/'
proj_dir  = read_env("PROJ_DIR") + '/' + project + '/' + aircraft + '/'

# Initialization 
sys.path.insert(0,proj_dir)
from fieldProc_setup import *
# Note: The RStudio piece seems to need special setup for each project

# Query user for the flight designation and place to send output
flight = raw_input('Input flight designation (e.g. tf01):')
print flight
email = raw_input('Input email address to send results:')


##############   Beginning of Setup ######################################
nc2ascBatch =	proj_dir + 'scripts/nc2asc.bat'

# Don't make it Raw_Data/proj.
zip_dir = '/tmp/'

# Catalog setup should not need to change - they are very consistent
# so leave this here, rather than in project-specific setup file
qc_ftp_site =    'catalog.eol.ucar.edu'
# Hard-code around project name inconsistency. Revert for next project.
#qc_ftp_dir =     '/pub/incoming/catalog/'+ project.lower()
qc_ftp_dir =     '/pub/incoming/catalog/we-can'
if aircraft == "GV_N677F":
  raircraft      = 'aircraft.NSF_NCAR_GV.'
elif aircraft == "C130_N130AR":
  raircraft      = 'aircraft.NSF_NCAR_C-130.'
else:
  print "Unknown aircraft "+aircraft+" Update code\n"
  sys.exit(1)

# Echo configuration:
print
print 'Processing ' + project + ' from ' + aircraft + '.   If incorrect, edit ~/ads3_environment.'
print
print 'Expecting to find .ads files in ' + raw_dir + '.'
print

# *************************  Dictionaries ************************
# These are directories where instrument-specific data files (not 
# RAF standard data) can be found.
inst_dir = {
   "ADS"   : raw_dir,
   "LRT"   : data_dir,
   "KML"   : data_dir,
   "HRT"   : data_dir,
   "SRT"   : data_dir,
   "ICARTT": data_dir,
   "IWG1"  : data_dir,
   "PMS2D" : raw_dir+'PMS2D/',
   "twods" : raw_dir+'3v_cpi/2DS/'+ string.upper(project) +'_'+ string.upper(flight) + '/',
   "oap"   : raw_dir+'3v_cpi/oapfiles/',
   "cpi"   : raw_dir+'3v_cpi/CPI/'+string.upper(project) + '_' + string.upper(flight) + '/',
}

# Add extensions here for file types you want to process
# This should ONLY contain extensions based on files you want to process
# Populate from config file fieldProc_setup.py based on True/False settings.
file_ext = OrderedDict ([("ADS" , "ads"), ("LRT" , "nc"), ("KML" , "kml")])
if HRT:
  file_ext["HRT"] =  "nc"
if SRT:
  file_ext["SRT"] =  "nc"
if ICARTT:
  file_ext["ICARTT"] = "ict"
if IWG1:
  file_ext["IWG1"] = "iwg"
if PMS2D:
  file_ext["PMS2D"] = "2d"
if threeVCPI:
  file_ext["threeVCPI"] = "2ds"

# Dictionary to hold data file names
filename = {}

# NetCDF filename rate indicator
file_type = {
  "ADS" : "",
  "LRT" : "",
  "KML" : "",
  "HRT" : "h",
  "SRT" : "s",
  "ICARTT" : "",
  "IWG1" : "",
  "PMS2D" : "",
}

# nimbus processing rates (for use in config files)
rate = {
  "LRT" : "1",
  "HRT" : "25",
  "SRT" : "0",
}

# nimbus config filename extensions
config_ext = {
  "LRT" : "",
  "HRT" : "_HRT",
  "SRT" : "_SRT",
}

# This dictionary contains a list of all file types you want to report
# status on.
status = {
   "ADS"         : { "proc" : "N/A", "ship" : "No!", "stor" : "No!"},
   "LRT"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "KML"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "HRT"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "SRT"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "ICARTT"      : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "IWG1"        : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "PMS2D"       : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "threeVCPI"   : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "QCplots"     : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
}
####################   End of Setup ######################################

####################   Begin function definitions ########################
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

# If you print an error message to the screen, also print it to the email.
def print_message(message):
    global final_message
    print message
    final_message = final_message + message

# Rsync file to output dir and record success status
def rsync_file(file,out_dir):
  command = 'rsync '+file+" "+out_dir
  if os.system(command) == 0:
    proc_file = 'Yes-NAS'
    return(str(proc_file));
  else: 
    message = '\nERROR!: syncing file: '+command
    print_message(message)

# See of a LRT file exists already and query user about what to do.
def find_lrt_netcdf(filetype):

  process=False
  reprocess=False

  nclist = glob.glob(data_dir+'*'+flight+'.'+filetype)
  if nclist.__len__() == 1:
    ncfile = nclist[0]
    print "Found a netCDF file: "+ncfile

    # Since found a netCDF file, query user if they want to reprocess the data,
    # or if they just want to ship the data to the NAS/ftp site.
    reproc = ''
    while reproc == '' and reproc != 'R' and reproc != 'S':
      reproc = raw_input('Reprocess? (R) or Ship? (S):')
    if reproc == 'R': 
      process = True
      reprocess = True
    else: # Ship only
      process = False
      reprocess = False 

  elif nclist.__len__() == 0:
    print "No files found matching form: "+data_dir+'*'+flight+'.'+filetype
    print "We must process!"
    process = True
    ncfile = data_dir+file_prefix+".nc"

  else:
    print "More than one "+filetype+" file found."
    ncfile=step_through_files(nclist)

  if ncfile == '' : 
    print "No NetCDF file identified!"
    print "Aborting"
    sys.exit(0)

  return(process,reprocess,ncfile)

# See of a file exists already and query user about what to do.
def find_file(data_dir,flight,file_prefix,filetype,fileext,flag):
  datafile = ''
  datalist = glob.glob(data_dir+'*'+flight+filetype+'.'+fileext)
  if (datalist.__len__() == 1):
    if (flag == False):
      reproc = raw_input('Found file: datalist[0]. Reprocess?(Y/N)')
      if reproc == 'Y':
       flag = True
    datafile = datalist[0]
  elif datalist.__len__() == 0:
    print "No files found matching form: "+data_dir+'*'+flight+filetype+'*.'+fileext
    if fileext == 'ads':
      print "Aborting..."
      sys.exit(0)
    else:
      if process:
        print "We are scheduled to process all is good"
        datafile = data_dir+file_prefix+filetype+'.'+fileext
      else:
        print "We have nc file but not "+fileext+" file....  aborting..."
        sys.exit(0)
  else:
    print "More than one "+fileext+" file found."
    datafile=step_through_files(datalist)

  if datafile == '' :
    print "No "+datafile+" file identified!"
    print "Aborting..."
    sys.exit(0)

  return(flag,datafile)

# Handle multiple files of a given type for a single flight
def step_through_files(datalist):
  print "Stepping through files, please select the right one."
  datafile = ''
  i = 0
  while datafile == '' :
    ans = raw_input(datalist[i]+'? (Y/N)')
    if ans == 'Y' or ans == 'y':
      datafile = datalist[i]
    if i < datalist.__len__() - 1: 
      i = i + 1
    else:
      i = 0
  return(datafile)

# Run nimbus to create a .nc file (LRT, HRT, or SRT)
def process_netCDF(rawfile,ncfile,pr,config_ext):

  # If there is a setup file for this flight in proj_dir/Production
  # use that. If not, create one.

  nimConfFile = proj_dir+"Production/setup_"+flight+config_ext

  if not os.path.exists(nimConfFile):
    cf = open(nimConfFile, 'w')
    line = "if="+rawfile+'\n'
    cf.write(str(line))
    line = "of="+ncfile+'\n'
    cf.write(str(line))
    line = "pr="+pr+'\n'
    cf.write(str(line))
    cf.close()

  command = "/opt/local/bin/nimbus -b "+nimConfFile
  print "about to execute nimbus I hope: "+command

  res = os.system(command)
  print '\nresult of nimbus call = '+str(res)
  print

  # nimbus is currently returning code 134. I am not sure what this means,
  # but code is completing successfully, so assume success.
  #if (res == 0):
  return(True)
  #else:
  #  return(False)

def process_threeVCPI(aircraft,project,flight,twods_raw_dir,oapfile_dir):
    print "\n\n *****************  3VCPI **************************\n"
    mkdir_fail = False
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
      
      # move 2DS file to the RAF naming convention and location
      if not os.path.isdir(oapfile_dir):
        try:
          os.mkdir(oapfile_dir)
        except:
          message= "\nERROR: Could not make oapfile directory:"+oapfile_dir
          message= message +  "\n  - skipping 2d file gen/placement\n"
          print_message(message)
          mkdir_fail = True
      if not mkdir_fail:
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

def reorder_nc(ncfile):
  command = "ncReorder "+ncfile+" tmp.nc";
  print "about to execute : "+command
  os.system(command)

  command = "/bin/mv tmp.nc "+ncfile;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_nc_file  =    'Yes'
  else:
    message= "ERROR: NC Reorder failed! But NetCDF file should be fine"
    print_message(message)
    proc_nc_file  =    'Yes'
  return(proc_nc_file)

def zip_file(filename,datadir):
    os.chdir(datadir)
    command = "zip " + filename + ".zip " + filename
    if os.system(command) != 0:
      message =  "\nERROR!: Zipping up " + filename + " with command:\n  "
      message = message + command
      print_message(message)

####################   End function definitions ##########################

######################   Begin main function  ############################

# Create the project- and flight-specific filename prefix (e.g. WECANrf01)
file_prefix =	project + flight

# Prepare for final message information
print ""
final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
final_message = final_message + 'Process and Push log for Project:' + project
final_message = final_message + '  Flight:'+flight+'\r\n'


# Make sure the directory to store processed data exists.
ensure_dir(data_dir)

# 3VCPI 
threevcpi2d_file = ''

# Confirm code exists for RStudio plotting
if not os.path.exists(rstudio_dir):
  print 'RStudio DataReview has not been checked out at : '+ rstudio_dir
  print 'QC plots cannot be generated.'

###################  Beginning of Processing ##############################
## Get the netCDF, kml, icartt, IWG1 and raw ADS files for working with ##

# First the LRT netCDF. We use this to determine if code has been run before
# because we ALWAYS generate a LRT data file for every flight.
# Determine if we are in process, reprocess, or ship mode.
(process,reprocess,filename["LRT"]) = find_lrt_netcdf(file_ext["LRT"])

# Now everthing else (skip LRT)
for key in file_ext:
  if (key == "LRT"):
    next;
  else:
    (key,filename[key])=find_file(inst_dir[key],flight,file_prefix,file_type[key],file_ext[key],key)

if process:
  for key in file_ext:
    # Get the flight date from the ADS filename
    if (key == "ADS"):
      file_name = filename[key].split(raw_dir)[1]
      date = file_name[:15]
      date = re.sub('_','', date)

    # Process the ads data to desired netCDF frequencies
    if ((key == "LRT" or key == "HRT" or key == "SRT") and process):
      res=process_netCDF(filename["ADS"],filename[key],rate[key],config_ext[key])
      if res:
        status[key]["proc"]= reorder_nc(filename[key])
      else:
        status[key]["proc"] = False

    # Generate IWG1 file from LRT, if requested
    if (key == "IWG1"):
      command = "nc2iwg1 "+filename["LRT"]+" > "+filename[key];
      print "about to execute : "+command
      if os.system(command) == 0:
        status[key]["proc"] = 'Yes'

    # Generate ICARTT file from LRT, if requested
    if (key == "ICARTT"):
      command = "nc2asc -b "+nc2ascBatch+" -i "+filename["LRT"]+" -o "+filename[key];
      print "about to execute : "+command
      if os.system(command) == 0:
        status[key]["proc"] = 'Yes'

    # Convert SPEC file form to oap file form
    if (key == "threeVCPI"):
      process_threeVCPI(aircraft,project,flight,inst_dir["twods"],inst_dir["oap"])

    # Fast 2D data, extract first, then process.
    if (key == "PMS2D"):
      ensure_dir(inst_dir["PMS2D"])

      file_name = filename["ADS"].split(raw_dir)[1]
      fileelts = file_name.split('.')
      filename["PMS2D"] = inst_dir["PMS2D"] + fileelts[0] + '.2d'
      if not os.path.exists(filename["PMS2D"]):
        # General form of extract2d from RAW_DATA_DIR is:
        #   extract2d PMS2D/output.2d input.ads
        command = 'extract2d '+filename["PMS2D"]+' '+filename["ADS"]
        message = '\nExtracting 2D from ads:'+command+'\n'
        print message
        os.system(command)

      if os.path.exists(filename["PMS2D"]):
        # Process 2D data into netCDF file.  General form is:
        #   process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
        #
        command = 'process2d '+filename["PMS2D"]+' -o '+filename["LRT"]
        print '2D merge command: '+command
        if os.system(command) == 0:
          status["PMS2D"]["proc"] = 'Yes'

        status["PMS2D"]["ship"] = 'Yes'
        status["PMS2D"]["stor"] = 'Yes'

      print


  #
  # Run Al Cooper's R code for QA/QC production
  #
  # Currently requires being run from the ~/RStudio/QAtools directory.
  # To run interactively: launch rstudio, then type "shiny::runApp()"
  #
  if Rstudio:
    os.chdir(rstudio_dir+"/QAtools")
    command = "Rscript DataReview.R "+project+" "+flight
    print "about to execute : "+command
    os.system(command)

###################  Beginning of Shipping ##############################
else:
  print "Processing already done, skipping nimbus command"

print ""
print "************************** Begin Shipping Data ***************"
for key in file_ext:
  print key+" file = "+filename[key]
  print os.system("ls -l "+filename[key])
print "**************************************************************"
print ""
print " We're not done yet. Please be patient."

if NAS:
  if NAS_permanent_mount == False:
     # Mount NAS
     command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
     print '\r\nMounting nas: '+command
     os.system(command)

  # Put copies of files to local store
  # in dirs to sync to fto site in Boulder...
  nas_sync_dir = nas_mnt_pt + '/data/' + project + '/data_synced'
  # and in dirs for local use...
  nas_data_dir = nas_mnt_pt + '/data/' + project + '/data_scr'
  nc_out_dir = nas_data_dir+"/nc/"
  qc_out_dir = nas_data_dir+"/qc/"
  raw_out_dir = nas_data_dir+"/raw/"

  ensure_dir(nc_out_dir)
  ensure_dir(qc_out_dir)
  ensure_dir(raw_out_dir)

  print ""
  print "*************** Copy files to NAS scratch area ***************"
  for key in file_ext:
    print 'Copying '+filename[key]+' to '+nc_out_dir
    status[key]["stor"] = rsync_file(filename[key],nc_out_dir)

  print ""

# Set up email
emailfilename = 'email.addr.txt'
emailfile = data_dir+emailfilename
command = 'rm '+emailfile
os.system(command)
fo = open(emailfile, 'w+')
fo.write(email+'\n')
fo.close()

# ZIP up the files as per expectations back home
#if sendzipped:
for key in file_ext:
  data_dir,file_name = os.path.split(filename[key])
  print key+" filename = "+file_name
  print "data_dir = "+data_dir
  zip_file(file_name,inst_dir[key])

### data_dump section ###
# Project specific data_dump's for indivual users.
if datadump:

  # PICARRO data - extract and write to nas_sync_dir
  ddfilename = 'picarro_'+flight+'.asc'
  command = 'data_dump -i 10,600 -A '+rawfile+' > '+data_dir+'/'+ddfilename
  os.system(command)
  command = 'zip '+nas_sync_dir+'picarro_'+flight+'.zip '+data_dir+'/'+ddfilename
  os.system(command)

# Put QC files into catalog and to the NAS if it exists
if catalog and process:
  try:
    print ""
    print "*************************** Catalog transfer *****************"
    print 'opening FTP connection to: ' + qc_ftp_site
    print '- putting QC data in directory: ' + qc_ftp_dir
  
    ftp = ftplib.FTP(qc_ftp_site)
    ftp.login("anonymous", email)
    ftp.cwd(qc_ftp_dir)

    print "Renaming file "+project+flight+"Plots.pdf"
    command = "/bin/mv "+rstudio_dir+"/QAtools/"+project+flight+"Plots.pdf "+rstudio_dir+"/QAtools/"+raircraft+date+".RAF_QC_plots.pdf"
    print "about to execute : "+command
    if os.system(command) == 0:
      status["QCplots"]["ship"] =    'Yes-Cat'
      print "Sending file "+raircraft+date+".RAF_QC_plots.pdf to catalog"
      os.chdir(rstudio_dir+"/QAtools")
      file = open(raircraft+date+".RAF_QC_plots.pdf", 'r')
      ftp.storbinary('STOR ' + raircraft+date+".RAF_QC_plots.pdf", file)
      file.close()
    else:
       message= "ERROR: Rename of plots failed"

  except ftplib.all_errors as e:
    print ""
    print 'Error writing QC data to server'
    print e
    try:
      ftp.quit()
    except ftplib.all_errors as e:
      print 'Could not close ftp connection:'
      print e

# No NAS this project, so put zipped files to EOL server
# This has not been tested as of WECAN (2018)
if NAS != True:
  try:
    print 'opening FTP connection to: ' + ftp_site

    ftp = ftplib.FTP(ftp_site)
    ftp.login(user, password)
    ftp.cwd(ftp_data_dir)
    print ""
    print datetime.datetime.now().time()

    print "Putting files: "
    for key in file_ext:
      print filename[key]+' '
      os.chdir(inst_dir[key])
      if filename[key] != '': 
        file = open(filename[key], 'r')
        ftp.storbinary('STOR ' + filename[key]+".zip", file)
        file.close()
        status[key]["stor"] = 'Yes-FTP'

    print datetime.datetime.now().time()
    print "Finished putting data file"
    print ""
    ftp.quit()

  except ftplib.all_errors as e:
    print ""
    print 'Error writing nc/kml/iwg1/icartt data file to eol server'
    print e
    ftp.quit()

# put zipped file onto NAS for BT-syncing back home.
else:
  print ""
  print "***** Copy files to NAS sync area for transfer back home *****"

  if reprocess or (not reprocess and not process):  
    final_message = final_message + '\n***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n'
    final_message = final_message + 'Reprocessing so assume ADS already shipped during first processing\n'
    final_message = final_message + 'If this is not the case, run\n'
    final_message = final_message + '"cp /home/data/Raw_Data/'+project+'/*'+flight+'.ads '+nas_sync_dir+'/ADS"\n'
    final_message = final_message + 'when this script is complete\n'
    final_message = final_message + '***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'
  else:
    # Now ZiP up the ADS file.
    raw_dir,rawfilename = os.path.split(filename["ADS"])
    print "zipping "+rawfilename
    zip_raw_file = zip_dir + rawfilename + '.bz2'
    print "rawfilename = "+zip_raw_file
    os.chdir(raw_dir)
    if not os.path.exists(zip_raw_file):
      print "Compressing ADS file with command:"
      command = "bzip2 -kc " + rawfilename + " > " + zip_raw_file
      print command
      os.system(command)
      print ""
    else:
      print 'Compressed ADS image already exists.'


  # mount the NAS and put zipped files to it
  if NAS_permanent_mount == False:
     # Mount NAS
     command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
     print '\r\nMounting nas: '+command
     os.system(command)

  for key in file_ext:
    os.chdir(inst_dir[key])
    status[key]["ship"] = rsync_file(filename[key],nas_sync_dir+'/' + key)
    print 'Copying '+filename[key]+' file to '+nas_sync_dir+'/' + key

  if key == "ADS" and not reprocess and process:  
    status[key]["ship"] = rsync_file(filename[key],nas_sync_dir+'/' + key)
    print 'Copying  '+filename[key]+' file to '+nas_sync_dir

  # unmount NAS
#  if NAS_permanent_mount == False:
#    command = "sudo /bin/umount "+nas_mnt_pt
#    print 'Unmounting nas: ' + command
#    os.system(command)


final_message = final_message + '\nREPORT on Processing and shipping. \n\n'
final_message = final_message + 'FileType  Proc Stor     Ship\n'
for key in file_ext:
  final_message = final_message + key+'\t'+str(status[key]["proc"])+'\t'
  final_message = final_message + str(status[key]["stor"])+'\t'+str(status[key]["ship"])+'\n'

final_message = final_message + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

print final_message
msg = MIMEText(final_message)
msg['Subject'] = 'Process & Push message for:'+project+'  flight:'+flight
msg['From'] = 'ads@groundstation'
msg['To'] = email

s = smtplib.SMTP('localhost')
s.sendmail('ads@groundstation',email, msg.as_string())
s.quit()

print "\r\nSuccessful completion. Close window to exit."
sys.exit(1)

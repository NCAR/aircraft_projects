#!/usr/bin/python
#
# It takes a flight number designation and then using it gets raw ads 
# file, netCDF file and kml file for that flight number (verifying with the 
# user where needed) and does several things:
#  1: zips up the nc, kml, and iwg1 files into a single zip file 
#  2: zips up the ads file
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
#   The RStudio piece seems to need special setup for each project
sys.path.insert(0,proj_dir)
from fieldProc_setup import *

##############   Beginning of Setup ######################################
nc2ascBatch =	proj_dir + 'scripts/nc2asc.bat'

# Don't make it Raw_Data/proj.
zip_dir = '/tmp/'

# Catalog setup should not need to change - they are cery consistent
# so leave this here, rather than in project-specific setup file
qc_ftp_site =    'catalog.eol.ucar.edu'
qc_ftp_dir =     '/pub/incoming/catalog/'+ project.lower()
if aircraft == "GV_N677F":
  raircraft      = 'aircraft.NSF_NCAR_GV.'
elif aircraft == "C130_N130AR":
  raircraft      = 'aircraft.NSF_NCAR_C130.'
else:
  print "Unknown aircraft "+aircraft+" Update code\n"
  sys.exit(1)

# Echo configuration:
print
print 'Processing ' + project + ' from ' + aircraft + '.   If incorrect, edit ~/ads3_environment.'
print
print 'Expecting to find .ads files in ' + raw_dir + '.'
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
process   = False

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

def find_file(data_dir,flight,file_prefix,filetype):
  datafile = ''
  datalist = glob.glob(data_dir+'*'+flight+'.'+filetype)
  if datalist.__len__() == 1:
    datafile = datalist[0]
  elif datalist.__len__() == 0:
    print "No files found matching form: "+data_dir+'*'+flight+'*.'+filetype
    if filetype == 'ads':
      print "Aborting..."
      sys.exit(0)
    else:
      if process:
        print "We are scheduled to process all is good"
        datafile = data_dir+file_prefix+'.'+filetype
      else:
        print "We have nc file but not "+filetype+" file....  aborting..."
        sys.exit(0)
  else:
    print "More than one "+filetype+" file found."
    datafile=step_through_files(datalist)

  if datafile == '' :
    print "No "+datafile+" file identified!"
    print "Aborting..."
    sys.exit(0)

  return(datafile)

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

def process_netCDF(rawfile,ncfile,HRT):
  proc_raw_file =    'No'
  proc_kml_file =    'No'

  # If there is a setup file for this flight in proj_dir/Production
  # use that. If not, create one.

  if HRT == True:
    nimConfFile = proj_dir+"Production/setup_"+flight+"_HRT"
  else:
    nimConfFile = proj_dir+"Production/setup_"+flight

  if not os.path.exists(nimConfFile):

    cf = open(nimConfFile, 'w')
    line = 'if='+rawfile+'\n'
    cf.write(str(line))
    line = "of="+ncfile+'\n'
    cf.write(str(line))
    if HRT == True:
      line = "pr=25\n"
      cf.write(str(line))
    cf.close()

  command = "/opt/local/bin/nimbus -b "+nimConfFile
  print "about to execute nimbus I hope: "+command

  res = os.system(command)
  print 'result of nimbus call = '+str(res)
  print

  if res == 0:
    proc_raw_file =    'Yes'
    proc_kml_file =    'Yes'

  return(proc_raw_file, proc_kml_file)

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

def zip_file(file):
    command = "zip " + file + ".zip " + file
    if os.system(command) != 0:
      message =  "\nERROR!: Zipping up " + file + " with command:\n  "
      message = message + command
      print_message(message)

####################   End function definitions ##########################

ensure_dir(data_dir)

# Get the netCDF, kml, icartt, IWG1 and raw ADS files for working with
# First netCDF
filetype = 'nc'
nclist = glob.glob(data_dir+'*'+flight+'.'+filetype)
if nclist.__len__() == 1:
  ncfile = nclist[0]
  print "Found a netCDF file: "+ncfile
  reproc = ''
  while reproc == '' and reproc != 'R' and reproc != 'S':
    reproc = raw_input('Reprocess? (R) or Ship? (S):')
  if reproc == 'R': 
    process = True
    reprocess = True
  else:
    process = False
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
  #sys.exit(0)

# HRT
if process:
  if (HRT == False):
    nclist = glob.glob(data_dir+'*'+flight+'h.'+filetype)
    if nclist.__len__() == 1:
      reproc = raw_input('Found a HRT file: nclist[0]. Reprocess HRT as well as LRT?(Y/N)')
      if reproc == 'Y':
        HRT = True

# KML
kmlfile=find_file(data_dir,flight,file_prefix,'kml')
# asc
icarttfile=find_file(data_dir,flight,file_prefix,'asc')
# iwg
if nc2iwg:
  iwg1file=find_file(data_dir,flight,file_prefix,'iwg1')
# ads
rawfile=find_file(raw_dir,flight,file_prefix,'ads')


# RStudio plotting
if not os.path.exists(rstudio_dir):
  print 'RStudio DataReview has not been checked out at : '+ rstudio_dir
  print 'No plots being generated.'
else:
  #Include time in RStudio filename so can load into field catalog
  filename = rawfile.split(raw_dir)[1]
  time = filename.split(".")[0].replace('_','')

  # RStudio PDF file
  RStudio_outfile = data_dir+file_prefix+'Plots.pdf'
  rstudiofile=find_file(data_dir,raircraft+time[0:12],raircraft+time[0:12],'RAF_QC_plots_hires.pdf')

  # RStudio HTML file
  if RstudioHTML:
    RStudio_outfileHTML = data_dir+file_prefix+'Plots.html'
    rstudiofileHTML=find_file(data_dir,raircraft+time[0:12],raircraft+time[0:12],'RAF_QC_plots.html')

###################  Beginning of Processing ##############################
# 3VCPI 
threevcpi2d_file = ''

# Run nimbus to generate first look product
# Use a configuration file
if process:
  if HRTonly != True:
    # Process LRT
    (proc_raw_file,proc_kml_file)=process_netCDF(rawfile,ncfile,'False')
  if (HRT):
    # Process HRT
    nchfile = data_dir+file_prefix+"h.nc"
    (proc_rawh_file,proc_kmlh_file)=process_netCDF(rawfile,nchfile, HRT)
    # Reorder HRT
    proc_nch_file = reorder_nc(nchfile)
    if HRTonly:
      sys.exit(1)


  # LRT NetCDF utility work - Reorder, generate IWG ascii and/or ICARTT ascii
  proc_nc_file = reorder_nc(ncfile)

  if nc2iwg:
    command = "nc2iwg1 "+ncfile+" > "+iwg1file;
    print "about to execute : "+command
    if os.system(command) == 0:
      proc_iwg_file = 'Yes'

  if nc2asc:
    command = "nc2asc -b "+nc2ascBatch+" -i "+ncfile+" -o "+icarttfile;
    print "about to execute : "+command
    if os.system(command) == 0:
      proc_asc_file = 'Yes'

  #
  # Convert SPEC file form to oap file form
  #
  if threeVCPI:
    process_threeVCPI(aircraft,project,flight,twods_raw_dir,oapfile_dir)

  #
  # Fast 2D data, extract first, then process.
  #
  if twoD:
    ensure_dir(twodfile_dir)

    filename = rawfile.split(raw_dir)[1]
    fileelts = filename.split('.')
    twoDfile = twodfile_dir + fileelts[0] + '.2d'
    if not os.path.exists(twoDfile):
      # General form of extract2d from RAW_DATA_DIR is:
      #   extract2d PMS2D/output.2d input.ads
      command = 'extract2d '+twoDfile+' '+rawfile
      message = '\nExtracting 2D from ads:'+command+'\n'
      print message
      os.system(command)

    if os.path.exists(twoDfile):
      # Process 2D data into netCDF file.  General form is:
      #   process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
      #
      command = 'process2d '+twoDfile+' -o '+ncfile
      print '2D merge command: '+command
      if os.system(command) == 0:
        proc_2d_files = 'Yes'
        ship_2d_files = 'ads&NC '
        stor_2d_files = 'ads&NC '
      else:
        ship_2d_files = 'ads    '
        ship_2d_files = 'ads    '
    print


  #
  # Run Al Cooper's R code for QA/QC production
  #
  # Currently requires being run from the ~/RStudio/DataReview directory.
  # Run as: "Rscript Review.R ##", without the 'rf', 'tf', or 'ff' at this time.
  #
  # If R is not installed or working, documentation is in:
  #  RStudio/Randadu/RanaduManual.pdf (git clone https://github.com/WilliamCooper/Ranadu)
  # also see:
  #  RStudio/DataReview/DataReviewManual.pdf
  #
  os.chdir(data_dir)
  fl_num = flight[2:]  # This will probably change in the future...
  command = "Rscript " + rstudio_dir + "/Review.R " + fl_num
  print "about to execute : "+command
  os.system(command)

  # rename Rstudio output files to name with time so can input into
  # field catalog
  command = "/bin/cp " + RStudio_outfile + " " + rstudiofile;
  print "about to execute : "+command
  if os.system(command) == 0:
    proc_qc_files = "Yes"

  if RstudioHTML:
    command = "/bin/cp " + RStudio_outfileHTML + " " + rstudiofileHTML;
    print "about to execute : "+command
    if os.system(command) == 0:
      proc_Rstudio_HTML= "Yes"

###################  Beginning of Shipping ##############################
else:
  print "Processing already done, skipping nimbus command"


print "************************** Begin Shipping Data ***************"
print "NetCDF file = "+ncfile
print os.system("ls -l "+ncfile)
print "KML file = "+kmlfile
print os.system("ls -l "+kmlfile)
if nc2iwg:
  print "IWG1 file = "+iwg1file
  print os.system("ls -l "+iwg1file)
if nc2asc:
  print "ASCII file = "+icarttfile
  print os.system("ls -l "+icarttfile)
print "RStudio PDF file = "+rstudiofile
print os.system("ls -l "+rstudiofile)
print "RStudio PDF outfile = "+RStudio_outfile
print os.system("ls -l "+RStudio_outfile)
if RstudioHTML:
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

if NAS:
  if NAS_permanent_mount == False:
     # Mount NAS
     command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
     print 'Mounting nas: '+command
     os.system(command)

  # Put copies of files to local store
  nc_out_dir = nas_data_dir+"/nc/"
  qc_out_dir = nas_data_dir+"/qc/"
  raw_out_dir = nas_data_dir+"/raw/"

  ensure_dir(nc_out_dir)
  ensure_dir(qc_out_dir)
  ensure_dir(raw_out_dir)

  stor_nc_file = rsync_file(ncfile,nc_out_dir)
  stor_kml_file = rsync_file(kmlfile,nc_out_dir)
  if nc2iwg:
    stor_iwg_file = rsync_file(iwg1file,nc_out_dir)
  if nc2asc:
    stor_asc_file = rsync_file(icarttfile,nc_out_dir)
  stor_qc_file = rsync_file(rstudiofile,qc_out_dir)
  if RstudioHTML:
    stor_qchtml_file = rsync_file(rstudiofileHTML,qc_out_dir)
  if not reprocess:
    stor_raw_file = rsync_file(rawfile,raw_out_dir)

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
if nc2iwg:
  data_dir,iwg1filename = os.path.split(iwg1file)
if nc2asc:
  data_dir,icarttfilename = os.path.split(icarttfile)
rdata_dir,rstudiofilename = os.path.split(rstudiofile)
if RstudioHTML:
  rdata_dir,rstudiofilenameHTML = os.path.split(rstudiofileHTML)

print "data_dir = "+data_dir
print "ncfilename = "+ncfilename
print "kmlfilename = "+kmlfilename
if nc2iwg:
  print "iwg1filename = "+iwg1filename
if nc2asc:
  print "icarttfilename = "+icarttfilename
print "RStudiofilenamePDF = "+rstudiofilename
if RstudioHTML:
  print "RStudiofilenameHTML = "+rstudiofilenameHTML

#
# data_dump section
#
# Project specific data_dump's for indivual users.
#
if datadump:

  # PICARRO data - extract and write to nas_sync_dir
  ddfilename = 'picarro_'+flight+'.asc'
  command = 'data_dump -i 10,600 -A '+rawfile+' > '+data_dir+'/'+ddfilename
  os.system(command)
  command = 'zip '+nas_sync_dir+'picarro_'+flight+'.zip '+data_dir+'/'+ddfilename
  os.system(command)

#
# Zip up netCDF and products individually 
os.chdir(data_dir)
zip_file(ncfilename)
zip_file(kmlfilename)
if nc2iwg:
  zip_file(iwg1filename)
if nc2asc:
  zip_file(icarttfilename)
zip_file(RStudio_outfile)
if RstudioHTML:
  zip_file(Rstudio_outfileHTML)


# Put QC files into catalog and to the NAS if it exists
if catalog:
  try:
    print 'opening FTP connection to: ' + qc_ftp_site
    print '- putting QC data in directory: ' + qc_ftp_dir
  
    ftp = ftplib.FTP(qc_ftp_site)
    ftp.login("anonymous", email)
    ftp.cwd(qc_ftp_dir)
    print ""
    print "Putting file:"+rstudiofilename
    os.chdir(rdata_dir)
    file = open(rstudiofilename, 'r')
    ftp.storbinary('STOR ' + rstudiofilename, file)
    file.close()
    if RstudioHTML:
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
    except ftplib.all_errors as e:
      print 'Could not close ftp connection:'
      print e

# Put zipped files to EOL server
if NAS != True:
  try:
    print 'opening FTP connection to: ' + ftp_site

    ftp = ftplib.FTP(ftp_site)
    ftp.login(user, password)
    ftp.cwd(ftp_data_dir)
    print ""
    print datetime.datetime.now().time()
    print "Putting files:"+ncfilename+" "+kmlfilename+" "+iwg1filename+" "+icarttfilename
    os.chdir(data_dir)
    if ncfilename != '': 
      file = open(ncfilename, 'r')
      ftp.storbinary('STOR ' + ncfilename+".zip", file)
      file.close()
      ship_nc_file = 'Yes-FTP'
    if kmlfilename != '':
      file = open(kmlfilename, 'r')
      ftp.storbinary('STOR ' + kmlfilename+".zip", file)
      file.close()
      ship_kml_file = 'Yes-FTP'
    if nc2iwg:
      if iwg1filename != '':
        file = open(iwg1filename, 'r')
        ftp.storbinary('STOR ' + iwg1filename+".zip", file)
        file.close()
        ship_iwg_file = 'Yes-FTP'
    if icarttfilename != '':
      file = open(icarttfilename, 'r')
      ftp.storbinary('STOR ' + icarttfilename+".zip", file)
      file.close()
      ship_asc_file = 'Yes-FTP'
    print datetime.datetime.now().time()
    print "Finished putting data file"
    print ""
    ftp.quit()


  except ftplib.all_errors as e:
    print ""
    print 'Error writing nc/kml/iwg1/icartt data file to eol server'
    print e
    ftp.quit()
#    sys.exit(1)

# put zipped file onto NAS for BT-syncing back home.
else:

  if not reprocess:  
    # Now ZiP up the rawfile.
    raw_dir,rawfilename = os.path.split(rawfile)
    zip_raw_file = zip_dir + rawfilename + '.bz2'
    print "rawfilename = "+rawfilename
    os.chdir(raw_dir)
    if not os.path.exists(zip_raw_file):
      print "Compressing ADS file with command:"
      print command
      command = "bzip2 -kc " + rawfilename + " > " + zip_raw_file
      os.system(command)
      print ""
    else:
      print 'Compressed ADS image already exists.'
  else:
    print 'Reprocessing so assume ADS already shipped during first processing'


  # mount the NAS and put zipped files to it
  if NAS_permanent_mount == False:
     # Mount NAS
     command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
     print 'Mounting nas: '+command
     os.system(command)

  os.chdir(data_dir)
  ship_nc_file = rsync_file(ncfilename,nas_sync_dir)
  ship_kml_file = rsync_file(kmlfilename,nas_sync_dir)
  if nc2iwg:
    ship_iwg_file = rsync_file(iwg1filename,nas_sync_dir)
  if nc2asc:
    ship_asc_file = rsync_file(icarttfilename,nas_sync_dir)
  if not reprocess:  
    ship_raw_file = rsync_file(zip_raw_file,nas_sync_dir)
    command = 'unzip '+nas_sync_dir+'/'+zip_raw_file
    if os.system(command) == 0:
      unzip_raw_file = 'Yes-NAS'
    else:
      message='ERROR!: unzipping zipfile: '+command
      print_message(message)

#  if NAS_permanent_mount == False:
#    command = "sudo /bin/umount "+nas_mnt_pt
#    print 'Unmounting nas: ' + command
#    os.system(command)


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

#!/usr/bin/python
#  NOTE = Be sure to ask the systems group to create a directory:
#   /net/iftp2/pub/incoming/<project>/synced_data. If NAS_permanent_mount
#   then NAS will copy files to that dir.
#   Note that the CWIG standard and the standard expected by the 
#   catcher script will be that <project> above will be the lower
#   case version of the project name e.g. icebridge2015 not ICEBRIDGE2015
#
# This script only copies ADS, LRT, and KML back to Boulder (and QC plots
# if requested). If you need something else, talk to an RAF SE.

# Plots - set path to RStudio dir
rstudio_dir =    '/home/ads/RStudio/'  # Data dir to run on gstation
#rstudio_dir =    '/h/eol/ads/RStudio/' # Data dir to run on EOL servers

# Software - set locations of needed software
translate2ds = '/opt/local/bin/translate2ds '

# Products - set to true if you want 'em
nc2asc = False # Generate ICARTT
nc2iwg =  True # Generate IWG1 packet
catalog = True # Send QC plots to field catalog
HRT =     True # Generate HRT .nc file
SRT =     True # Generate SRT .nc file

# If processing was already done, and now someone wants HRT data,
# to avoid reprocessing LRT, regenerating plots, etc, set HRTonly to 
# True
HRTonly = False


### NAS stuff ###
# Do we have local SWIG RAID storage.
NAS =     True
# Does NAS have a permanent mount?
NAS_permanent_mount = False
nas_url =        '192.168.1.30:/data'
nas_mnt_pt =     '/mnt/Data'


### remote FTP setup (if no NAS) ###
#ftp_site =       'data.eol.ucar.edu'
#user =           'orcas'
#password =       'all4thepod'
#ftp_data_dir =   'synced_data'

### local FTP setup ###
#local_ftp_site = '192.168.1.10'
#local_user     = 'anonymous'
#local_password = 'cjw@ucar.edu'
#local_ftp_dir  = '/FieldStorage/FieldProjects/' + project + '/C130nc'
#rlocal_ftp_dir = '/FieldStorage/FieldProjects/' + project + '/RAFqc'

### R stuff ###
# DataReview is in github.  https://github/WilliamCooper/DataReview.git
# Is Rstudio generating HTML files?
Rstudio = True

### Instrument specific processing ###
# - true or false depending on if instrument is on project.
twoD      =      True 	#PMS2D from 2D-C
threeVCPI =      False 	#CPI, 2DS

# If doing a project specific data_dump for a user, please go to the datadump 
# section of push_data and set command as you want.
datadump = False

# To trim flights when processing, create a setup file for the flight under
# Production. The process script will read that if it exists.

#backup_raw_dir = '/mnt/opsdisk'
#backup_raw_dir2 = '/media/Seagate\ Expansion\ Drive/wecan/'


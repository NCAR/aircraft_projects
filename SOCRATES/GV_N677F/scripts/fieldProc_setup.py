#!/usr/bin/python
#  NOTE = Be sure to ask the systems group to create a directory:
#   /net/iftp2/pub/incoming/<project>/synced_data. If NAS_permanent_mount
#   then NAS will copy files to that dir.
#   Note that the CWIG standard and the standard expected by the 
#   catcher script will be that <project> above will be the lower
#   case version of the project name e.g. icebridge2015 not ICEBRIDGE2015

# Data dir to run on gstation
rstudio_dir =    '/home/ads/RStudio/'
#translate2ds = '/home/local/raf/instruments/3v-cpi/translate2ds/translate2ds '

# Data dir to run on EOL servers
#rstudio_dir =    '/h/eol/ads/RStudio/'
translate2ds = '/opt/local/bin/translate2ds '

# Products - set to true if you want 'em
nc2asc = False
nc2iwg = False
catalog = True
HRT =    False
# If processing was already done, and now someone wants HRT data,
# to avoid reprocessing LRT, regenerating plots, etc, set HRTonly to 
# True
HRTonly = False

### NAS stuff ###
# Do we have local SWIG RAID storage.
NAS =     True
# Does NAS have a permanent mount?
NAS_permanent_mount = True

nas_url =        '192.168.1.46:/data'
nas_mnt_pt =     '/mnt/Data/'
nas_sync_dir =   nas_mnt_pt + '/data/synced_data/'
nas_data_dir =   nas_mnt_pt + '/data/scr_data/'

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
# The Rstudio shiny app is in the repository: https://github.com/WilliamCooper/QAtools 
# Should this script launch the QAtools shiny app?
Rstudio = True

### Instrument specific processing ###
# - true or false depending on if instrument is on project.
twoD      =      True
threeVCPI =      False

# If doing a project specific data_dump for a user, please go to the datadump 
# section of push_data and set command as you want.
datadump = True

# To trim flights when processing, create a setup file for the flight under
# Production. The process script will read that if it exists.

#backup_raw_dir = '/mnt/opsdisk'
#backup_raw_dir2 = '/media/Seagate\ Expansion\ Drive/deepwave/'


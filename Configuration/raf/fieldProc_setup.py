#!/usr/bin/python
#
#   Be sure to ask the systems group to create a directory:
#   /net/ftp/pub/data/incoming/<project> and then to create the tree below it:
#       EOL_data/
#           RAF_data/
#              ADS/
#              PMS2D/
#   If NAS_permanent_mount then NAS will copy files to that dir.
#
#   Note that the CWIG standard and the standard expected by the 
#   catcher script will be that <project> above will be the lower
#   case version of the project name e.g. icebridge2015 not ICEBRIDGE2015
#
# This script currently copies all data files back to Boulder.
# A future upgrade would be to put the proc, ship, and stor booleans (i.e. the
# status hash from push_data) into this file so users could set them here.
# (Would need to modify push_data to use user requests rather than overwriting
# in certain places.
#
# Taylor Thomas - Updates including pulling ADS config to this file from 
# push_data.py, updating this file with the config portion for 
# dist_field_data.py paths for new sync_field_data.py script. 01/16/2019
############################################################################
### Define settings for NAS in the field
#############################################################################
import os
project = 'OTREC'
DATA_DIR = os.environ['DATA_DIR']
RAW_DATA_DIR = os.environ['RAW_DATA_DIR']

# Do we have local SWIG RAID storage.
NAS =     False

# Does NAS have a permanent mount?
NAS_permanent_mount = True
nas_url =        '192.168.1.30:/data'
nas_mnt_pt =     '/mnt/Data/'

#############################################################################
### Define which files should be generated
#############################################################################

# Set to true if you want 'em
ICARTT = False # Generate ICARTT
IWG1 = False # Generate IWG1 packet
RstudioHTML = False # Generate a PDF of the QC plots
catalog = False # Send QC to field catalog
HRT =    False # Generate HRT .nc file
HRTonly = False # If processing was already done, and now someone wants HRT data,
                # to avoid reprocessing LRT, regenerating plots, etc, set HRTonly to 
                # True
SRT = False # Generate SRT .nc file
sendzipped = False # Zips all files before btsync to Boulder
zip_ads = False # Bzips the ads file independently of processed files
# you can have both sendzipped and zip_ads set to True if you want

### Instrument specific processing ###
# True or False depending on if instrument is on project.
PMS2D = True            #PMS2D from 2D-C
threeVCPI = False       #CPI, 2DS

#############################################################################

# Plots - set path to RStudio dir
rstudio_dir =    '/home/ads/RStudio/'  # Data dir to run on gstation
# rstudio_dir =    '/h/eol/ads/RStudio/' # Data dir to run on EOL servers

# Software - set locations of needed software
translate2ds = '/opt/local/bin/translate2ds '

############################################################################
# FTP configuration - not used if using NAS
#############################################################################
ftp_site =       'ftp.eol.ucar.edu'
user =           'anonymous'
qpassword =       'ads@ucar.edu'
ftp_data_dir='pub/data/incoming/otrec/EOL_data/RAF_data'

#############################################################################
# To trim flights when processing, create a setup file for the flight under
# Production. The process script will read that if it exists.
# Configuration for the distribution - modify the following
# Choose between NAS_in_field and FTP
#############################################################################
NAS_in_field =    False                            # Set to false for ftp
FTP = True
dat_parent_dir =  DATA_DIR+'/'     # Where nc files go
rdat_parent_dir = RAW_DATA_DIR+'/' # Where raw ads files go
ftp_parent_dir =  '/net/ftp/pub/data/incoming/otrec/'   # Where nc files go for PIs

############################################################################
# Temp file that exists if program is running.
# Allows script to not clobber itself
#############################################################################
# busy_file = temp_dir+'DIST_PROD'  

#############################################################################
# If doing a project specific data_dump for a user, please go to the datadump
# section of push_data and set command as you want.
#############################################################################
datadump = False

#############################################################################
### local FTP setup ###
#############################################################################
#local_ftp_site = '192.168.1.10'
#local_user     = 'anonymous'
#local_password = 'cjw@ucar.edu'
#local_ftp_dir  = '/FieldStorage/FieldProjects/' + project + '/C130nc'
#rlocal_ftp_dir = '/FieldStorage/FieldProjects/' + project + '/RAFqc'

#############################################################################
# Stuff that I am not sure if push_data uses anymore...
#############################################################################
#nas_sync_dir =   nas_mnt_pt + '/data/synced_data/'
#nas_data_dir =   nas_mnt_pt + '/data/scr_data/'

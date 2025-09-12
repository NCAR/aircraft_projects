#!/usr/bin/env python3
#
#   Be sure to ask the systems group to create a directory:
#   /net/ftp/pub/data/incoming/<project>.
#   If using syncthing, set it up for unidirectional syncing from /var/r1/syncthing_staging on gs3
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

import os
project = os.environ['PROJECT']
DATA_DIR = os.environ['DATA_DIR']
RAW_DATA_DIR = os.environ['RAW_DATA_DIR']
dat_parent_dir =  DATA_DIR+'/'     # Where nc and kml files go
rdat_parent_dir = RAW_DATA_DIR+'/' # Where raw ads files go


### Default email address(es) to send status messages to ###
default_emails = ['srunkel@ucar.edu']
#############################################################################
### Define settings for NAS in the field
#############################################################################
# Do we have local CWIG RAID storage?
NAS = False
# Does NAS have a permanent mount?
NAS_permanent_mount = False
nas_url = '192.168.1.30:/data'
nas_mnt_pt =     '/mnt/Data'

#############################################################################
### FTP configuration - not used if using NAS
#############################################################################
FTP = False
ftp_site = 'ftp.eol.ucar.edu'
user = 'anonymous'
password = ''
ftp_parent_dir = '/net/ftp/pub/data/incoming/maire'# no year identifier in ftp
ftp_data_dir = '/field_sync/EOL_Data/RAF_Data'

#############################################################################
### Define which files should be generated
#############################################################################
ICARTT = False # Generate ICARTT
IWG1 = False # Generate IWG1 packet

HRT = True # Generate HRT .nc file
SRT = False # Generate SRT .nc file
sendzipped = False # Zips all files before btsync to Boulder
zip_ADS = False # Bzips the ads file independently of processed files
# you can have both sendzipped and zip_ads set to True if you want

# Do you want to transfer ADS file back to Boulder (is the connection good enough?)
ship_ADS = True
ship_all_ADS = False

### Instrument specific processing ###
# True or False depending on if instrument is on project.
PMS2D = False            #PMS2D from 2D-C
threeVCPI = False       #CPI, 2DS

QA_notebook = True # Generate HTML of the QA plots
catalog = False # Send QC plots to field catalog, leave as False

#############################################################################
# Plots - set path to RStudio dir
rstudio_dir =    '/home/ads/RStudio/'  # Data dir to run on gstation
#rstudio_dir =    '/h/eol/ads/RStudio/'  # Data dir to run on barolo

# Software - set locations of needed software
translate2ds = '/opt/local/bin/translate2ds '

#############################################################################
# Temp file that exists if program is running.
# Allows script to not clobber itself
#############################################################################
# busy_file = temp_dir+'DIST_PROD'  

#############################################################################
# If doing a project specific data_dump for a user, please go to the datadump
# section of push_data and set command as you want.
#############################################################################
datadump = False

GDRIVE = False
rclone_staging_dir = ''
#############################################################################
SYNCTHING = True
syncthing_staging_dir = f'/var/r1/field_sync/EOL_Data/RAF_Data'


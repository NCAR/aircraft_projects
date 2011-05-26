#!/usr/bin/env python
#
################################################################################
# The ccompanion to this script, archAC.py, must be run from the project
# Production/archive subdir and required that Production/proj.info exist. This 
# was done so the user did not have to know the exact path on the mass store
# where the files were to be stored, but merely needed to chose between
# archiving under /RAF (by passing in 'RAF') or /ATD/DATA (by passing in
# ATDdata).
#
# This script eliminates that requirement, but requires the user to call it
# with the full mass store path where the files are to be archived, e.g.
# '/ATD/DATA/2010/PREDICT/GV_N677F'
#
# Both scripts keep the same filenames, except for RAF LRT and HRT aircraft
# netCDF files, which are renamed to contain flight, date, and time.
#
# Uses archAC.py libs
#
# Created by Janine (Goldstein) Aquino
#
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#  *  Copyright 2010                                                         *
#  *  University Corporation for Atmospheric Research, All Rights Reserved.  *
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
################################################################################
# Import modules used by this code. Some are part of the python library. Others
# were written here and will exist in the same dir as this code.
import sys, getopt, re
import os
import string
import re
from archAC import archRAFdata
from archAC import archraf
from archAC import rpwd

def usage():
    '''
    Usage statement for this code. This is also the only documentation.
    '''
    if len(sys.argv) < 3 or len(sys.argv) > 6:
        print '''"Usage: archAC.py TYPE SDIR SFILES MSSDIR EMAIL
        where:      
            TYPE is data type being archive (SID-2H, ADS, CAMERA)
                (will be used a subdir name on mss)
            SDIR = source file directory
            SFILES = source file suffix (i.e.  ads)
            MSSDIR = MSS dir data will be archived to
	    EMAIL = Where to email MSS confimations to, comma seperated if more than one e-mail (OPTIONAL)'''
        raise SystemExit
    return

#########################
### MAIN
##########################

#Usage:
usage()


# Read the data type from the command line. It must always
# be the second item on the line, after calling the script
type = sys.argv[1]
print "Processing type " + type
    
# Get the rest of the command line arguments off the command line
index = 2
flag = ""
sdir = sys.argv[index]
searchstr = sys.argv[index+1]
location = sys.argv[index+2]
email = ""
if len(sys.argv) >= index+4:
    email = sys.argv[index+3]

# Get the list of files to archive and store to array sfiles
sfiles = []

lines = os.listdir(sdir)
for line in lines:
    match = re.search(searchstr,line)
    if match:
        sfiles.append(line)
sdir = sdir + '/'

# Sort the files to be processed so they are processed in alphabetical order
sfiles.sort()


#Now archive the data!
mssroot = ' '+location+'/'
archraf.archive_files(sdir,sfiles,flag,type,mssroot,email)

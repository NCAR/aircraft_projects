#!/usr/bin/env python
#
################################################################################
# Script to rename RAF netCDF aircraft files to contain flight, date, and time.
# Uses archAC.py libs
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
mssroot = ' mss:'+location+'/'
archraf.archive_files(sdir,sfiles,flag,type,mssroot,email)

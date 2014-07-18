#!/usr/bin/python

#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2010-2012
#

import os
import sys
import glob
import ftplib
import syslog
import time
import datetime
import pg 
import re

def getList(lines,regex):
    result = []
    for l in lines:
        match = re.match(regex,l)
        if match:
            result.append(l)
    result.sort()
    return result

try: 
    database = os.environ['PGDATABASE']
except:
    #database = "real-time"
    database = "real-time-GV"

try: 
    dbhost = os.environ['PGHOST']
except:
    #dbhost = "localhost"
    dbhost = "eol-rt-data.fl-ext.ucar.edu"

# Initialization 
#  *******************  Modify The Following *********************
local_image_dir  = '/var/www/html/flight_data/images/'
labelfile        = local_image_dir+'time_label.jpg'
font             = '/usr/java/latest/lib/fonts/LucidaTypewriterRegular.ttf'

# **************** End of Modify section ************************

# Get information about what's being requested from the DB
cappiFile = ''
conusFile = ''
ltngFile = ''
visFile = ''

# Get the listing and search it for latest images of each type
os.chdir(local_image_dir)

dirlist = os.listdir(local_image_dir)
label = ''

# Infra-red
IRregx = 'satellite.GOES-13.*thermal_IR.jpg'
irlist = getList(dirlist,IRregx)
if len(irlist) != 0:
    irFile = irlist[len(irlist)-1]
    irElmts = []
    irElmts = irFile.split('.')
    label = label + "IR   : "+ irElmts[2][:8] + 'T' + irElmts[2][8:-2] + ':' + irElmts[2][10:] + '\\n'
else:
    label = label + 'IR   : no file available\\n'

# Visible
if len(visFile) == 0:
    print "Making vis label"
    VISregx = 'satellite.GOES-13.*ch1_vis.jpg'
    vislist = getList(dirlist,VISregx)
    if len(vislist) != 0:
        visFile = vislist[len(vislist)-1]
        visElmts = []
        visElmts = visFile.split('.')
        visFile = "VIS  : "+ visElmts[2][:8] + 'T' + visElmts[2][8:-2] + ':' + visElmts[2][10:] + '\\n'
    else:
        visFile = "VIS  : no file available\\n"

label = label + visFile

# NEXRAD Conus - NOTE: might want to do a diff on the last two
#  as it's possible that we get the same image repeatedly 
#  (date/time stamped on the plane)
if len(conusFile) == 0:
    NWSregx = 'NEXRAD.conu*'
    conuslist = getList(dirlist,NWSregx)
    if len(conuslist) != 0:
        conusFile = conuslist[len(conuslist)-1]
        conusElts = []
        conusElts = conusFile.split('.')
        conusFile = "NWS  : "+ conusElts[2][:8] + 'T' + conusElts[2][8:-2] + ':' + conusElts[2][10:] + ''
    else:
        conusFile = "NWS  : no file available"

label = label + conusFile


# Generate the label gif image
command = "convert -background lightblue -fill blue -font " + font + " -pointsize 18 label:'"+label+"' " + labelfile
os.system(command)


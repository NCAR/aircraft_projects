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

# Initialization 
#  *******************  Modify The Following *********************
local_image_dir  = '/var/www/html/flight_data/images/'
labelfile        = local_image_dir+'time_label.jpg'
local_ge_dir     = '/var/www/html/flight_data/GE/'
font             = '/usr/java/latest/lib/fonts/LucidaTypewriterRegular.ttf'

# **************** End of Modify section ************************

####   KML section #####
# Get the listing and search it for latest images of each type
dirlist = os.listdir(local_ge_dir)
label = ''
# CDPHE Data
CDPHEregx = 'gis.CDPHE_Monitor.*.obs.kml'
cdphelist = getList(dirlist,CDPHEregx)
if len(cdphelist) != 0:
    cdpheFile = cdphelist[len(cdphelist)-1]
    cdpheElmts = []
    cdpheElmts = cdpheFile.split('.')
    label = label + "CDPHE: "+ cdpheElmts[2][:8] + 'T' + cdpheElmts[2][8:-2] + ':' + cdpheElmts[2][10:] + "\\n"
else:
    label = label + 'CDPHE: no file available\\n'

####   Image section #####
# Get the listing and search it for latest images of each type
os.chdir(local_image_dir)

dirlist = os.listdir(local_image_dir)

# NEXRAD Conus - NOTE: might want to do a diff on the last two
#  as it's possible that we get the same image repeatedly 
#  (date/time stamped on the plane)
NWSregx = 'NEXRAD.conu*'
conuslist = getList(dirlist,NWSregx)
if len(conuslist) != 0:
    conusFile = conuslist[len(conuslist)-1]
    conusElts = []
    conusElts = conusFile.split('.')
    conusFile = "NWS:     "+ conusElts[2][:8] + 'T' + conusElts[2][8:-2] + ':' + conusElts[2][10:] + "\\n"
else:
    conusFile = "NWS:     no file available\\n"

label = label + conusFile

# Infra-red
IRregx = 'satellite.GOES-13.*thermal-IR.jpg'
irlist = getList(dirlist,IRregx)
if len(irlist) != 0:
    irFile = irlist[len(irlist)-1]
    irElmts = []
    irElmts = irFile.split('.')
    label = label + "IR:          "+ irElmts[2][:8] + 'T' + irElmts[2][8:-2] + ':' + irElmts[2][10:] + "\\n"
else:
    label = label + 'IR:          no file available\\n'

# Visible
VISregx = 'satellite.GOES-13.*ch1_vis.jpg'
vislist = getList(dirlist,VISregx)
if len(vislist) != 0:
    visFile = vislist[len(vislist)-1]
    visElmts = []
    visElmts = visFile.split('.')
    visFile = "VIS:        "+ visElmts[2][:8] + 'T' + visElmts[2][8:-2] + ':' + visElmts[2][10:] + "    "
else:
    visFile = "VIS:          no file available    "

label = label + visFile


####  Done getting listings ####
# Generate the label gif image
command = "convert -background lightblue -fill blue -font " + font + " -pointsize 18 label:'"+label+"' " + labelfile
os.system(command)


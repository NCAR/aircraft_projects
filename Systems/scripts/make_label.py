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
#local_image_dir  = '/var/www/html/flight_data/images/'
local_image_dir  = '/home/local/Systems/scripts/images/'
labelfile        = local_image_dir+'overlayLegend.gif'
font             = '/usr/local/idv/jre/lib/fonts/LucidaTypewriterRegular.ttf'

# **************** End of Modify section ************************

# Get information about what's being requested from the DB
cappiFile = ''
conusFile = ''
ltngFile = ''
visFile = ''

con = pg.connect(dbname=database, host=dbhost, user='ads')
querres = con.query("select value from global_attributes where key='cappi'")
cappilst = querres.getresult()
if len(cappilst) == 0:
    cappiFile = "CAPPI: Off\\n"
    conusFile = "NWS  : Off\\n"
else:
    cappi = (cappilst[0])[0]
    if cappi == 'off':
        cappiFile = "CAPPI: Off\\n"
        conusFile = "NWS  : Off\\n"

querres = con.query("select value from global_attributes where key='lightning'")
ltnglst = querres.getresult()
if len(ltnglst) == 0:
    ltngFile = "LMA  : Off\\n"
else:
    ltng = (ltnglst[0])[0]
    if ltng == 'off':
        ltngFile = "LMA  : Off\\n"

querres = con.query("select value from global_attributes where key='region'")
regionlst = querres.getresult()
if len(regionlst) == 0:
    visFile = "VIS  : Off\\n"
else:
    vis = (regionlst[0])[0]
    if vis == 'off':
        visFile = "VIS  : Off\\n"

con.close()

# Get the listing and search it for latest images of each type
os.chdir(local_image_dir)

dirlist = os.listdir(local_image_dir)
label = ''

# Infra-red
IRregx = 'ops.goes-13.*thermal-IR.jpg'  
irlist = getList(dirlist,IRregx)
if len(irlist) != 0:
    irFile = irlist[len(irlist)-1]
    irElmts = []
    irElmts = irFile.split('.')
    label = label + "IR   : "+ irElmts[2] +'\\n'
else:
    label = label + 'IR   : no file available\\n'

# Visible
if len(visFile) == 0:
    print "Making vis label"
    VISregx = 'ops.goes-13.*ch1_vis.jpg'
    vislist = getList(dirlist,VISregx)
    if len(vislist) != 0:
        visFile = vislist[len(vislist)-1]
        visElmts = []
        visElmts = visFile.split('.')
        visFile = "VIS  : "+ visElmts[2] + '\\n'
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
        conusFile = "NWS  : "+conusElts[2] + '\\n'
    else:
        conusFile = "NWS  : no file available\\n"

label = label + conusFile

#CAPPI gotta get date and height
if len(cappiFile) == 0:
    CAPPIregx = 'radar.NEXRAD_3D*'
    cappilist = getList(dirlist,CAPPIregx)
    if len(cappilist) != 0:
        cappiFile = cappilist[len(cappilist)-1]
        cappiElts = []
        cappiElts = cappiFile.split('.')
        cappiFt = []
        cappiFt = cappiElts[3].split("_")
        cappiFile = "CAPPI: "+cappiElts[2]+" - "+cappiFt[0]+'\\n'
    else:
        cappiFile = "CAPPI: no file available\\n"

label = label + cappiFile

#LMA
if len(ltngFile) == 0:
    LMAregx = 'research.*kft*'
    lmalist = getList(dirlist,LMAregx)
    if len(lmalist) != 0:
        ltngFile = lmalist[len(lmalist)-1]
        lmaElts = []
        lmaElts = ltngFile.split('.')
        lmaFt = []
        lmaFt = lmaElts[3].split("_")
        ltngFile = "LMA  : "+lmaElts[2]+" - "+lmaFt[1]+'\\n'
    else:
        ltngFile = "LMA  : no file available\\n"

label = label + ltngFile



# Generate the label gif image
command = "convert -background lightblue -fill blue -font " + font + " -pointsize 36 label:'"+label+"' " + labelfile
os.system(command)


#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "IDEAS-4-GV"
#echo "Make sure netCDF files have been reordered before archiving!!!"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL janine@ucar.edu

### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT \.nc EOL/2013

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL

### CAMERA
###- This line creates hour tarballs of static camera images and puts them on HPSS
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -a . tar EOL


### MOVIES
### Don't archive preliminary movies to MSS, but do put them in codiac and
### make them orderable.

# FINAL MOVIES
# Archive to /net/archive for preview and delivery, but also copy to HPSS
# for safe keeping.
#/net/work/bin/scripts/mass_store/archAC/archAC.py MOVIES /scr/raf/Raw_Data/$PROJECT/Movies mov EOL

### DGPS
##/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps ads ATDdata

### 3V-CPI
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi roi EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi 2DSCPI EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi 2DSCPIHK EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI  -r /scr/raf/Raw_Data/$PROJECT/3v-cpi log EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi TXT EOL

### SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd EOL

### VCSEL

### KML
/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2013

### NASA_AMES
#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /scr/raf/Prod_Data/$PROJECT/NASA_AMES gz EOL stroble@ucar.edu

### CN 
##/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/CN /scr/raf/Prod_Data/$PROJECT/CN/orig nc EOL

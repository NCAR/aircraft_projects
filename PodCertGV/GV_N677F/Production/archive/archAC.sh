#!/bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "PodCertGV"
#echo "Make sure netCDF files have been reordered before archiving!!!"

### ADS
/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT ads RAF

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf2/Raw_Data/$PROJECT/Chat log RAF

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d.gz ATDdata

### CAMERA - use archcam.510, not this script.

### MOVIES

### DGPS
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf2/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf2/Raw_Data/$PROJECT/sid2h srd RAF

### VCSEL

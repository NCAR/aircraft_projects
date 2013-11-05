#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "PLOWS"
echo "Make sure netCDF files have been reordered before archiving"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads RAF

### LRT - done; replaced with reordered data 6/11/2010
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc ATDdata

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL

### CAMERA - This line creates hour tarballs of static camera images and
### puts them on the mss. 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera jpg ATDdata

### MOVIES
### Don't archive preliminary movies to MSS, but do put them in codiac and
### make them oprderable.

### DGPS
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd RAF

### VCSEL

### CPI Benchtest
/net/work/bin/scripts/mass_store/archAC/archAC.py -r CPI-benchtest /scr/raf/Raw_Data/$PROJECT/CPI roi RAF

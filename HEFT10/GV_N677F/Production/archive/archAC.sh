#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT='HEFT10'
echo "Make sure netCDF files have been reordered before archiving!"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads RAF
#
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf/Prod_Data/$PROJECT nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT ff01.nc ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT ff02.nc ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT rf01.nc ATDdata
#
### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF

### PMS2D - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d.gz ATDdata

### CAMERA - This line creates hour tarballs of static camera images and
### puts them on the mss.  - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera jpg ATDdata

### MOVIES
### Don't archive preliminary movies to MSS, but do put them in codiac and
### make them oprderable.
/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf/Prod_Data/$PROJECT/Camera 0.mp4 ATDdata

### DGPS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps dat ATDdata

### SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd RAF

###KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/kml kml RAF

### DOAS
#/net/work/bin/scripts/mass_store/archAC/archAC.py DOAS /scr/raf/Prod_Data/$PROJECT/DOAS/orig txt RAF

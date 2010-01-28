#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "ADELE"
#echo "Make sure netCDF files have been reordered before archiving!!!"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT ads RAF

### PMS2D - note there is no data for flights 5 and 9 - done 9/16/09, redone 1/13/10
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d ATDdata

### CAMERA - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf2/Raw_Data/$PROJECT/Camera jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf2/Raw_Data/$PROJECT/Camera jpg ATDdata

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf2/Raw_Data/$PROJECT/Chat log RAF

### Unaltered LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/$PROJECT nc RAF

### LRT (merged) - we are not doing any merging for ADELE, just archive reordered LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/$PROJECT nc ATDdata

### KML files - done
#/net/work//bin/scripts/mass_store/archAC/archAC.py KML /scr/raf2/Prod_Data/$PROJECT kml ATDdata

### MOVIES
/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf2/Raw_Data/$PROJECT/Movies mp4 ATDdata

### DGPS
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf2/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H -done
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf2/Raw_Data/$PROJECT/sid2h srd RAF

### VCSEL

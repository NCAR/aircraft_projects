#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "ECLIPSE"
set YEAR = 2016

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads /FS/EOL/$YEAR

### CAMERA - there were no cameras during ECLIPSE. It was a night project.
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg /FS/EOL/$YEAR

########################## Preliminary Data Files ##########################
### Preliminary LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/LRT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT nc FS/EOL/$YEAR

### Preliminary KML
/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase/KML kml /FS/EOL/$YEAR

########################## Production Data Files ##########################
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT Z.nc /FS/EOL/$YEAR

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml /FS/EOL/$YEAR

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d /FS/EOL/$YEAR

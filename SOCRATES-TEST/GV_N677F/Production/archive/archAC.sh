#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "SOCRATES-TEST"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2016

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL/2016

########################## Preliminary Data Files ##########################
### Preliminary LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/LRT /scr/raf/Raw_Data/$PROJECT/field_phase nc EOL/2016

### Preliminary KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase kml EOL/2016

########################## Production Data Files ##########################
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT Z.nc EOL/2016

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2016

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2016

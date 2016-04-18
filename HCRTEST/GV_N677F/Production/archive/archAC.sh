#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "HCRTEST"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2014

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/ jpg EOL/2014

### PRELIMINARY LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/LRT /scr/raf/Raw_Data/$PROJECT/field_data nc EOL/2014

### PRELIMINARY SRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/SRT /scr/raf/Raw_Data/$PROJECT/field_data _sr.nc EOL/2014

### PRELIMINARY KML
/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/KML /scr/raf/Raw_Data/$PROJECT/field_data kml EOL/2014

### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL/2014

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2014

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2014

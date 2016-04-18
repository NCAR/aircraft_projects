#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "NOREASTER"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2015

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/ jpg EOL/2015

### PRELIMINARY LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/LRT /scr/raf/Raw_Data/$PROJECT/field_data 1.nc EOL/2015
/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/LRT /scr/raf/Raw_Data/$PROJECT/field_data 2.nc EOL/2015

### PRELIMINARY SRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/SRT /scr/raf/Raw_Data/$PROJECT/field_data _sr.nc EOL/2015

### PRELIMINARY KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/KML /scr/raf/Raw_Data/$PROJECT/field_data kml EOL/2015

### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL/2015

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2015

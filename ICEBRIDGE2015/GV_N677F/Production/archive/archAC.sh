#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "ICEBRIDGE2015"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2014

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2014

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf15 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff02 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff04 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff05 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_tf01 jpg EOL/2014

### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT Z.nc EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT ZPC.nc EOL/2014

### IWG1
#/net/work/bin/scripts/mass_store/archAC/archAC.py IWG1 /scr/raf/Prod_Data/$PROJECT/LRT/IWG1 iwg1 EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py IWG1 /scr/raf/Prod_Data/$PROJECT/LRT/IWG1 ZPC.iwg1 EOL/2014

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/KML kml EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/KML V1_2.kml EOL/2014

### HRT
/net/work/bin/scripts/mass_store/archAC/archAC.py HRT/V1\.4 /scr/raf/Prod_Data/$PROJECT/HRT h.nc EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT hPC.nc EOL/2014

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/HRT/KML h.kml EOL/2014


### PRELIMINARY KML - puts files in the wrong place, you need to then login
#to HPSS and move them under field phase dir.
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Raw_Data/$PROJECT/field_phase/GVnc kml EOL/2014

### MTP
#/net/work/bin/scripts/mass_store/archAC/archAC.py MTP /scr/raf/Prod_Data/$PROJECT/MTP NGV EOL/2014

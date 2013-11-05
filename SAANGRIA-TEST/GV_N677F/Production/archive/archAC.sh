#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "SAANGRIA-TEST"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL

#### CAMERA - This line creates hour tarballs of static camera images and
#### puts them on the hpss. 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL

### LRT
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL

### HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT nc EOL

### KML
/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL

### MOVIE
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf/Prod_Data/$PROJECT/movies mp4 EOL

### MTP
#/net/work/bin/scripts/mass_store/archAC/archAC.py mtp /scr/raf/Prod_Data/$PROJECT NGV EOL


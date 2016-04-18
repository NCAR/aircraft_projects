#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "FRAPPE"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2014

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2014

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL/2014


### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT Z.nc EOL/2014

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format R2.ict EOL/2014

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2014

### HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT nc EOL/2014

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml EOL/2014

### CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO /scr/raf/Prod_Data/$PROJECT/CO ict EOL/2014

### CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2CH4 /scr/raf/Prod_Data/$PROJECT/CO2CH4 ict EOL/2014

### HARP ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP /scr/raf/Prod_Data/$PROJECT/HARP ict EOL/2014

### GT-CIMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict EOL/2014

### NONO2O3 ICT
/net/work/bin/scripts/mass_store/archAC/archAC.py NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict EOL/2014


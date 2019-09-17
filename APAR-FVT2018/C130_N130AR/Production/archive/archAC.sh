#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "APAR-FVT2018"

### ADS 
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf_Raw_Data/$PROJECT ads FS/EOL/2018 taylort@ucar.edu

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg FS/EOL/2018

########################## Preliminary Data Files ##########################
### Preliminary LRT  
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/LRT /scr/raf/Prod_Data/$PROJECT/field_phase/LRT nc FS/EOL/2018 taylort@ucar.edu

### Preliminary SRT  
/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/SRT /scr/raf/Prod_Data/$PROJECT/field_phase/SRT nc FS/EOL/2018 taylort@ucar.edu

## Preliminary HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/HRT /scr/raf/Raw_Data/$PROJECT/field_phase/HRT nc FS/EOL/2018

### Preliminary KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/KML /scr/raf/Prod_Data/$PROJECT/field_phase/KML kml FS/EOL/2018 taylort@ucar.edu

########################## Production Data Files ##########################
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL/2016
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc FS/EOL/2016

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format ict EOL/2016

### PMS2D - Done Aug 17, 2016
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2016

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2016

### HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT nc EOL/2016

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml EOL/2016

### CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO /scr/raf/Prod_Data/$PROJECT/CO ict EOL/2016

### CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2CH4 /scr/raf/Prod_Data/$PROJECT/CO2CH4 ict EOL/2016

### HARP ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP /scr/raf/Prod_Data/$PROJECT/HARP ict EOL/2016

### GT-CIMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict EOL/2016

### NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict EOL/2016


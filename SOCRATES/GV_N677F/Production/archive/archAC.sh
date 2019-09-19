#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "SOCRATES"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads FS/EOL/2018

### CAMERA - RUN THIS LINE FROM /scr/raf/Raw_Data/ so temp files will go
# there and not fill up /net/jlocal
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff01/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff02/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff03/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff04/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff05/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff06/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff07/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff08/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff09/ jpg FS/EOL/2018
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff10/ jpg FS/EOL/2018

########################## Preliminary Data Files ##########################
### Preliminary LRT 
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/LRT/version0_2 /scr/raf/local_data/$PROJECT/LRT nc FS/EOL/2018

### Preliminary LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py preliminary/ICARTT /scr/raf/Raw_Data/$PROJECT/preliminary/icartt asc EOL/2018

### Preliminary KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase/LRT/KML kml FS/EOL/2018

### Preliminary HRT 
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/HRT /scr/raf/Raw_Data/$PROJECT/field_phase/HRT nc FS/EOL/2018

### Preliminary SRT 
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/SRT /scr/raf/Raw_Data/$PROJECT/field_phase/SRT nc FS/EOL/2018


### Preliminary HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KMLh /scr/raf/Raw_Data/$PROJECT/field_phase/HRT/kml kml FS/EOL/2018

### Preliminary CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO /scr/raf/Raw_Data/$PROJECT/field_phase/CO ict EOL/2018

### Preliminary CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO2CH4 /scr/raf/Raw_Data/$PROJECT/field_phase/CO2CH4 ict EOL/2018

### Preliminary NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/NONOyO3 /scr/raf/Raw_Data/$PROJECT/field_phase/NO_NOy_O3 ict EOL/2018

### Preliminary TOGA ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOGA /scr/raf/Raw_Data/$PROJECT/field_phase/TOGA ict EOL/2018

### Preliminary TOF-AMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOF-AMS /scr/raf/Raw_Data/$PROJECT/field_phase/CU-HRAMS ict EOL/2018

### Preliminary HARP Actinic Flux ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/HARP /scr/raf/Raw_Data/$PROJECT/field_phase/HARP_Jvalues ict EOL/2018

### Preliminary ARNOLD ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/ARNOLD /scr/raf/Raw_Data/$PROJECT/field_phase/ARNOLD ict EOL/2018


########################## Production Data Files ##########################
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/version1_3 /scr/raf/Prod_Data/$PROJECT/LRT/V1.3_20190412 nc FS/EOL/2018 taylort@ucar.edu

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/KML kml FS/EOL/2018 taylort@ucar.edu

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py ICARTT /scr/raf/Prod_Data/$PROJECT asc EOL/2018

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d FS/EOL/2018


### HRT
/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT/V1.0_20190412 nc FS/EOL/2018 taylort@ucar.edu

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml EOL/2018

### CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO /scr/raf/Prod_Data/$PROJECT/CO ict EOL/2018

### CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2CH4 /scr/raf/Prod_Data/$PROJECT/CO2CH4 ict EOL/2018

### HARP ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP /scr/raf/Prod_Data/$PROJECT/HARP ict EOL/2018

### GT-CIMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict EOL/2018

### NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict EOL/2018


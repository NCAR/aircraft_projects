#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and YEAR and uncomment each command to archive that data type.

###############
#   Project   #
###############
setenv PROJECT SPICULE
setenv YEAR 2021

### ADS 
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads FS/EOL/$YEAR taylort@ucar.edu

### CAMERA
/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg FS/EOL/$YEAR taylort@ucar.edu

########################## Preliminary Data Files #############################
### Preliminary LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/LRT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT nc FS/EOL/$YEAR

### Preliminary LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/LRT/ICARTT /scr/raf/Raw_Data/$PROJECT/field_phase/C130nc/ICARTT ict FS/EOL/$YEAR

### Preliminary LRT IWG1
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/IWG1 /scr/raf/Raw_Data/$PROJECT/field_phase/C130nc/IWG1 iwg1 FS/EOL/$YEAR

### Preliminary KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/KML /scr/raf/Raw_Data/$PROJECT/field_phase/KML kml FS/EOL/$YEAR

### Preliminary CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO /scr/raf/Raw_Data/$PROJECT/field_phase/CO ict FS/EOL/$YEAR

### Preliminary CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO2CH4 /scr/raf/Raw_Data/$PROJECT/field_phase/CO2CH4 ict FS/EOL/$YEAR

### Preliminary NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/NONOyO3 /scr/raf/Raw_Data/$PROJECT/field_phase/NO_NOy_O3 ict FS/EOL/$YEAR

### Preliminary TOGA ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOGA /scr/raf/Raw_Data/$PROJECT/field_phase/TOGA ict FS/EOL/$YEAR

### Preliminary TOF-AMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOF-AMS /scr/raf/Raw_Data/$PROJECT/field_phase/CU-HRAMS ict FS/EOL/$YEAR

### Preliminary HARP Actinic Flux ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/HARP /scr/raf/Raw_Data/$PROJECT/field_phase/HARP_Jvalues ict FS/EOL/$YEAR

### Preliminary ARNOLD ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/ARNOLD /scr/raf/Raw_Data/$PROJECT/field_phase/ARNOLD ict FS/EOL/$YEAR


########################## Production Data Files ##########################
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc FS/EOL/$YEAR

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format ict FS/EOL/$YEAR

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d FS/EOL/$YEAR

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml FS/EOL/$YEAR

### HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT nc FS/EOL/$YEAR

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml FS/EOL/$YEAR

### CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO /scr/raf/Prod_Data/$PROJECT/CO ict FS/EOL/$YEAR

### CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2CH4 /scr/raf/Prod_Data/$PROJECT/CO2CH4 ict FS/EOL/$YEAR

### HARP ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP /scr/raf/Prod_Data/$PROJECT/HARP ict FS/EOL/$YEAR

### GT-CIMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict FS/EOL/$YEAR

### NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict FS/EOL/$YEAR


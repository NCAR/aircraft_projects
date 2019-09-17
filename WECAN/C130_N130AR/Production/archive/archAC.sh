#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and YEAR and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "WECAN"
set YEAR = 2018

### ADS 
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads FS/EOL/$YEAR taylort@ucar.edu

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images jpg FS/EOL/$YEAR taylort@ucar.edu

########################## Preliminary Data Files #############################
### Preliminary LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/LRT/Version03 /scr/raf/Prod_Data/$PROJECT/field_data/LRT/Version03 .nc FS/EOL/$YEAR taylort@ucar.edu

### Preliminary HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/HRT /scr/raf_data/$PROJECT/field_data h.nc FS/EOL/$YEAR taylort@ucar.edu

### Preliminary SRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/SRT /scr/raf_data/$PROJECT/field_data s.nc FS/EOL/$YEAR taylort@ucar.edu

### Preliminary LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/LRT/ICARTT /scr/raf/Raw_Data/$PROJECT/field_phase/C130nc/ICARTT ict FS/EOL/$YEAR

### Preliminary LRT IWG1
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD/IWG1 /scr/raf/Raw_Data/$PROJECT/field_phase/C130nc/IWG1 iwg1 FS/EOL/$YEAR

### Preliminary KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KML /scr/raf_data/$PROJECT/field_data kml FS/EOL/$YEAR taylort@ucar.edu

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
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/Version1.1_20190517 /scr/raf/Prod_Data/$PROJECT/LRT/V1.1_20190517 nc FS/EOL/$YEAR taylort@ucar.edu

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1.1_20190517 ICARTT /scr/raf/Prod_Data/$PROJECT/LRT/V1.1_20190517/ICARTT ict FS/EOL/$YEAR taylort@ucar.edu

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d FS/EOL/$YEAR taylort@ucar.edu

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/KML kml FS/EOL/$YEAR taylort@ucar.edu

### HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT nc FS/EOL/$YEAR

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml FS/EOL/$YEAR

### CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO_N2O_H2O /scr/raf/Prod_Data/$PROJECT/CO_N2O_H2O ict FS/EOL/$YEAR taylort@ucar.edu

### CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2_CH4_CO_H2O /scr/raf/Prod_Data/$PROJECT/CO2_CH4_CO_H2O ict FS/EOL/$YEAR taylort@ucar.edu

### HARP ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP /scr/raf/Prod_Data/$PROJECT/HARP ict FS/EOL/$YEAR

### GT-CIMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict FS/EOL/$YEAR

### NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict FS/EOL/$YEAR


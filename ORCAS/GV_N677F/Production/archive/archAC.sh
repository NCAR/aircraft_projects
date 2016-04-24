#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "ORCAS"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2016

### CAMERA - done - RUN THIS LINE FROM /scr/raf/Raw_Data/ so temp files will go
### there and not fill up /net/jlocal
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL/2016

########################## Preliminary Data Files ##########################
### Preliminary LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/LRT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT nc EOL/2016
#/net/work/bin/scripts/mass_store/archAC/archAC.py PRELIMINARY/LRT /scr/raf_data/WINTER nc EOL/2016

### Preliminary LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/ICARTT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT/icartt asc EOL/2016

### Preliminary KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase/LRT/kml ff02.kml EOL/2016

### Preliminary HRT 
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/HRT /scr/raf/Raw_Data/$PROJECT/field_phase/HRT nc EOL/2016

### Preliminary HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KMLh /scr/raf/Raw_Data/$PROJECT/field_phase/HRT kml EOL/2016

### Preliminary CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO /scr/raf/Raw_Data/$PROJECT/field_phase/CO ict EOL/2016

### Preliminary CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO2CH4 /scr/raf/Raw_Data/$PROJECT/field_phase/CO2CH4 ict EOL/2016

### Preliminary NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/NONOyO3 /scr/raf/Raw_Data/$PROJECT/field_phase/NO_NOy_O3 ict EOL/2016

### Preliminary TOGA ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOGA /scr/raf/Raw_Data/$PROJECT/field_phase/TOGA ict EOL/2016

### Preliminary TOF-AMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOF-AMS /scr/raf/Raw_Data/$PROJECT/field_phase/CU-HRAMS ict EOL/2016

### Preliminary HARP Actinic Flux ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/HARP /scr/raf/Raw_Data/$PROJECT/field_phase/HARP_Jvalues ict EOL/2016

### Preliminary ARNOLD ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/ARNOLD /scr/raf/Raw_Data/$PROJECT/field_phase/ARNOLD ict EOL/2016


########################## Production Data Files ##########################
### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL/2016

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format ict EOL/2016

### PMS2D
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


#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "CSET"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2015

### CAMERA - done - RUN THIS LINE FROM /scr/raf/Raw_Data/ so temp files will go
### there and not fill up /net/jlocal
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL/2015

### CPI ROI - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/ROI -r /scr/raf/Raw_Data/$PROJECT/3v_cpi/CPI roi EOL/2015
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/2DS -r /scr/raf/Raw_Data/$PROJECT/3v_cpi/2DS *  EOL/2015
########################## Preliminary Data Files ##########################
### Preliminary LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/LRT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT nc EOL/2015
#/net/work/bin/scripts/mass_store/archAC/archAC.py PRELIMINARY/LRT /scr/raf_data/WINTER nc EOL/2015

### Preliminary KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase/LRT/KML kml EOL/2015
#/net/work/bin/scripts/mass_store/archAC/archAC.py PRELIMINARY/KML /scr/raf_data/WINTER kml EOL/2015

### Preliminary CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO /scr/raf/Raw_Data/$PROJECT/field_phase/CO ict EOL/2015

### Preliminary CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/CO2CH4 /scr/raf/Raw_Data/$PROJECT/field_phase/CO2CH4 ict EOL/2015

### Preliminary NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/NONOyO3 /scr/raf/Raw_Data/$PROJECT/field_phase/NO_NOy_O3 ict EOL/2015

### Preliminary TOGA ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOGA /scr/raf/Raw_Data/$PROJECT/field_phase/TOGA ict EOL/2015

### Preliminary TOF-AMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/TOF-AMS /scr/raf/Raw_Data/$PROJECT/field_phase/CU-HRAMS ict EOL/2015

### Preliminary HARP Actinic Flux ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/HARP /scr/raf/Raw_Data/$PROJECT/field_phase/HARP_Jvalues ict EOL/2015

### Preliminary ARNOLD ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py FIELD_INTERNAL_ONLY/ARNOLD /scr/raf/Raw_Data/$PROJECT/field_phase/ARNOLD ict EOL/2015


########################## Production Data Files ##########################
### LRT
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/version1.1 /scr/raf/Prod_Data/$PROJECT [0-9].nc EOL/2015

### LRT ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format ict EOL/2015

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2015


### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2015

### HRT
/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT h.nc EOL/2015

### HRT KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml EOL/2015

### CO ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO /scr/raf/Prod_Data/$PROJECT/CO ict EOL/2015

### CO2CH4 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2CH4 /scr/raf/Prod_Data/$PROJECT/CO2CH4 ict EOL/2015

### HARP ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP /scr/raf/Prod_Data/$PROJECT/HARP ict EOL/2015

### GT-CIMS ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict EOL/2015

### NONO2O3 ICT
#/net/work/bin/scripts/mass_store/archAC/archAC.py NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict EOL/2015


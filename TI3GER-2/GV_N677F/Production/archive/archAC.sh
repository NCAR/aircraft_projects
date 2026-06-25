#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and YEAR and uncomment each command to archive that data type.

###############
#   Project   #
###############
setenv PROJECT "TI3GER-2"
setenv YEAR 2026
setenv PLATFORM "GV_N677F"
setenv ARCHIVE_SCRIPT "/net/jlocal/projects/Configuration/scripts/archAC.py"
setenv CS_LOCATION "/glade/campaign/eol/archive/"
setenv EMAIL "jenframe@ucar.edu"
setenv projectlower "ti3ger-2"
setenv platformlower "gv_n677f"
########################## Raw Data Files ##############################
### ADS 
#$ARCHIVE_SCRIPT ADS /scr/raf/Raw_Data/$PROJECT ads $CS_LOCATION$YEAR/ $EMAIL

### CAMERA
#$ARCHIVE_SCRIPT CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f rf01 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f rf02 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f rf03 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f rf04 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f rf05 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f rf06 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f ff01 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f ff02 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f pp01 /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL
#$ARCHIVE_SCRIPT CAMERA -f <flight> /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL

########################## Preliminary Data Files #############################
### Preliminary LRT
#$ARCHIVE_SCRIPT FIELD/LRT /scr/raf_data/$PROJECT/field_data nc /net/archive/data/ $EMAIL

### Preliminary HRT
#$ARCHIVE_SCRIPT FIELD/HRT /scr/raf_data/$PROJECT/field_data/HRT nc $CS_LOCATION$YEAR/ $EMAIL

### Preliminary SRT
#$ARCHIVE_SCRIPT FIELD/SRT /scr/raf_data/$PROJECT/field_data/SRT nc $CS_LOCATION$YEAR/ $EMAIL

### Preliminary KML
#$ARCHIVE_SCRIPT FIELD/KML /scr/raf_data/$PROJECT/field_data kml $CS_LOCATION$YEAR/ $EMAIL

### Preliminary LRT ICT
#$ARCHIVE_SCRIPT FIELD/ICARTT /scr/raf_data/$PROJECT/field_data ict $CS_LOCATION$YEAR/ $EMAIL

### Preliminary LRT IWG1
#$ARCHIVE_SCRIPT field_phase/IWG1 /scr/raf/Raw_Data/$PROJECT/field_phase/C130nc/IWG1 iwg1 $CS_LOCATION$YEAR $EMAIL

### Preliminary KML
#$ARCHIVE_SCRIPT field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase/KML kml $CS_LOCATION$YEAR $EMAIL

###Preliminary F2DS
#$ARCHIVE_SCRIPT FIELD/F2DS -t /scr/raf/Raw_Data/$PROJECT/F2DS F2DS $CS_LOCATION$YEAR/ $EMAIL

### Preliminary CO ICT
#ARCHIVE_SCRIPT field_phase/CO /scr/raf/Raw_Data/$PROJECT/field_phase/CO ict $CS_LOCATION$YEAR $EMAIL

### Preliminary CO2CH4 ICT
#$ARCHIVE_SCRIPT field_phase/CO2CH4 /scr/raf/Raw_Data/$PROJECT/field_phase/CO2CH4 ict $CS_LOCATION$YEAR $EMAIL

### Preliminary NONO2O3 ICT
#$ARCHIVE_SCRIPT field_phase/NONOyO3 /scr/raf/Raw_Data/$PROJECT/field_phase/NO_NOy_O3 ict $CS_LOCATION$YEAR $EMAIL

### Preliminary TOGA ICT
#$ARCHIVE_SCRIPT field_phase/TOGA /scr/raf/Raw_Data/$PROJECT/field_phase/TOGA ict $CS_LOCATION$YEAR $EMAIL

### Preliminary TOF-AMS ICT
#$ARCHIVE_SCRIPT field_phase/TOF-AMS /scr/raf/Raw_Data/$PROJECT/field_phase/CU-HRAMS ict $CS_LOCATION$YEAR $EMAIL

### Preliminary HARP Actinic Flux ICT
#$ARCHIVE_SCRIPT field_phase/HARP /scr/raf/Raw_Data/$PROJECT/field_phase/HARP_Jvalues ict $CS_LOCATION$YEAR $EMAIL

### Preliminary ARNOLD ICT
#ARCHIVE_SCRIPT field_phase/ARNOLD /scr/raf/Raw_Data/$PROJECT/field_phase/ARNOLD ict $CS_LOCATION$YEAR $EMAIL

########################## Production Data Files ##########################
### LRT
#$ARCHIVE_SCRIPT LRT /scr/raf/Prod_Data/$PROJECT nc /net/archive/data/$projectlower/aircraft/$platformlower/LRT $EMAIL

### LRT ICT
#$ARCHIVE_SCRIPT ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format ict $CS_LOCATION$YEAR $EMAIL

### PMS2D
#$ARCHIVE_SCRIPT PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d $CS_LOCATION$YEAR $EMAIL

### KML
#$ARCHIVE_SCRIPT KML /scr/raf/Prod_Data/$PROJECT kml $CS_LOCATION$YEAR $EMAIL

### HRT
#$ARCHIVE_SCRIPT HRT /scr/raf/Prod_Data/$PROJECT/HRT nc $CS_LOCATION$YEAR $EMAIL

### HRT KML
#$ARCHIVE_SCRIPT KMLh /scr/raf/Prod_Data/$PROJECT/HRT kml $CS_LOCATION$YEAR $EMAIL

### CO ICT
#$ARCHIVE_SCRIPT CO /scr/raf/Prod_Data/$PROJECT/CO ict $CS_LOCATION$YEAR $EMAIL

### CO2CH4 ICT
#$ARCHIVE_SCRIPT CO2CH4 /scr/raf/Prod_Data/$PROJECT/CO2CH4 ict $CS_LOCATION$YEAR $EMAIL

### HARP ICT
#$ARCHIVE_SCRIPT HARP /scr/raf/Prod_Data/$PROJECT/HARP ict $CS_LOCATION$YEAR $EMAIL

### GT-CIMS ICT
#$ARCHIVE_SCRIPT GT-CIMS /scr/raf/Prod_Data/$PROJECT/GT-CIMS ict $CS_LOCATION$YEAR $EMAIL

### NONO2O3 ICT
#$ARCHIVE_SCRIPT NONO2O3 /scr/raf/Prod_Data/$PROJECT/NONO2O3 ict $CS_LOCATION$YEAR $EMAIL

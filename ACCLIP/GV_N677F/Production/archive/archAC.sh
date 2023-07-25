#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and YEAR and uncomment each command to archive that data type.

###############
#   Project   #
###############
setenv PROJECT "ACCLIP"
setenv YEAR 2022
setenv PLATFORM "GV_N677F"
setenv ARCHIVE_SCRIPT "/net/jlocal/projects/Configuration/scripts/archAC.py"
setenv CS_LOCATION "/glade/campaign/eol/archive/"
setenv EMAIL "taylort@ucar.edu"
setenv projectlower "acclip"
setenv platform_lower "gv_n677f"
########################## Raw Data Files ##############################
### ADS 
#$ARCHIVE_SCRIPT ADS /scr/raf/Raw_Data/$PROJECT ads $CS_LOCATION$YEAR $EMAIL

### CAMERA
#$ARCHIVE_SCRIPT CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL

########################## Preliminary Data Files #############################
### Preliminary LRT
#$ARCHIVE_SCRIPT field_phase/LRT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT nc field_phase/LRT $EMAIL

### Preliminary LRT ICT
#$ARCHIVE_SCRIPT field_phase/ICARTT/RA /scr/raf/Raw_Data/$PROJECT/field_phase/ICARTT/RA ict $CS_LOCATION$YEAR $EMAIL

### Preliminary LRT IWG1
#$ARCHIVE_SCRIPT field_phase/IWG1 /scr/raf/Raw_Data/$PROJECT/field_phase/C130nc/IWG1 iwg1 $CS_LOCATION$YEAR $EMAIL

### Preliminary KML
#$ARCHIVE_SCRIPT field_phase/KML /scr/raf/Raw_Data/$PROJECT/field_phase/KML kml $CS_LOCATION$YEAR $EMAIL

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
#$ARCHIVE_SCRIPT LRT /scr/raf/Prod_Data/$PROJECT/LRT/version1_0 nc /net/archive/data/$projectlower/aircraft/$platform_lower/LRT/version1_0 $EMAIL

### LRT ICT
#$ARCHIVE_SCRIPT ICARTT /scr/raf/Prod_Data/$PROJECT/ICARTT_format ict $CS_LOCATION$YEAR $EMAIL

### PMS2D
#$ARCHIVE_SCRIPT PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d $CS_LOCATION$YEAR $EMAIL

### KML
#$ARCHIVE_SCRIPT KML /scr/raf/Prod_Data/$PROJECT/KML kml $CS_LOCATION$YEAR $EMAIL

### HRT
$ARCHIVE_SCRIPT HRT /scr/raf_data/$PROJECT/hrt/version0_9 nc $CS_LOCATION$YEAR $EMAIL

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

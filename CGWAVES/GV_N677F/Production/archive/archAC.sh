#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and YEAR and uncomment each command to archive that data type.

###############
#   Project   #
###############
setenv PROJECT "CGWAVES"
setenv YEAR 2025
setenv PLATFORM "GV_N677F"
setenv ARCHIVE_SCRIPT "/net/jlocal/projects/Configuration/scripts/archAC.py"
setenv CS_LOCATION "/glade/campaign/eol/archive/"
setenv EMAIL "srunkel@ucar.edu"
setenv projectlower "cgwaves"
setenv platformlower "gv_n677f"
########################## Raw Data Files ##############################
### ADS 
#$ARCHIVE_SCRIPT ADS /scr/raf/Raw_Data/$PROJECT ads $CS_LOCATION$YEAR/ $EMAIL

### CAMERA
#$ARCHIVE_SCRIPT CAMERA -r /scr/raf/Raw_Data/$PROJECT/camera_images jpg $CS_LOCATION$YEAR $EMAIL

########################## Preliminary Data Files #############################

### Preliminary LRT
$ARCHIVE_SCRIPT FIELD/LRT /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/LRT nc /net/archive/data/ $EMAIL

### Preliminary KML
$ARCHIVE_SCRIPT FIELD/KML /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/KML kml $CS_LOCATION$YEAR/ $EMAIL

###Preliminary F2DS
$ARCHIVE_SCRIPT FIELD/F2DS -t /scr/raf/Raw_Data/$PROJECT/F2DS F2DS $CS_LOCATION$YEAR/ $EMAIL

########################## Production Data Files ##########################

### LRT
#$ARCHIVE_SCRIPT LRT /scr/raf/Prod_Data/$PROJECT nc /net/archive/data/ $EMAIL

### PMS2D
$ARCHIVE_SCRIPT PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d $CS_LOCATION$YEAR $EMAIL

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

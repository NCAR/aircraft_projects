#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and YEAR and uncomment each command to archive that data type.

###############
#   Project   #
###############
setenv PROJECT "CAESAR"
setenv YEAR 2024
setenv ARCHIVE_SCRIPT "/net/jlocal/projects/Configuration/scripts/archAC.py"
setenv CS_LOCATION "/glade/campaign/eol/archive/"
setenv EMAIL "srunkel@ucar.edu"
setenv projectlower "caesar"
setenv platform_lower "c130_n130ar"
########################## Raw Data Files ##############################
### ADS 
#$ARCHIVE_SCRIPT ADS /scr/raf/Raw_Data/$PROJECT ads $CS_LOCATION$YEAR/ $EMAIL

### CAMERA
#$ARCHIVE_SCRIPT CAM /scr/raf/Raw_Data/$PROJECT/camera_images/hourly_tar tar $CS_LOCATION$YEAR/ $EMAIL 



########################## Preliminary Data Files #############################
### Preliminary LRT
#$ARCHIVE_SCRIPT LRT/v0.3 /scr/raf_data/$PROJECT/LRT nc /net/archive/data/ $EMAIL

### Preliminary LRT
#$ARCHIVE_SCRIPT FIELD/LRT /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/LRT nc /net/archive/data/ $EMAIL

### Preliminary SRT
#$ARCHIVE_SCRIPT FIELD/SRT /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/SRT nc $CS_LOCATION$YEAR/ $EMAIL

### Preliminary HRT
#$ARCHIVE_SCRIPT FIELD/HRT /scr/raf/Raw_Data/$PROJECT/HRT nc $CS_LOCATION$YEAR/ $EMAIL

### Preliminary LRT ICT
#$ARCHIVE_SCRIPT field_sync/ICARTT /scr/raf/Raw_Data/$PROJECT/field_sync/ICARTT ict $CS_LOCATION$YEAR $EMAIL

### Preliminary LRT IWG1
#$ARCHIVE_SCRIPT FIELD/PMS2D /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/PMS2D 2d $CS_LOCATION$YEAR/ $EMAIL

### Preliminary LRT IWG1
#$ARCHIVE_SCRIPT FIELD/IWG1 /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/IWG1 iwg $CS_LOCATION$YEAR/ $EMAIL

###Preliminary F2DS
#$ARCHIVE_SCRIPT FIELD/F2DS -t /scr/raf/Raw_Data/$PROJECT/F2DS F2DS $CS_LOCATION$YEAR/ $EMAIL

###Preliminary HVPS
#$ARCHIVE_SCRIPT FIELD/HVPS -t /scr/raf/Raw_Data/$PROJECT/HVPS HVPS $CS_LOCATION$YEAR/ $EMAIL

###Preliminary F2DS
#$ARCHIVE_SCRIPT FIELD/ICARTT/F2DS /scr/raf/Raw_Data/$PROJECT/F2DS/ICARTT ict $CS_LOCATION$YEAR/ $EMAIL

###Preliminary F2DS
#$ARCHIVE_SCRIPT FIELD/ICARTT/HVPS /scr/raf/Raw_Data/$PROJECT/HVPS/ICARTT ict $CS_LOCATION$YEAR/ $EMAIL


### Preliminary KML
#$ARCHIVE_SCRIPT FIELD/KML /scr/raf/Raw_Data/$PROJECT/field_sync/EOL_data/RAF_data/KML kml $CS_LOCATION$YEAR/ $EMAIL

### Preliminary CO ICT
#ARCHIVE_SCRIPT field_sync/CO /scr/raf/Raw_Data/$PROJECT/field_sync/CO ict $CS_LOCATION$YEAR $EMAIL

### Preliminary CO2CH4 ICT
#$ARCHIVE_SCRIPT field_sync/CO2CH4 /scr/raf/Raw_Data/$PROJECT/field_sync/CO2CH4 ict $CS_LOCATION$YEAR $EMAIL

### Preliminary NONO2O3 ICT
#$ARCHIVE_SCRIPT field_sync/NONOyO3 /scr/raf/Raw_Data/$PROJECT/field_sync/NO_NOy_O3 ict $CS_LOCATION$YEAR $EMAIL

### Preliminary TOGA ICT
#$ARCHIVE_SCRIPT field_sync/TOGA /scr/raf/Raw_Data/$PROJECT/field_sync/TOGA ict $CS_LOCATION$YEAR $EMAIL

### Preliminary TOF-AMS ICT
#$ARCHIVE_SCRIPT field_sync/TOF-AMS /scr/raf/Raw_Data/$PROJECT/field_sync/CU-HRAMS ict $CS_LOCATION$YEAR $EMAIL

### Preliminary HARP Actinic Flux ICT
#$ARCHIVE_SCRIPT field_sync/HARP /scr/raf/Raw_Data/$PROJECT/field_sync/HARP_Jvalues ict $CS_LOCATION$YEAR $EMAIL

### Preliminary ARNOLD ICT
#ARCHIVE_SCRIPT field_sync/ARNOLD /scr/raf/Raw_Data/$PROJECT/field_sync/ARNOLD ict $CS_LOCATION$YEAR $EMAIL

########################## Production Data Files ##########################
### LRT
$ARCHIVE_SCRIPT LRT/v1.2 /scr/raf/Prod_Data/$PROJECT nc /net/archive/data/ $EMAIL

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

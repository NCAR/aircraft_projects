#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
setenv PROJECT "CONTRAST"
setenv YEAR 2014
setenv PLATFORM "GV_N677F"
setenv ARCHIVE_SCRIPT "/net/jlocal/projects/Configuration/scripts/archAC.py"
setenv CS_LOCATION "/glade/campaign/eol/archive/"
setenv EMAIL "taylort@ucar.edu"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2014

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL/2014

### CAMERA
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf08 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf09 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf10 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf11 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf12 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf13 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf14 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf15 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf16 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_rf17 jpg EOL/2014
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_tf01 jpg EOL/2014

### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1.2_20181015 /scr/raf/Prod_Data/$PROJECT/LRT/V1.2_20181015 nc FS/EOL/2014 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1.3_20210424 /scr/raf/Prod_Data/$PROJECT/LRT/V1.3_20210424 nc FS/EOL/2014 janine@ucar.edu

### HRT
$ARCHIVE_SCRIPT HRT /scr/raf/Prod_Data/$PROJECT/HRT nc  $CS_LOCATION$YEAR $EMAIL

### ICARTT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/ICARTT/V3_20181015 /scr/raf/Prod_Data/$PROJECT/LRT/V1.2_20181015 GV FS/EOL/2014 taylort@ucar.edu

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml EOL/2014

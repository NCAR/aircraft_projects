#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "DC3"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL

### PMS2D - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL

### CAMERA - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_ff01 jpg EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images/flight_number_tf02 jpg EOL

#### CAMERA - This line creates hour tarballs of static camera images and
#### puts them on the hpss. 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL

### LRT - done, rearchived with updated VCSEL cals 1/28/2013, updated 2017/05/05 for RAF reprocessing.
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/ICARTT_format/V3_20181015 /scr/raf/Prod_Data/$PROJECT/V3_20181015/ICARTT_format ICT FS/EOL/2012 taylort@ucar.edu

### HRT - done, rearchived with updated VCSEL cals 1/28/2013, 2017 for variable name change.
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/$PROJECT/HRT nc FS/EOL/2012

### KML - done, rearchived with updated VCSEL cals 1/28/2013, 20170505 for reprocessing.
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml FS/EOL/2012
 
### MOVIE
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf/Prod_Data/$PROJECT/movies mp4 EOL

### MTP
#/net/work/bin/scripts/mass_store/archAC/archAC.py mtp /scr/raf/Prod_Data/$PROJECT NGV EOL cbsnyder@ucar.edu

### VCSEL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/ROI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi roi EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/OAP -r /scr/raf_Raw_Data/$PROJECT/3v-cpi/oapfiles 2d FS/EOL/2012
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi 2DSCPIHK EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi log EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi TXT EOL

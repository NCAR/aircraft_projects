#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "ICE-T"
#echo "Make sure netCDF files have been reordered before archiving!!!"
#
### ADS - done 8/18/2011
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL janine@ucar.edu
#
### LRT - done 10/13/2011, final data updated 11/16/2011, added updated FSSP
### and SID2H 10/2/2012, fixed minor error in FSSP 10/30/2012
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf/Prod_Data/$PROJECT/orig nc EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT \.nc EOL 

#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1 /scr/raf/Prod_Data/$PROJECT .nc FS/EOL/2011 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V2_20111116 /scr/raf/Prod_Data/$PROJECT/V2_20111116 .nc FS/EOL/2011 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V3_20120103 /scr/raf/Prod_Data/$PROJECT/V3_20120103 .nc FS/EOL/2011 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V4_20120424 /scr/raf/Prod_Data/$PROJECT/V4_20120424 .nc FS/EOL/2011 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V5_20120822 /scr/raf/Prod_Data/$PROJECT/V5_20120822 .nc FS/EOL/2011 taylort@ucar.edu


# HRT - done Jan 4, 2012, updated FSSP 10/30/2012
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf/Prod_Data/ICE-T/HRT h.nc EOL


### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF
#
### PMS2D - done 8/18/2011, added ferry flights 10/13/2011
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D ff0..2d EOL
#
### CAMERA - started 8/18/2011
###- This line creates hour tarballs of static camera images and puts them on HPSS
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/Cameras jpg EOL 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -a . tar EOL 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -a . tar.dir EOL 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -r /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_ff02/down jpg EOL 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf10/forward jpg EOL/2011
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_tf02 jpg EOL/2011

### MOVIES
### Don't archive preliminary movies to MSS, but do put them in codiac and
### make them orderable.

# FINAL MOVIES
# Archive to /net/archive for preview and delivery, but also copy to HPSS
# for safe keeping.
#/net/work/bin/scripts/mass_store/archAC/archAC.py MOVIES /scr/raf/Prod_Data/$PROJECT/movies mp4 EOL

### DGPS
##/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps ads ATDdata

### 3V-CPI
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/2D-S -r /scr/raf/Raw_Data/$PROJECT/3v-cpi 2DSCPI EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/ROI -r /scr/raf/Raw_Data/$PROJECT/3v-cpi roi EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/HK_and_logs -r /scr/raf/Raw_Data/$PROJECT/3v-cpi 2DSCPIHK EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/HK_and_logs -r /scr/raf/Raw_Data/$PROJECT/3v-cpi log EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py 3V-CPI/HK_and_logs -r /scr/raf/Raw_Data/$PROJECT/3v-cpi TXT EOL

### SID2H
##/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H /scr/raf/Prod_Data/$PROJECT/SID2H nc EOL

### VCSEL

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/kml kml EOL

### NASA_AMES
#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /scr/raf/Prod_Data/$PROJECT/NASA_AMES gz EOL stroble@ucar.edu

### CN ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/CN /scr/raf/Prod_Data/$PROJECT/CN/orig nc EOL

### CVI ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/CVI /scr/raf/Prod_Data/$PROJECT/CVI/orig txt EOL

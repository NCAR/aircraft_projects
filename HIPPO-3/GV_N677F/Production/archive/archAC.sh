#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "HIPPO-3"
#echo "Make sure netCDF files have been reordered before archiving!!!"
#
#### ADS
##/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads RAF
#
### LRT - done 6/14/2010, V3 Dec 2012, V4 Nov 2016
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf/Prod_Data/$PROJECT nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT \.nc EOL/2010 janine@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1_20110328 /scr/raf/Prod_Data/$PROJECT/V1_20110328 .nc FS/EOL/2010 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.pu LRT/V2_20110506 /scr/raf/Prod_Data/$PROJECT/V2_20110506 .nc FS/EOL/2010 taylort@ucar.edu
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V5_20190125 /scr/raf/Prod_Data/$PROJECT/V5_20190125 .nc FS/EOL/2010 taylort@ucar.edu

#
#### CHAT
##/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF
#
#### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL
##/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d.gz ATDdata
#
#### CAMERA - This line creates hour tarballs of static camera images and
#### puts them on the mss. 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_rf07/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_rf08/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_rf09/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_rf10/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_rf11/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_tf01/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera/flight_number_tf02/forward jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera jpg ATDdata
#
#### MOVIES
#### Don't archive preliminary movies to MSS, but do put them in codiac and
#### make them orderable.
#
#### DGPS
##/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps ads ATDdata
#
#### SID2H
##/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd RAF
#
#### VCSEL

###KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/kml/V4_20161109 kml EOL/2010

### NASA_AMES
#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /scr/raf/Prod_Data/$PROJECT 1DC.asc EOL/2010 janine@ucar.edu

### MTP
#/net/work/bin/scripts/mass_store/archAC/archAC.py MTP /scr/raf/Prod_Data/$PROJECT/mtp NGV EOL janine@ucar.edu

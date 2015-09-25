#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "HIPPO-4"
#echo "Make sure netCDF files have been reordered before archiving!!!"
#
#### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL cbsnyder@ucar.edu
#
### LRT - done 5/15/2012, redone 06/25/2012
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT \.nc EOL janine@ucar.edu
#
#### CHAT
##/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF
#
#### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL
#
#### CAMERA - This line creates hour tarballs of static camera images and
#### puts them on the mss. 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf01/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf02/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf03/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf04/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf05/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf06/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf07/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf08/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf09/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf10/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf11/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_rf12/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_tf01/forward jpg EOL csibo@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_files/flight_number_tf02/forward jpg EOL csibo@ucar.edu
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

###KML - done, redone 6/25/2012
/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/kml kml EOL/2011

### NASA_AMES
#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /scr/raf/Prod_Data/$PROJECT/NASA_AMES gz EOL stroble@ucar.edu

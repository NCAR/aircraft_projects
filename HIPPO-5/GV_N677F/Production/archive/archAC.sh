#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "HIPPO-5"
#echo "Make sure netCDF files have been reordered before archiving!!!"
#
#### ADS - done 1/25/2012
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL janine@ucar.edu
#
### LRT - done 5/16/2012, redone 6/25/2012
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
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/camera_images jpg EOL

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

###KML - done 5/16/2012, redone 6/25/2012
/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/kml kml EOL/2011

### NASA_AMES
#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /scr/raf/Prod_Data/$PROJECT/NASA_AMES gz EOL stroble@ucar.edu

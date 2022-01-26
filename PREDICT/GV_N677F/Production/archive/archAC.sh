#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = PREDICT
set YEAR = 2010
#echo "Make sure netCDF files have been reordered before archiving!"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ff01.ads RAF janine@ucar.edu

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF

###LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/Version1_2001Feb02 /scr/raf/Prod_Data/$PROJECT/Version1_2001Feb02 .nc FS/EOL/$YEAR taylort@ucar.edu
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/Version3_2021Aug06 /scr/raf/Prod_Data/$PROJECT/LRT/Version3_2021Aug06 .nc FS/EOL/$YEAR taylort@ucar.edu

#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT/ordered rf26.nc ATDdata

###KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT kml ATDdata

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D rf02.2d ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL

### CAMERA - This line creates hour tarballs of static camera images and
### puts them on the mss. 
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf14 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_ff04 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf26 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf21 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf22 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf23 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf24 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Cameras/flight_number_rf25 jpg ATDdata janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -a /net/jlocal/projects/PREDICT/GV_N677F/Production/archive jpg.tar ATDdata janine@ucar.edu

### MOVIES
### Don't archive preliminary movies to MSS, but do put them in codiac and
### make them orrderable.
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /net/jlocal/projects/PREDICT/GV_N677F/Production/archive mp4 ATDdata janine@ucar.edu

### DGPS
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd EOL janine@ucar.edu

###CVI
#/net/work/bin/scripts/mass_store/archAC/archAC.py hidden/cvi /scr/raf/Prod_Data/$PROJECT/cvi/orig txt EOL janine@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py hidden/cvi /scr/raf/Prod_Data/$PROJECT/cvi/nc nc EOL janine@ucar.edu

### VCSEL

### GISMOS
#/net/work/bin/scripts/mass_store/archAC/archAC.py gismos -r /scr/raf/Prod_Data/$PROJECT/gismos Z EOL janine@ucar.edu

### MTP
#/net/work/bin/scripts/mass_store/archAC/archAC.py mtp /scr/raf/Prod_Data/$PROJECT/mtp NGV EOL janine@ucar.edu

### O3
#/net/work/bin/scripts/mass_store/archAC/archAC.py O3 /scr/raf/Prod_Data/$PROJECT/O3 dat EOL

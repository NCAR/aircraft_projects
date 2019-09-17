#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "HIPPO-2"
echo "Make sure netCDF files have been reordered before archiving!"

### LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf/Prod_Data/$PROJECT nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT \.nc EOL/2009
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1_20110328 /scr/raf/Prod_Data/$PROJECT/V1_20110328 .nc FS/EOL/taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V2_20110506 /scr/raf/Prod_Data/$PROJECT/V2_20110506 .nc FS/EOL/taylort@ucar.edu

### ADS - done 12/17/09
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads RAF

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF

### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d EOL
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d.gz ATDdata

### CAMERA - this line makes tarfiles by hour of raw camera images. - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Camera jpg ATDdata

### MOVIES
### Do not put preliminary movies on mss, but DO make them into an
### orderable codiac dss.

### DGPS
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf/Raw_Data/$PROJECT/sid2h srd RAF

###KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/$PROJECT/kml/V4_20161109 kml EOL/2009

### VCSEL

### NASA_AMES
/net/work/bin/scripts/mass_store/archAC/archAC.py gv /scr/raf/Prod_Data/$PROJECT 1DC\.asc EOL/2009

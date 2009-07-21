#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "VOCALS"
# Source Rate
#/net/work/bin/scripts/mass_store/archAC/archAC.py SRT /scr/raf2/Prod_Data/$PROJECT srt.nc ATDdata


# UNALTERED LRT - updated 6/30/09
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/productiondata ${PROJECT}rf...nc RAF
# UNALTERED HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/HRT /scr/productiondata ${PROJECT}rf..h.nc RAF

#### Final (merged) Datasets ####
# LRT - DONE - updated 6/30/09, 7/9/09
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/$PROJECT .nc ATDdata

# HRT - DONE
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf2/Prod_Data/$PROJECT h.nc ATDdata

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT .ads RAF
# Rearchive flights 9 and 10
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT 09.ads RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT 10.ads RAF

### CVI raw - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CVI /scr/raf2/Raw_Data/$PROJECT/CVI 12.txt RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py CVI /scr/raf2/Raw_Data/$PROJECT/CVI 13.txt RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py CVI /scr/raf2/Raw_Data/$PROJECT/CVI 14.txt RAF

### CVI .nc format
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/CVI /scr/raf2/Prod_Data/$PROJECT/CVI .nc RAF

### CHAT
###/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf2/Raw_Data/$PROJECT/Chat log RAF

### PMS2D src format- done
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d ATDdata
### PMS2D nc format - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf2/Prod_Data/$PROJECT/PMS2D/V5_20090606 nc RAF

### CAMERA - use archcam.###, not this script.

### MOVIES - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA /scr/raf/Raw_Data/$PROJECT/Movies mp4 ATDdata

### DGPS
###/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf2/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H
###/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf2/Raw_Data/$PROJECT/sid2h srd RAF

### VCSEL

### O3 txt
#/net/work/bin/scripts/mass_store/archAC/archAC.py O3 -t /scr/raf2/Prod_Data/VOCALS/O3 txt RAF
### O3 netCDF
#/net/work/bin/scripts/mass_store/archAC/archAC.py O3 /scr/raf2/Prod_Data/VOCALS/O3 nc RAF

### CVI
#/net/work/bin/scripts/mass_store/archAC/archAC.py CVI /scr/raf2/Raw_Data/VOCALS/CVI txt RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py CVI /scr/raf2/Prod_Data/VOCALS/CVI nc RAF

### TSURF netCDF
#/net/work/bin/scripts/mass_store/archAC/archAC.py TSURF /scr/raf2/Prod_Data/VOCALS/TSURF nc RAF

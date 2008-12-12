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

# HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf2/Prod_Data/$PROJECT H.nc ATDdata

# LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/$PROJECT .nc ATDdata

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT .ads RAF

### CHAT
###/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf2/Raw_Data/$PROJECT/Chat log RAF

### PMS2D - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/$PROJECT/PMS2D 2d ATDdata

### CAMERA - use archcam.###, not this script.

### MOVIES

### DGPS
###/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf2/Raw_Data/$PROJECT/dgps ads ATDdata

### SID2H
###/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf2/Raw_Data/$PROJECT/sid2h srd RAF

### VCSEL

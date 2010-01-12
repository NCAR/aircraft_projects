#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "HIPPO"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/$PROJECT ads RAF

### LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/HIPPO-1 nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/HIPPO-1 nc ATDdata

### KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf2/Prod_Data/HIPPO-1/kml kml ATDdata

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf2/Raw_Data/$PROJECT/Chat log RAF

### CAMERA - use archcam.510, not this script.

### MOVIES

### MTP - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py MTP /scr/raf2/Raw_Data/HIPPO MTP_HIPPO_20081213_20090130.tar.gz RAF

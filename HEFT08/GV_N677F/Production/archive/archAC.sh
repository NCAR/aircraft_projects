#!/bin/csh -f
#
# Set PROJECT and uncomment each command to archive that data type.

##############
#   HEFT08   #
##############
set PROJECT = "HEFT08"

#echo "Make sure netCDF files have been reordered before archiving!!!"


# LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/$PROJECT nc ATDdata

# CAMERA - replaced full-res images with 1/2 size sharpened and
# time-stamped images. - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -p FWD /scr/raf2/Raw_Data/$PROJECT/camera jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf2/Raw_Data/$PROJECT/camera tar ATDdata

# MOVIE - prelim movies - done
/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf2/Raw_Data/$PROJECT/camera mov ATDdata


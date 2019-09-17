#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "PACDEX"
set YEAR = 2007


#echo "Make sure netCDF files have been reordered before archiving!!!"
#
#### PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py HARP -r /scr/raf/Raw_Data/$PROJECT/HARP_spectral_irradiance sav EOL

## LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/Version1 /scr/raf/Prod_Data/$PROJECT/Version1 .nc /FS/EOL/$YEAR taylort@ucar.edu
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/Version3 /scr/raf/Prod_Data/$PROJECT/Version3 .nc /FS/EOL/$YEAR taylort@ucar.edu

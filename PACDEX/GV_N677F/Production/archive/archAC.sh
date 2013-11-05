#! /bin/csh -f
##
## This is an example script.
## Set PROJECT and uncomment each command to archive that data type.
#
################
##   Project   #
################
set PROJECT = "PACDEX"
#echo "Make sure netCDF files have been reordered before archiving!!!"
#
#### PMS2D
/net/work/bin/scripts/mass_store/archAC/archAC.py HARP -r /scr/raf/Raw_Data/$PROJECT/HARP_spectral_irradiance sav EOL

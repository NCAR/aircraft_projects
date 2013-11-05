#!/bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "PodCertGV"
#echo "Make sure netCDF files have been reordered before archiving!!!"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads RAF

### MATLAB
#/net/work/bin/scripts/mass_store/archAC/archAC.py MATLAB /scr/raf/Raw_Data/$PROJECT/GAC_data mat EOL

### NetCDF
/net/work/bin/scripts/mass_store/archAC/archAC.py NetCDF /scr/raf/Prod_Data/$PROJECT nc EOL

#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "PASE"
echo "Make sure netCDF files have been reordered before archiving!"

### KML
/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Raw_Data/$PROJECT kml ATDdata

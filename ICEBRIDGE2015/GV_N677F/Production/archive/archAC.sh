#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "ICEBRIDGE2015"

### ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads EOL/2015

### Prelim LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py field/LRT /scr/raf/Raw_Data/$PROJECT/field_phase/LRT nc EOL/2015

### LRT
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/$PROJECT nc EOL/2015

### IWG1
#/net/work/bin/scripts/mass_store/archAC/archAC.py field/IWG1 /scr/raf/Raw_Data/$PROJECT/field_phase/IWG1 iwg1 EOL/2015

### KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py field/KML /scr/raf/Raw_Data/$PROJECT/field_phase/KML kml EOL/2015

#! /bin/csh -f
#
# This is an example script.
# Set PROJECT and uncomment each command to archive that data type.

###############
#   Project   #
###############
set PROJECT = "HIPPO"

### ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf/Raw_Data/$PROJECT ads RAF

### LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf/Prod_Data/HIPPO-1 nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf/Prod_Data/HIPPO-1 .nc /FS/EOL/2009
#/net/work/bin/scripts/mass_store/archAC/archAC.py gv /scr/raf/Prod_Data/HIPPO-1 .asc /FS/EOL/2009
### LRT (legacy docs)
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V1_20090602 /scr/raf/Prod_Data/HIPPO-1/V1_20090602 .nc FS/EOL/2009 taylort@ucar.edu
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V2_20100729 /scr/raf/Prod_Data/HIPPO-1/V2_20100729 .nc FS/EOL/2009 taylort@ucar.edu
/net/work/bin/scripts/mass_store/archAC/archAC.py LRT/V3_20110506 /scr/raf/Prod_Data/HIPPO-1/V3_20110506 .nc FS/EOL/2009 taylort@ucar.edu

### KML - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Prod_Data/HIPPO-1/kml/V3_20110506 kml /FS/EOL/2009

### CHAT
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf/Raw_Data/$PROJECT/Chat log RAF

### CAMERA -  done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -p FWD /scr/raf/Raw_Data/HIPPO/Camera/TF01.081213-123723 jpg ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -a /jnet/local/projects/HIPPO/GV_N677F/Production/archive tar ATDdata


### MOVIES - prelim
#/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf/Raw_Data/HIPPO/Camera mov RAF

### raw MTP - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py MTP /scr/raf/Raw_Data/HIPPO MTP_HIPPO_20081213_20090130.tar.gz RAF

### raw vcsel
#/net/work/bin/scripts/mass_store/archAC/archAC.py VCSEL /scr/raf/Raw_Data/HIPPO/vcsel asc RAF

### Final AO2 NASA AMES format ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py AO2 /net/work/Projects/HIPPO-1/aircraft/GV/AO2 v02a.GV ATDdata 

### Final AWAS NASA AMES format ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py AWAS /net/work/Projects/HIPPO-1/aircraft/GV/AWAS gv ATDdata

### Final CH4-N2O-CO-QCLS NASA AMES format ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py CH4-N2O-CO-QCLS /net/work/Projects/HIPPO-1/aircraft/GV/CH4-N2O-CO-QCLS GV ATDdata

### CO2_OMS ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2_OMS /net/work/Projects/HIPPO-1/aircraft/GV/CO2_OMS GV ATDdata

### CO2_QCLS ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO2_QCLS /net/work/Projects/HIPPO-1/aircraft/GV/CO2_QCLS GV ATDdata

### CO_RAF ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py CO_RAF /net/work/Projects/HIPPO-1/aircraft/GV/CO_RAF gv ATDdata

### GCMS-M2 ###
#/net/work/bin/scripts/mass_store/archAC/archAC.py GCMS-M2 /net/work/Projects/HIPPO-1/aircraft/GV/GCMS-M2 GV ATDdata

#/net/work/bin/scripts/mass_store/archAC/archAC.py GC_ECD /net/work/Projects/HIPPO-1/aircraft/GV/GC_ECD GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py GC_MSD /net/work/Projects/HIPPO-1/aircraft/GV/GC_MSD GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py MAGICC /net/work/Projects/HIPPO-1/aircraft/GV/MAGICC GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py MEDUSA_flaskdata /net/work/Projects/HIPPO-1/aircraft/GV/MEDUSA_flaskdata GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py MEDUSA_kernel /net/work/Projects/HIPPO-1/aircraft/GV/MEDUSA_kernel GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py MTP /net/work/Projects/HIPPO-1/aircraft/GV/MTP NGV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py O3_NOAA /net/work/Projects/HIPPO-1/aircraft/GV/O3_NOAA GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py SP2 /net/work/Projects/HIPPO-1/aircraft/GV/SP2 GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py UCATS /net/work/Projects/HIPPO-1/aircraft/GV/UCATS/GC GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py UCATS /net/work/Projects/HIPPO-1/aircraft/GV/UCATS/H2O GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py UCATS /net/work/Projects/HIPPO-1/aircraft/GV/UCATS/O3 GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py VCSEL /net/work/Projects/HIPPO-1/aircraft/GV/VCSEL GV ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /net/work/Projects/HIPPO-1/aircraft/GV/GV_nav_and_state gz ATDdata


#/net/work/bin/scripts/mass_store/archAC/archAC.py NASA_AMES /net/work/Projects/HIPPO-1/aircraft/GV/gv gz EOL stroble@ucar.edu

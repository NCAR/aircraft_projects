# ADS - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/START08 ads RAF

# CHAT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py CHAT -t /scr/raf2/Raw_Data/START08/Chat log RAF

#PMS2D - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/START08/PMS2D 2d ATDdata
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/START08/PMS2D 2d.gz ATDdata

# KML
#/net/work/bin/scripts/mass_store/archAC/archAC.py KML /scr/raf/Raw_Data/START08/kml kml RAF

#CAMERA - use archcam.510, not this script.

# FINAL MOVIES - Do NOT archive prelim movies!
/net/work/bin/scripts/mass_store/archAC/archAC.py CAMERA -m /scr/raf/Raw_Data/START08/camera/final_movies mp4 ATDdata

# DGPS - not done, waiting for final, usable data from Pavel
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf2/Raw_Data/START08/dgps ads ATDdata

# SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py
#/h/eol/janine/work/python/archAC/archAC.py SID2H -t /scr/raf2/Raw_Data/START08/sid2h srd RAF

##vcsel - VCSEL team is processing. Pavel will give me final data when team
#gives it to him.

# Unaltered LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /jnet/productiondata START08rf...nc RAF

# LRT - done
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/START08 nc ATDdata

# MTP
#/net/work/bin/scripts/mass_store/archAC/archAC.py MTP /scr/raf2/Raw_Data/START08 MTP_START08_20080414_20080627.tar.gz RAF

# TDL
#/net/work/bin/scripts/mass_store/archAC/archAC.py TDL /scr/raf2/Prod_Data/START08/TDL START08_MRTDL.tar ATDdata

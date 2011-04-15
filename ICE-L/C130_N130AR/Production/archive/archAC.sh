echo "Be sure to reorder netCDF files before archiving to MSS!!!"
# ADS
#/net/work/bin/scripts/mass_store/archAC/archAC.py ADS /scr/raf2/Raw_Data/ICE-L ads RAF

# SID2H
#/net/work/bin/scripts/mass_store/archAC/archAC.py SID2H -t /scr/raf2/Raw_Data/ICE-L/sid-2h srd RAF

# CPI
#/net/work/bin/scripts/mass_store/archAC/archAC.py CPI -t /scr/raf2/Raw_Data/ICE-L/CPI roi RAF
# Rearchive to /ATD/DATA. Don't redo tarfiles, just read the ones we did above.
#/h/eol/janine/work/python/archAC/archAC.py CPI /jnet/local/projects/ICE-L/C130_N130AR/Production/archive .tar ATDdata
#msrm -R -wpwd RAFDMG /RAF/2008/115/CPI

#PMS2D
#/net/work/bin/scripts/mass_store/archAC/archAC.py PMS2D /scr/raf/Raw_Data/ICE-L/PMS2D 2d ATDdata

#CAMERA
# Don't archive camera files here. Use the archive_camera script!!!
#movies - waiting for jbj to create final aircraft .nc files so stuart can add params to
#movies. Then I can archive these final, movie files. Do NOT archive prelim movies!

#DGPS - in LRT, archive processing to raw area
#/net/work/bin/scripts/mass_store/archAC/archAC.py DGPS /scr/raf/Prod_Data/ICE-L/MERGE DGPS.tar.gz RAF

#FINAL DGPS (are in LRT data)

#TDL - in LRT, archive processing to raw area
#/net/work/bin/scripts/mass_store/archAC/archAC.py TDL /scr/raf/Prod_Data/ICE-L/MERGE TDL.tar.gz RAF

#FINAL TDL (are in LRT data)

# satcom: don't need to archive anything at this time -
# CJW

# UNALTERED LRT - rearchived 2/20/2009 for reprocessing done 12/1/22008 to remove 2D vars
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 1.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 2.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 3.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 4.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 5.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 6.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 7.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 8.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 9.nc RAF
#/net/work/bin/scripts/mass_store/archAC/archAC.py UNALTERED/LRT /scr/raf2/Prod_Data/ICE-L 0.nc RAF

# HRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py HRT /scr/raf2/Prod_Data/ICE-L/HRT h.nc ATDdata

# LRT
#/net/work/bin/scripts/mass_store/archAC/archAC.py LRT /scr/raf2/Prod_Data/ICE-L nc ATDdata

# KML - archive to /net/archive/data

#FO3 - RAW
#/net/work/bin/scripts/mass_store/archAC/archAC.py FO3 /scr/raf/Raw_Data/ICE-L/FO3 mrg.txt RAF

#FO3 - Interpolated
/net/work/bin/scripts/mass_store/archAC/archAC.py FO3 /scr/raf/Prod_Data/ICE-L/MERGE/fO3 mrg.txt RAF


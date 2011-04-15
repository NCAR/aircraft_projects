#!/bin/sh 

for file in `ls -1 /scr/raf/Prod_Data/HEFT10/DOAS/*nc`
do
   ncatted -a units,CHOCHO_dSCD,m,c,'molec/cm2' -h $file
   ncatted -a long_name,CHOCHO_dSCD,m,c,'trace gas differential Slant Column Density of glyoxal' -h $file
   ncatted -a units,CHOCHO_dSCDsig,m,c,'molec/cm2' -h $file
   ncatted -a long_name,CHOCHO_dSCDsig,m,c,'significance of trace gas differential Slant Column Density of glyoxal' -h $file
    ncatted -a units,IO_dSCD,m,c,'molec/cm2' -h $file
    ncatted -a long_name,IO_dSCD,m,c,'trace gas differential Slant Column Density of iodine oxide' -h $file
    ncatted -a units,IO_dSCDsig,m,c,'molec/cm2' -h $file
    ncatted -a long_name,IO_dSCDsig,m,c,'significance of trace gas differential Slant Column Density of iodine oxide' -h $file
done

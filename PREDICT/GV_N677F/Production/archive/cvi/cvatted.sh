#!/bin/sh

exec > ./cvatted.log 2>&1

for filename in `ls -1 ./rf*nc`
do
    ncatted -a units,CVINLET,m,c,"dimensionless" -h $filename
    ncatted -a long_name,CVINLET,m,c,"CVI Inlet Flag: 0=CVI, 1=ambient" -h $filename
    ncatted -a TimeLagCorrection,CVINLET,c,c,"The data has been corrected for a 3.5 second time lag." -h $filename

    ncatted -a units,CVFXFLOWS,m,c,"dimensionless" -h $filename
    ncatted -a long_name,CVFXFLOWS,m,c,"CVI Flow Flag" -h $filename
    ncatted -a TimeLagCorrection,CVFXFLOWS,c,c,"The data has been corrected for a 3.5 second time lag." -h $filename

    ncatted -a units,CVCWC,m,c,"g m-3" -h $filename
    ncatted -a long_name,CVCWC,m,c,"CVI condensed water content" -h $filename
    ncatted -a TimeLagCorrection,CVCWC,c,c,"The data has been corrected for a 3.5 second time lag." -h $filename

    ncatted -a units,CVRAD,m,c,"microns" -h $filename
    ncatted -a long_name,CVRAD,m,c,"CVI cut radius" -h $filename
    ncatted -a TimeLagCorrection,CVRAD,c,c,"The data has been corrected for a 3.5 second time lag." -h $filename

    ncatted -a units,CVCFACT,m,c,"dimensionless" -h $filename
    ncatted -a long_name,CVCFACT,m,c,"CVI concentration factor" -h $filename
    ncatted -a TimeLagCorrection,CVCFACT,c,c,"The data has been corrected for a 3.5 second time lag." -h $filename
done

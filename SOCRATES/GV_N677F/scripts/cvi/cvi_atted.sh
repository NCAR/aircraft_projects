#!/bin/sh

exec > ./cvatted.log 2>&1

for filename in `ls -1 ${CVIDAT}/RF*nc`
do
    ncatted -a units,CVIFLAG,m,c,"bool" -h $filename
    ncatted -a long_name,CVIFLAG,m,c,"CVI flag" -h $filename

    ncatted -a units,CVCFACTC,m,c,"" -h $filename
    ncatted -a long_name,CVCFACTC,m,c,"CVI Concentration Factor, Compensated for Icing" -h $filename

    ncatted -a units,CVCFACTTDL,m,c,"" -h $filename
    ncatted -a long_name,CVCFACTTDL,m,c,"CVI TDL Concentration Factor" -h $filename

    ncatted -a units,CVCWCC,m,c,"g/m-3" -h $filename
    ncatted -a long_name,CVCWCC,m,c,"CVI Cloud Condensed Water Content, Corrected" -h $filename

    ncatted -a units,CONCUD,m,c,"#/cm3" -h $filename
    ncatted -a long_name,CONCUD,m,c,"UHSAS CVI Drop Concentration (all cells)" -h $filename

done

#!/bin/sh

#exec > ./merge_cvi.log 2>&1

#export CVIDAT=/scr/raf/Prod_Data/SOCRATES/CVI/
for srcfile in `ls -1 ${CVIDAT}/RF[0-9][0-9]*nc`
do
    destfile=${DAT}`echo $srcfile | sed 's/.*\\/RF\(..\)CVI.........nc/\\/SOCRATESrf\1.nc/'`
    ncmerge -v CVIFLAG,CVCFACTC,CVCFACTTDL,CVCWCC,CONCUD $destfile $srcfile
done


#!/bin/sh

exec > ./merge_cvi.log 2>&1

for srcfile in `ls -1 ${DAT}/RF[0-9][0-9]*nc`
do
    destfile=`echo $srcfile | sed 's/CVI\\/RF\(..\)CVI.........nc/LRT\\/SOCRATESrf\1.nc/'`
    ncmerge -v CVINLET,CVFXFLOWS,CVCWC,CVRAD,CVCFACT $destfile $srcfile
done


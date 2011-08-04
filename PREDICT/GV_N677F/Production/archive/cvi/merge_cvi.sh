#!/bin/sh

#exec > ./merge_cvi.log 2>&1

#for srcfile in `ls -1 nc/rf[0-9][0-9]*nc`
for srcfile in `ls -1 nc/rf01*nc`
do
    destfile=`echo $srcfile | sed 's/nc\\/\(rf..\)CVI.......nc/PREDICT\1.nc/'`
    ncmerge -v CVINLET,CVFXFLOWS,CVCWC,CVRAD,CVCFACT $destfile $srcfile
done


#!/bin/sh

exec > ./merge_new_vars.log 2>&1

for srcfile in `ls -1 V20170411_LRT/CSET*nc`
do
    destfile=`echo $srcfile | sed 's/V20170411_LRT\/CSETrf\(...nc\)/CSETrf\1/'`
    ncmerge -v A1DC_LWOO,AUHSAS_RWOOU,ACDP_LWOI,RSTB $destfile $srcfile
done

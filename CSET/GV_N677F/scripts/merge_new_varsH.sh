#!/bin/sh


for file in `ls CSET*nc`
do
    outfile=`echo $file | sed 's/nc/nc.new/'`
    echo $outfile
    ncks -x -v ACDP_LWOI,AUHSAS_RWOOU $file $outfile
    mv $outfile $file
done

exec > ./merge_new_varsH.log 2>&1

for srcfile in `ls -1 V20170503_HRT/CSET*nc`
do
    destfile=`echo $srcfile | sed 's/V20170503_HRT\/CSETrf\(..h.nc\)/CSETrf\1/'`
    ncmerge -v A1DC_LWOO,AUHSAS_RWOOU,ACDP_LWOI,RSTB $destfile $srcfile
done

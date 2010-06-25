#!/bin/sh

exec > ./merge_DOAS.log 2>&1

for srcfile in `ls -1 /scr/raf/Prod_Data/HEFT10/DOAS/DOAS_HEFT10*nc`
do
    destfile=`echo $srcfile | sed '{
        s?DOAS/DOAS_??
	s/FF/ff/
	s/RF/rf/
    }'`
    #ncmerge -v CHOCHO_dSCD,CHOCHO_dSCDsig,IO_dSCD,IO_dSCDsig $destfile $srcfile
    ncmerge -v CHOCHO_dSCDsig,IO_dSCDsig $destfile $srcfile
done

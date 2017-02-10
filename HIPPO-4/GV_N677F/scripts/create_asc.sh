#!/bin/csh

#set nc2asc = "/opt/local/bin/nc2asc"
set nc2asc = "/net/work/dev/jaa/raf/nc_utils/nc2asc/deploy/nc2asc.sh"

foreach file (`ls HIPPO*no1DC.nc`)
    set outfile = `echo $file | sed s/nc/asc/;`
    ${nc2asc} -b HIPPO_template -i $file -o $outfile
end

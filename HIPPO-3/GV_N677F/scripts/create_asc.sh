#!/bin/csh

set nc2asc = "/opt/local/bin/nc2asc"

foreach file (`ls HIPPO*nc`)
    set outfile = `echo $file | sed s/nc/asc/;`
    ${nc2asc} -b HIPPO_template -i $file -o $outfile
end

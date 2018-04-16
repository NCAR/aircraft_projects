#!/bin/csh

# The July 24 flight ran over midnight and the time cycled back to zero rather than continuing past 86400. Fix
#./fix_times_after_midnight.py
#mv /scr/raf/Prod_Data/CSET/HOLODEC/H2H/CSET-HOLODEC-H2H_GV_20150724.csv.corr /scr/raf/Prod_Data/CSET/HOLODEC/H2H/CSET-HOLODEC-H2H_GV_20150724.csv

# As the agreed-upon header was in flux when the data were submitted, make changes here.
#./correct_header_h2h.pl

#foreach file (`ls /scr/raf/Prod_Data/CSET/HOLODEC/H2H/sample_rate/*-[0-9]*csv`)
#  set ncfile=`echo $file | sed 's/csv/nc/'`
#  echo $ncfile
#  ./ascav.py --input_file=$file
#end
foreach file (`ls /scr/raf/Prod_Data/CSET/HOLODEC/H2H/1hz/*-[0-9]*csv.1`)
  set ncfile=`echo $file | sed 's/csv.1/nc/'`
  /net/work/dev/jaa/aircraft_nc_utils/asc2cdf/asc2cdf -c $file $ncfile
end

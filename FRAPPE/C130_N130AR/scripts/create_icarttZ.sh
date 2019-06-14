#!/bin/csh

set nc2asc = "/opt/local/bin/nc2asc"

#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf01Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140726_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf02Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140727_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf03Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140728_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf04Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140729_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf05Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140731_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf06Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140802_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf07Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140803_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf08Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140806_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf09Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140807_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf10Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140808_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf11Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140811_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf12Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140812_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf13Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140815_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf14Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140816_R4.ict
#${nc2asc} -b RAF_templateZ -i $DAT/FRAPPErf15Z.nc -o $DAT/FRAPPE-NCAR-LRT-NAV_C130_20140818_R4.ict

# change revision #s from 0
sed -i -e 's/R0/R4/g' ${DAT}/FRAPPE-*_C130_*R4.ict

# change GV to C-130
sed -i -e 's/Aircraft location data is given in GV nav data file/Aircraft location data is given in C-130 nav data file/g' ${DAT}/FRAPPE-*_C130_*R4.ict

# change to Final Data
sed -i -e 's/R4: Field Data/R4: Final Data/g' ${DAT}/FRAPPE-*_C130_*R4.ict







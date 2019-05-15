#!/bin/bash
# Script to convert ascii text files with MR_UVH data to .nc and merge with main flight nc file for WE-CAN
UVH_NC=WECAN_UVHrf
DAT=/scr/raf_data/WECAN/uvh_merge/final_uvh_merge
PRODUCTION=/scr/raf/local_productiondata

# In text files, missing values should be updated to align with convention for missing data 
# Make sure that the header in the .txt files contains UTC, MR_UVH
# Time in seconds since midnight UTC and MR_UVH in ppmv
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf01.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf02.txt 
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf03.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf04.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf05.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf06.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf07.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf08.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf09.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf10.txt 
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf11.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf12.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf13.txt 
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf14.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf15.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf16.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf17.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf18.txt
sed -i -e 's/-99999.0/-32767/g' ${DAT}/rf19.txt

# Use asc2cdf to convert the text file to .nc
asc2cdf -d 2018-07-24 -m ${DAT}/rf01.txt ${DAT}/${UVH_NC}01.nc
asc2cdf -d 2018-07-26 -m ${DAT}/rf02.txt ${DAT}/${UVH_NC}02.nc
asc2cdf -d 2018-07-30 -m ${DAT}/rf03.txt ${DAT}/${UVH_NC}03.nc
asc2cdf -d 2018-07-31 -m ${DAT}/rf04.txt ${DAT}/${UVH_NC}04.nc
asc2cdf -d 2018-08-02 -m ${DAT}/rf05.txt ${DAT}/${UVH_NC}05.nc
asc2cdf -d 2018-08-03 -m ${DAT}/rf06.txt ${DAT}/${UVH_NC}06.nc
asc2cdf -d 2018-08-06 -m ${DAT}/rf07.txt ${DAT}/${UVH_NC}07.nc
asc2cdf -d 2018-08-08 -m ${DAT}/rf08.txt ${DAT}/${UVH_NC}08.nc
asc2cdf -d 2018-08-09 -m ${DAT}/rf09.txt ${DAT}/${UVH_NC}09.nc
asc2cdf -d 2018-08-13 -m ${DAT}/rf10.txt ${DAT}/${UVH_NC}10.nc
asc2cdf -d 2018-08-15 -m ${DAT}/rf11.txt ${DAT}/${UVH_NC}11.nc
asc2cdf -d 2018-08-16 -m ${DAT}/rf12.txt ${DAT}/${UVH_NC}12.nc
asc2cdf -d 2018-08-20 -m ${DAT}/rf13.txt ${DAT}/${UVH_NC}13.nc
asc2cdf -d 2018-08-23 -m ${DAT}/rf14.txt ${DAT}/${UVH_NC}14.nc
asc2cdf -d 2018-08-26 -m ${DAT}/rf15.txt ${DAT}/${UVH_NC}15.nc
asc2cdf -d 2018-08-28 -m ${DAT}/rf16.txt ${DAT}/${UVH_NC}16.nc
asc2cdf -d 2018-09-06 -m ${DAT}/rf17.txt ${DAT}/${UVH_NC}17.nc
asc2cdf -d 2018-09-10 -m ${DAT}/rf18.txt ${DAT}/${UVH_NC}18.nc
asc2cdf -d 2018-09-13 -m ${DAT}/rf19.txt ${DAT}/${UVH_NC}19.nc

# Use ncatted to update the long name and units in the newly created .nc files
ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}01.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}01.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}02.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}02.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}03.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}03.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}04.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}04.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}05.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}05.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}06.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}06.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}07.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}07.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}08.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}08.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}09.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}09.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}10.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}10.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}11.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}11.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}12.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}12.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}13.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}13.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}14.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}14.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}15.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}15.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}16.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}16.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}17.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}17.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}18.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}18.nc

ncatted -O -a long_name,MR_UVH,o,c,"UVH Volumetric Mixing Ratio Dry Air" ${DAT}/${UVH_NC}19.nc
ncatted -O -a units,MR_UVH,o,c,"ppmv" ${DAT}/${UVH_NC}19.nc

# After the .nc files are created containing the MR_UVH data, merge variable into main .nc files
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf01.nc ${DAT}/WECAN_UVHrf01.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf02.nc ${DAT}/WECAN_UVHrf02.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf03.nc ${DAT}/WECAN_UVHrf03.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf04.nc ${DAT}/WECAN_UVHrf04.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf05.nc ${DAT}/WECAN_UVHrf05.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf06.nc ${DAT}/WECAN_UVHrf06.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf07.nc ${DAT}/WECAN_UVHrf07.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf08.nc ${DAT}/WECAN_UVHrf08.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf09.nc ${DAT}/WECAN_UVHrf09.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf10.nc ${DAT}/WECAN_UVHrf10.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf11.nc ${DAT}/WECAN_UVHrf11.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf12.nc ${DAT}/WECAN_UVHrf12.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf13.nc ${DAT}/WECAN_UVHrf13.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf14.nc ${DAT}/WECAN_UVHrf14.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf15.nc ${DAT}/WECAN_UVHrf15.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf16.nc ${DAT}/WECAN_UVHrf16.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf17.nc ${DAT}/WECAN_UVHrf17.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf18.nc ${DAT}/WECAN_UVHrf18.nc
ncmerge -v MR_UVH ${PRODUCTION}/WECANrf19.nc ${DAT}/WECAN_UVHrf19.nc

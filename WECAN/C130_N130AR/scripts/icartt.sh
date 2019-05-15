#!/bin/bash

if [ "$UID" -eq 20000 ]; then
  DAT=/scr/raf/local_productiondata
else
  # Make sure files contain the merged CVI data
  # DAT=${DATA_DIR}/WECAN
  DAT=/scr/raf_data/WECAN/cvi_merge/Version1_1
fi
REV=R1
#BATCH_FILE=${PROJ_DIR}/WECAN/C130_N130AR/scripts/nc2asc.bat
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf01.nc -o ${DAT}/WECAN-CORE_C130_20180713_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf02.nc -o ${DAT}/WECAN-CORE_C130_20180717_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANff01.nc -o ${DAT}/WECAN-CORE_C130_20180720_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf01Z.nc -o ${DAT}/WECAN-CORE_C130_20180724_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf02Z.nc -o ${DAT}/WECAN-CORE_C130_20180726_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf03Z.nc -o ${DAT}/WECAN-CORE_C130_20180730_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf04Z.nc -o ${DAT}/WECAN-CORE_C130_20180731_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf05Z.nc -o ${DAT}/WECAN-CORE_C130_20180802_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf06Z.nc -o ${DAT}/WECAN-CORE_C130_20180803_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf07Z.nc -o ${DAT}/WECAN-CORE_C130_20180806_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf08Z.nc -o ${DAT}/WECAN-CORE_C130_20180808_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf09Z.nc -o ${DAT}/WECAN-CORE_C130_20180809_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf10Z.nc -o ${DAT}/WECAN-CORE_C130_20180813_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf11Z.nc -o ${DAT}/WECAN-CORE_C130_20180815_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf12Z.nc -o ${DAT}/WECAN-CORE_C130_20180816_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf13Z.nc -o ${DAT}/WECAN-CORE_C130_20180820_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf14Z.nc -o ${DAT}/WECAN-CORE_C130_20180823_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf15Z.nc -o ${DAT}/WECAN-CORE_C130_20180826_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf16Z.nc -o ${DAT}/WECAN-CORE_C130_20180828_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf17Z.nc -o ${DAT}/WECAN-CORE_C130_20180906_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf18Z.nc -o ${DAT}/WECAN-CORE_C130_20180910_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf19Z.nc -o ${DAT}/WECAN-CORE_C130_20180913_${REV}.ict

BATCH_FILE=${PROJ_DIR}/WECAN/C130_N130AR/scripts/nc2asc_cvi.bat
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf01.nc -o ${DAT}/WECAN-CVI_C130_20180713_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf02.nc -o ${DAT}/WECAN-CVI_C130_20180717_${REV}.ict
#nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANff01.nc -o ${DAT}/WECAN-CVI_C130_20180720_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf01Z.nc -o ${DAT}/WECAN-CVI_C130_20180724_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf02Z.nc -o ${DAT}/WECAN-CVI_C130_20180726_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf03Z.nc -o ${DAT}/WECAN-CVI_C130_20180730_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf04Z.nc -o ${DAT}/WECAN-CVI_C130_20180731_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf05Z.nc -o ${DAT}/WECAN-CVI_C130_20180802_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf06Z.nc -o ${DAT}/WECAN-CVI_C130_20180803_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf07Z.nc -o ${DAT}/WECAN-CVI_C130_20180806_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf08Z.nc -o ${DAT}/WECAN-CVI_C130_20180808_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf09Z.nc -o ${DAT}/WECAN-CVI_C130_20180809_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf10Z.nc -o ${DAT}/WECAN-CVI_C130_20180813_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf11Z.nc -o ${DAT}/WECAN-CVI_C130_20180815_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf12Z.nc -o ${DAT}/WECAN-CVI_C130_20180816_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf13Z.nc -o ${DAT}/WECAN-CVI_C130_20180820_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf14Z.nc -o ${DAT}/WECAN-CVI_C130_20180823_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf15Z.nc -o ${DAT}/WECAN-CVI_C130_20180826_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf16Z.nc -o ${DAT}/WECAN-CVI_C130_20180828_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf17Z.nc -o ${DAT}/WECAN-CVI_C130_20180906_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf18Z.nc -o ${DAT}/WECAN-CVI_C130_20180910_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf19Z.nc -o ${DAT}/WECAN-CVI_C130_20180913_${REV}.ict

# change revision #s from 0
sed -i -e 's/R0/R1/g' ${DAT}/WECAN-*_C130_*R1.ict

# change GV to C-130
sed -i -e 's/Aircraft location data is given in GV nav data file/Aircraft location data is given in C-130 nav data file/g' ${DAT}/WECAN-*_C130_*R1.ict

# change to Final Data
sed -i -e 's/R1: Field Data/R1: Final Data/g' ${DAT}/WECAN-*_C130_*R1.ict

# CVI updates for Cindy T. 
sed -i -e 's/CVINLET,",CVI inlet flag, 0=CVI, 1=Total/CVINLET,",CVI inlet flag, 0=CVI, 1=Total, 2=SDI/g' ${DAT}/WECAN-CVI*_C130_*R1.ict
sed -i -e 's/DATA_INFO: data reported in ambient condition, ambient temperature and pressure are given for conversion to STP (273.15K and 1013 mb)/DATA_INFO:CVCWCC and CONCU_CVIU reported in ambient units, use ambient temperature and pressure from aircraft file for conversion to STP (273.15K and 1013 mb)/g' ${DAT}/WECAN-CVI*_C130_*R1.ict
sed -i -e 's/Romashkin, Pavel/Toohey, Darin/g' ${DAT}/WECAN-CVI*_C130_*R1.ict
sed -i -e 's/Pavel Romashkin/Darin Toohey/g' ${DAT}/WECAN-CVI*_C130_*R1.ict

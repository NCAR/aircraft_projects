#!/bin/bash

if [ "$UID" -eq 20000 ]; then
  DAT=/scr/raf/local_productiondata
else
  DAT=${DATA_DIR}/WECAN
fi
REV=RC
BATCH_FILE=${PROJ_DIR}/WECAN/C130_N130AR/scripts/nc2asc.bat
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf01.nc -o ${DAT}/WECAN-CORE_C130_20180713_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf02.nc -o ${DAT}/WECAN-CORE_C130_20180717_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANff01.nc -o ${DAT}/WECAN-CORE_C130_20180720_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf01.nc -o ${DAT}/WECAN-CORE_C130_20180724_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf02.nc -o ${DAT}/WECAN-CORE_C130_20180726_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf03.nc -o ${DAT}/WECAN-CORE_C130_20180730_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf04.nc -o ${DAT}/WECAN-CORE_C130_20180731_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf05.nc -o ${DAT}/WECAN-CORE_C130_20180802_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf06.nc -o ${DAT}/WECAN-CORE_C130_20180803_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf07.nc -o ${DAT}/WECAN-CORE_C130_20180806_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf08.nc -o ${DAT}/WECAN-CORE_C130_20180808_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf09.nc -o ${DAT}/WECAN-CORE_C130_20180809_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf10.nc -o ${DAT}/WECAN-CORE_C130_20180813_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf11.nc -o ${DAT}/WECAN-CORE_C130_20180815_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf12.nc -o ${DAT}/WECAN-CORE_C130_20180816_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf13.nc -o ${DAT}/WECAN-CORE_C130_20180820_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf14.nc -o ${DAT}/WECAN-CORE_C130_20180823_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf15.nc -o ${DAT}/WECAN-CORE_C130_20180826_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf16.nc -o ${DAT}/WECAN-CORE_C130_20180828_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf17.nc -o ${DAT}/WECAN-CORE_C130_20180906_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf18.nc -o ${DAT}/WECAN-CORE_C130_20180910_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf19.nc -o ${DAT}/WECAN-CORE_C130_20180913_${REV}.ict

BATCH_FILE=${PROJ_DIR}/WECAN/C130_N130AR/scripts/nc2asc_cvi.bat
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf01.nc -o ${DAT}/WECAN-CVI_C130_20180713_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf02.nc -o ${DAT}/WECAN-CVI_C130_20180717_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANff01.nc -o ${DAT}/WECAN-CVI_C130_20180720_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf01.nc -o ${DAT}/WECAN-CVI_C130_20180724_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf02.nc -o ${DAT}/WECAN-CVI_C130_20180726_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf03.nc -o ${DAT}/WECAN-CVI_C130_20180730_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf04.nc -o ${DAT}/WECAN-CVI_C130_20180731_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf05.nc -o ${DAT}/WECAN-CVI_C130_20180802_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf06.nc -o ${DAT}/WECAN-CVI_C130_20180803_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf07.nc -o ${DAT}/WECAN-CVI_C130_20180806_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf08.nc -o ${DAT}/WECAN-CVI_C130_20180808_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf09.nc -o ${DAT}/WECAN-CVI_C130_20180809_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf10.nc -o ${DAT}/WECAN-CVI_C130_20180813_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf11.nc -o ${DAT}/WECAN-CVI_C130_20180815_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf12.nc -o ${DAT}/WECAN-CVI_C130_20180816_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf13.nc -o ${DAT}/WECAN-CVI_C130_20180820_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf14.nc -o ${DAT}/WECAN-CVI_C130_20180823_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf15.nc -o ${DAT}/WECAN-CVI_C130_20180826_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf16.nc -o ${DAT}/WECAN-CVI_C130_20180828_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf17.nc -o ${DAT}/WECAN-CVI_C130_20180906_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf18.nc -o ${DAT}/WECAN-CVI_C130_20180910_${REV}.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf19.nc -o ${DAT}/WECAN-CVI_C130_20180913_${REV}.ict

# change revision #s from 0 to C
sed -i -e 's/R0/RC/g' ${DAT}/WECAN-*_C130_*RC.ict
# change GV to C-130
sed -i -e 's/Aircraft location data is given in GV nav data file/Aircraft location data is given in C-130 nav data file/g' ${DAT}/WECAN-*_C130_*RC.ict
# change final verbiage to preliminary
sed -i -e 's/Final data for publication use/This file contains PRELIMINARY DATA that are NOT to be used for critical analysis./g' ${DAT}/WECAN-*_C130_*RC.ict

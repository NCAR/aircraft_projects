#!/bin/bash

if ($uid == 20000) then
  setenv DAT /scr/raf/local_productiondata
else
  setenv DAT ${DATA_DIR}/WECAN
endif

BATCH_FILE=${PROJ_DIR}/WECAN/C130_N130AR/scripts/nc2asc.bat

nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf01.nc -o ${DAT}/WECAN-CORE_C130_20180713_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANtf02.nc -o ${DAT}/WECAN-CORE_C130_20180717_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANff01.nc -o ${DAT}/WECAN-CORE_C130_20180720_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf01.nc -o ${DAT}/WECAN-CORE_C130_20180724_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf02.nc -o ${DAT}/WECAN-CORE_C130_20180726_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf03.nc -o ${DAT}/WECAN-CORE_C130_20180730_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf04.nc -o ${DAT}/WECAN-CORE_C130_20180731_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf05.nc -o ${DAT}/WECAN-CORE_C130_20180802_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf06.nc -o ${DAT}/WECAN-CORE_C130_20180803_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf07.nc -o ${DAT}/WECAN-CORE_C130_20180806_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf08.nc -o ${DAT}/WECAN-CORE_C130_20180808_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf09.nc -o ${DAT}/WECAN-CORE_C130_20180809_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf10.nc -o ${DAT}/WECAN-CORE_C130_20180813_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf11.nc -o ${DAT}/WECAN-CORE_C130_20180815_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf12.nc -o ${DAT}/WECAN-CORE_C130_20180816_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf13.nc -o ${DAT}/WECAN-CORE_C130_20180820_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf14.nc -o ${DAT}/WECAN-CORE_C130_20180823_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf15.nc -o ${DAT}/WECAN-CORE_C130_20180826_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf16.nc -o ${DAT}/WECAN-CORE_C130_20180828_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf17.nc -o ${DAT}/WECAN-CORE_C130_20180906_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf18.nc -o ${DAT}/WECAN-CORE_C130_20180910_RA.ict
nc2asc -b ${BATCH_FILE} -i ${DAT}/WECANrf19.nc -o ${DAT}/WECAN-CORE_C130_20180913_RA.ict

# change revision #s from 0 to A
sed -i -e 's/R0/RA/g' ${DAT}/WECAN-CORE_C130_*RA.ict

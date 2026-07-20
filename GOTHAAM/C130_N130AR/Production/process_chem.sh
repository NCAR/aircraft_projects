#!/bin/bash
## This script will convert ICARTT files, merge the GOTHAAM coreChem data files and create a single netCDF file for each flight
version=R0

asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250722_${version}.ict chem_GOTHAAMrf01.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250723_${version}.ict chem_GOTHAAMrf02.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250724_${version}.ict chem_GOTHAAMrf03.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250725_${version}.ict chem_GOTHAAMrf04.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250729_${version}.ict chem_GOTHAAMrf05.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250730_${version}.ict chem_GOTHAAMrf06.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250803_${version}.ict chem_GOTHAAMrf07.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250804_${version}.ict chem_GOTHAAMrf08.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250805_${version}.ict chem_GOTHAAMrf09.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250806_${version}.ict chem_GOTHAAMrf10.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250808_${version}.ict chem_GOTHAAMrf11.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250812_${version}.ict chem_GOTHAAMrf12.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250813_${version}.ict chem_GOTHAAMrf13.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250815_${version}.ict chem_GOTHAAMrf14.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250816_${version}.ict chem_GOTHAAMrf15.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250819_${version}.ict chem_GOTHAAMrf16.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250822_${version}.ict chem_GOTHAAMrf17.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250823_${version}.ict chem_GOTHAAMrf18.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250824_${version}.ict chem_GOTHAAMrf19.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250827_${version}.ict chem_GOTHAAMrf20.nc
asc2cdf -i coreChem_ict/GOTHAAM-RAFCoreChemistry_C130_20250828_${version}.ict chem_GOTHAAMrf21.nc

for file in GOTHAAMrf??.nc
do
  echo merging $file
  ncmerge $file coreChem_ict/nc/chem_${file}
done

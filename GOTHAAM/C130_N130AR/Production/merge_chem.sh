#!/bin/bash
# This script will convert ICARTT files, merge the GOTHAAM coreChem data files
# and create a single netCDF file for each flight

chem_version=R0
nc_version=V1.2

# Declare base dir where data lives
basedir=/scr/raf/Prod_Data/GOTHAAM

# date (YYYYMMDD) -> flight number
declare -A flight=(
  [20250722]=rf01 [20250723]=rf02 [20250724]=rf03 [20250725]=rf04
  [20250729]=rf05 [20250730]=rf06 [20250803]=rf07 [20250804]=rf08
  [20250805]=rf09 [20250806]=rf10 [20250808]=rf11 [20250812]=rf12
  [20250813]=rf13 [20250815]=rf14 [20250816]=rf15 [20250819]=rf16
  [20250822]=rf17 [20250823]=rf18 [20250824]=rf19 [20250827]=rf20
  [20250828]=rf21)

for file in ${basedir}/coreChem_ict/*_${chem_version}.ict
do
  # Pull the 8 digit date out of the filename
  if [[ $(basename "$file") =~ _([0-9]{8})_ ]]; then
    date=${BASH_REMATCH[1]}
    rf=${flight[$date]}
    if [[ -z $rf ]]; then
      echo "WARNING: no flight mapping for date $date ($file) -- skipping" >&2
      continue
    fi
    asc2cdf -i "$file" "${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc"

    # When the merge is run, the long_name in the provided file will overwrite
    # the name in the base LRT file. Correct the names before that is done
    ncatted -a long_name,FO3_RAF,o,c,"NSF NCAR Chemiluminescence Ozone Mixing Ratio" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,N2O_QCL,o,c,"Aerodyne Mini 108 Nitrous Oxide Mixing Ratio" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,H2O_QCL,o,c,"Aerodyne Mini 108 Water Mixing Ratio" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,H2O_PIC,o,c,"Picarro H2O Mixing Ratio" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,CO2_PIC,o,c,"Picarro Carbon Dioxide Mixing Ratio (Raw)" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,CO_QCL,o,c,"Aerodyne Mini 108 Carbon Monoxide Mixing Ratio" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,CO_PIC,o,c,"Picarro Carbon Monoxide Mixing Ratio" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncatted -a long_name,CH4_PIC,o,c,"Picarro Methane Mixing Ratio (Raw)" \
        ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc

    # The variables called CO2_PIC and CH4_PIC need to be renamed to 
    # corrected (CO2C_PIC, CH4C_PIC)
    ncrename -v CO2_PIC,CO2C_PIC ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc
    ncrename -v CH4_PIC,CH4C_PIC ${basedir}/coreChem_ict/nc/chem_GOTHAAM${rf}.nc

  else
    echo "WARNING: could not parse date from $file -- skipping" >&2
  fi
done


if [ `whoami` == nimbus ]; then
  filedir=/scr/raf/local_productiondata
else
  filedir=${basedir}/LRT/${nc_version}
fi

for filepath in ${filedir}/GOTHAAMrf??.nc
do
  ncfile=$(basename "$filepath")
  echo "merging ${basedir}/coreChem_ict/nc/chem_$ncfile into $filepath"
  ncmerge $filepath ${basedir}/coreChem_ict/nc/chem_$ncfile
done

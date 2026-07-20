#!/bin/bash
# This script will convert ICARTT files, merge the GOTHAAM coreChem data files
# and create a single netCDF file for each flight

chem_version=R0
nc_version=V1.1

# Declare base dir where data lives
basedir=/scr/raf/Prod_Data/GOTHAAM

# date (YYYYMMDD) -> flight number
declare -A flight=(
  [20250722]=rf01 [20250723]=rf02 [20250724]=rf03 [20250725]=rf04
  [20250729]=rf05 [20250730]=rf06 [20250803]=rf07 [20250804]=rf08
  [20250805]=rf09 [20250806]=rf10 [20250808]=rf11 [20250812]=rf12
  [20250813]=rf13 [20250815]=rf14 [20250816]=rf15 [20250819]=rf16
  [20250822]=rf17 [20250823]=rf18 [20250824]=rf19 [20250827]=rf20
  [20250828]=rf21
)

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
    asc2cdf -i "$file" "chem_GOTHAAM${rf}.nc"
  else
    echo "WARNING: could not parse date from $file -- skipping" >&2
  fi
done

for filepath in ${basedir}/LRT/${nc_version}/GOTHAAMrf??.nc
do
  echo merging $filepath
  ncfile=$(basename "$filepath")
  ncmerge $filepath ${basedir}/coreChem_ict/nc/chem_$ncfile
done

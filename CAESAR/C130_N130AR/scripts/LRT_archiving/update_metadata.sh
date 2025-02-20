#!/bin/bash

# Loop through all files matching the pattern
for file in CAESARrf??.nc; do
  echo "Updating metadata for file: $file"

  # Add units attribute to CDP016_bnds
  ncatted -a units,CDP016_bnds,o,c,"um" $file

  # Add units attribute to CDP058_bnds
  ncatted -a units,CDP058_bnds,o,c,"um" $file

  # Add units attribute to UHSAS011_bnds
  ncatted -a units,UHSAS011_bnds,o,c,"um" $file

  # Add units attribute to PCAS108_bnds
  ncatted -a units,PCAS108_bnds,o,c,"um" $file

  # P2D variables
  ncatted -a units,F2DS020_P2D,o,c,"um" $file
  ncatted -a units,F2DC003_P2D,o,c,"um" $file
  ncatted -a units,HVPS315_P2D,o,c,"um" $file

  ##Add Long Name
  ncatted -a long_name,F2DS020_P2D,o,c,"F2DS arithmetic midpoint bin size in diameter" $file
  ncatted -a long_name,F2DC003_P2D,o,c,"Fast2DC_v2 arithmetic midpoint bin size in diameter" $file
  ncatted -a long_name,HVPS315_P2D,o,c,"HVPS arithmetic midpoint bin size in diameter" $file
done

echo "Finished updating all files."

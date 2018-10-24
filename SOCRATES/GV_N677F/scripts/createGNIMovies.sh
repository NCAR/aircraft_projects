#!/bin/csh

# Convert GNI images from pgm to png
#foreach file (/scr/raf/Prod_Data/SOCRATES/GNI/images/*pgm)
#    set outfile=`echo $file | sed 's/pgm/png/'`
#    convert -quality 100 -density 1600x1200 $file $outfile
#end

# Create movie named gni_movie.mp4
nice +19 ./combineGNIslides.pl GNI.paramfile

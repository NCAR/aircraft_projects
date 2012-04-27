#!/bin/csh
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf01
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf02
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf03
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf04
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf05
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf06
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf07
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf08
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf09
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf10 
#/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.ParamFile rf11

################################################################################
# THIS IS A HIGH-RES VERSION OF A SUBSET OF RF06 CREATED FOR a gentleman at the 
# American Academy of Science.
#
# I considered feeding the files in
# /scr/raf/Raw_Data/HIPPO-3/movie_for_AAS/flight_number_rf06/forward directly 
# into ffmpeg because the resolution is the same, but then realized that the 
# camera software sharpens the image so decided to run that first (as usual).
#
# ffmpeg command:
#/net/work/bin/converters/createMovies/ffmpeg -passlogfile ./ffmpeg_rf06 -r 15 -b 1500000 -y
#-pass 2 -i /scr/raf/Prod_Data/HIPPO-3/Movies/for_AAS/AnnotatedImages_rf06/%05d.jpg
#/scr/raf/Prod_Data/HIPPO-3/Movies/for_AAS/rf06.100405.232355_004159.mp4
################################################################################
/net/work/bin/converters/createMovies/combineCameras.pl HIPPO-3.for_AAS.ParamFile rf06

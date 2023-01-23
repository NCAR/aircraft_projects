#!/bin/csh
perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf_data/PREDICT/movie_processing_2023/FWD" "-proj:PREDICT" "-s:15" "-t:5i"
perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf_data/PREDICT/movie_processing_2023/LEFT" "-proj:PREDICT" "-s:15"
perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf_data/PREDICT/movie_processing_2023/RIGHT" "-proj:PREDICT" "-s:15"

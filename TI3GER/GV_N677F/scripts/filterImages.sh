#! /bin/csh -f

perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera/flight_number_rf08/forward/" "-s:60" "-t:5i"
perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera/flight_number_rf08/left/" "-s:60" "-t:5i"
perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera/flight_number_rf08/right/" "-s:60" "-t:5i"
perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera/flight_number_rf08/down/" "-s:60" "-t:5i"

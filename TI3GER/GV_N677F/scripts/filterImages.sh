#! /bin/csh -f
FLIGHT='rf01'

perl ./Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera_images/flight_number_$FLIGHT/forward/" "-s:60" "-t:5i"
perl ./Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera_images/flight_number_$FLIGHT/right/" "-s:60" "-t:5i"
perl ./Image_Filter.pl "/scr/raf/Raw_Data/TI3GER/camera_images/flight_number_$FLIGHT/down/" "-s:60" "-t:5i"

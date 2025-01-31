#! /bin/csh -f

set FLIGHT="rf01"
set PROJECT="ACES"

perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf/Raw_Data/$PROJECT/flight_number_$FLIGHT/forward/" "-s:60" "-t:5i" "-proj:$PROJECT"

#perl /net/jlocal/projects/scripts/camera/Image_Filter.pl "/scr/raf/Raw_Data/<PROJECT>/flight_number_$FLIGHT/forward/" "-s:60" "-t:5i"
#perl ./Image_Filter.pl "/scr/raf/Raw_Data/<PROJECT>/camera_images/flight_number_$FLIGHT/left/" "-s:60" "-t:5i"
#perl ./Image_Filter.pl "/scr/raf/Raw_Data/<PROJECT>/camera_images/flight_number_$FLIGHT/right/" "-s:60" "-t:5i"
#perl ./Image_Filter.pl "/scr/raf/Raw_Data/<PROJECT>/camera_images/flight_number_$FLIGHT/down/" "-s:60" "-t:5i"

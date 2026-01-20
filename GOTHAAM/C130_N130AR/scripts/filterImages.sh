#! /bin/csh -f

echo "Set flight and project, uncomment, then comment out this line"
set FLIGHT=rf01
set PROJECT=GOTHAAM

perl ./Image_Filter.pl "/scr/raf/Raw_Data/$PROJECT/CAMERA/flight_number_$FLIGHT/forward/" "-s:60" "-t:5i" "-proj:$PROJECT"
#perl ./Image_Filter.pl "/scr/raf/Raw_Data/$PROJECT/CAMERA/flight_number_$FLIGHT/left/" "-s:60" "-t:5i" "-proj:$PROJECT"
#perl ./Image_Filter.pl "/scr/raf/Raw_Data/$PROJECT/CAMERA/flight_number_$FLIGHT/right/" "-s:60" "-t:5i" "-proj:$PROJECT"
perl ./Image_Filter.pl "/scr/raf/Raw_Data/$PROJECT/CAMERA/flight_number_$FLIGHT/down/" "-s:60" "-t:5i" "-proj:$PROJECT"

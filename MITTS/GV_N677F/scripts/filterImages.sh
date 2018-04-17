#!/bin/csh

# MITTS only flew a left-facing camera
#/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_rf01/forward/" "-proj:MITTS" "-s:15"
#/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_rf02/forward/" "-proj:MITTS" "-s:15"
#/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_rf03/forward/" "-proj:MITTS" "-s:15"
#/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_tf01/forward/" "-proj:MITTS" "-s:15"

/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_rf01/left/" "-proj:MITTS" "-s:15"
/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_rf02/left/" "-proj:MITTS" "-s:15"
/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_rf03/left/" "-proj:MITTS" "-s:15"
/net/work/bin/converters/ImageFilter/Image_Filter.pl "/scr/raf/Raw_Data/MITTS/camera_images/flight_number_tf01/left/" "-proj:MITTS" "-s:15"

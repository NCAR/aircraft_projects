#! /bin/csh -f

perl /home/local/projects/scripts/camera/Image_Filter.pl "/var/r1/TI3GER/camera_images/flight_number_ff01/forward/" "-s:60" "-t:5i"
perl /home/local/projects/scripts/camera/Image_Filter.pl "/var/r1/TI3GER/camera_images/flight_number_ff01/left/" "-s:60" "-t:5i"
perl /home/local/projects/scripts/camera/Image_Filter.pl "/var/r1/TI3GER/camera_images/flight_number_ff01/right/" "-s:60" "-t:5i"
perl /home/local/projects/scripts/camera/Image_Filter.pl "/var/r1/TI3GER/camera_images/flight_number_ff01/down/" "-s:60" "-t:5i"

# Must be run as user dmg on bora because the version of Python on tsunami
# does not have some of the libraries I used. tsunami is RHEL 4.
# It will NOT be upgraded. The plan is to spec and purchase a new 
# server to replace it. The timeline will probably be in the fall at soonest.
#
# Note that merlot and shiraz also have access to the needed libraries, not just
# bora, so test code on those too.

#../../../../../archAC/archAC.py ADS /net/work/dev/jaa/archcam_archAC_merge/data/ads ads RAF
../../../../../archAC.py LRT ../../../../../data/LRT nc ATDdata
#../../../../../archAC.py CAMERA -p FWD ../../../../../data/GV/camera jpg ATDdata
#../../../../../archAC/archAC.py CAMERA ../../../../../data/GV/camera/flight_number_rf01 jpg RAF

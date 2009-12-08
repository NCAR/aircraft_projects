#!/bin/csh
# Must be run as user dmg on tsunami because the version of tcsh on tsunami
# is old and does NOT interpret the number 08 as octal. Newer versions do
# which causes the code to crash.
../../../../../archcam/archcam.ppp.fwd -r -f RF01 -t -v -d
#../../../../../archcam/archcam.ppp.fwd -r -f RF01 -t -p


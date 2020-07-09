#!/bin/bash
# Script to check on proper GV Forward camera operation. Goes into the camera
# directory, reads the camera.log file to find the latest entry which points to
# the directory being used. Then reads this directory for the latest file, waits,
# and reads it again for up to 5 seconds. A new image should have arrived by then.

# DEPENDS ON
#    Images arriving faster than every 5 seconds (set in camera acq. program).
#    $imageDirectory must match location given in dsmc01:/home/ads/startCamera
#        modified by mount point in dsmc01:/etc/fstab.
#    camera.log must match location and format in dsmc01:/home/ads/startCamera.

cameraLog="/mnt/r1/camera/FwdCam/camera.log"
# directory name starts at the 38th character.
imageDirectory="/mnt/r1/camera/FwdCam/`tail -n1 $cameraLog |cut -c 38-`"

if [ -d $imageDirectory ]; then

last=`ls -t $imageDirectory |head -n1`
echo "Camera files being stored to : " $imageDirectory
echo "Checking camera files..."
sleep 2

#See if new file arrived. Repeat.
for ((i=0; i<5; i++));do
        curr=`ls -t $imageDirectory |head -n1`
        if [ $curr != $last ]; then
	        echo "New images arriving OK!"
		echo "Displaying most recent image for 10 seconds"
		display $imageDirectory$last &
		sleep 10
	        exit
	fi
        sleep 1
	echo "still checking..."
done

# Shouldn't get here unless no new images arrived.
echo "No new camera images found!"
echo "Check DSMC01 power, or wait for plane to be airborne at least 10 seconds." 
sleep 20

else

   echo "ERROR: Image Directory: "
   echo "     $imageDirectory"
   echo "DOES NOT EXIST - is camera on?"
   sleep 20
fi

#! /bin/bash
###----------------------------------------------------------------------------
# script to tar and copy image files from aircraft to transfer media for a given flight
# after connecting removable drive, run script to transfer file(s)
###----------------------------------------------------------------------------
# assign list of parameters for transferring data
#PROJECT="OTREC"

DATA_LOCATION="/var/r1/$PROJECT/camera_images"

TRANSFER_MEDIA="/run/media/ads/*"

echo "Enter flight to copy from $PROJECT using lower case e.g. rf01 or ff03:"
read FLIGHT

if [[ $FLIGHT = *"rf"* ]]; then
   echo "Research flight images from $PROJECT selected for copying."
elif [[ "$FLIGHT" = *"tf"* ]]; then
   echo "Test flight images from $PROJECT selected for copying."
elif [[ "$FLIGHT" = *"ff"* ]]; then
   echo "Ferry flight images from $PROJECT selected for copying."
elif [[ "$FLIGHT" = *"cf"* ]]; then
   echo "Calibration images flight from $PROJECT selected for copying."
else 
   echo "You have selected something other than a research, test, ferry, or calibration flight from $PROJECT."
fi

test -d $DATA_LOCATION/flight_number_$FLIGHT/
DIR=$?
test -f $DATA_LOCATION/flight_number_$FLIGHT.tar
TAR_FILE=$?

if [ $DIR -eq 0 ]; then
   echo "Do you have a removable drive connected?"
   echo "Please type Y or y and press enter to confirm. Anything else and enter will stop script."
   read DRIVE_CONNECTION
   if [ $DRIVE_CONNECTION == "Y" ] || [ $DRIVE_CONNECTION == "y" ]; then
      echo "You entered $DRIVE_CONNECTION, which means you have a drive connected."
      if [ $TAR_FILE -eq 0 ]; then
         rsync -cav --no-perms --no-owner --no-group $DATA_LOCATION/flight_number_$FLIGHT.tar $TRANSFER_MEDIA/$PROJECT
         EXIT="$?"
         echo "rsync exit status: $EXIT"
         if [ $EXIT -eq 0 ]; then
            echo "Copy of camera_images .tar file for $PROJECT$FLIGHT SUCCESSFUL. Please wait for drive to unmount."
	    umount $TRANSFER_MEDIA;
            echo "The removable drive has been unmounted and is safe to remove."
            sleep 8
         elif [ $EXIT -gt 0 ]; then
            echo "Copy of camera_images .tar file for $PROJECT$FLIGHT UNSUCCESSFUL."
            echo "Please check the files and try again."
            sleep 8
         else
            echo "rsync error"
            sleep 8
         fi
      elif [ $TAR_FILE -gt 0 ]; then
         echo "No .tar file for flight_number_$FLIGHT found, creating tar file."
         cd $DATA_LOCATION
         tar -cvf flight_number_$FLIGHT.tar flight_number_$FLIGHT
         rsync -cav --no-perms --no-owner --no-group flight_number_$FLIGHT.tar $TRANSFER_MEDIA/$PROJECT
         EXIT="$?"
         echo "rsync exit status: $EXIT" 
         if [ $EXIT -eq 0 ]; then
            echo "Copy of camera_images .tar file for $PROJECT$FLIGHT SUCCESSFUL."
            umount $TRANSFER_MEDIA;
            echo "You can now safely remove the drive by right-clicking the desktop icon."
            sleep 8
         elif [ $EXIT -gt 0 ]; then
            echo "Copy of camera_images .tar file for $PROJECT$FLIGHT UNSUCCESSFUL."
            echo "Please check the files and try again."
            sleep 8
         else
            echo "rsync error"
            sleep 8
         fi
      else
         echo "Unable to determine existence of a .tar file for the images."
         sleep 8        
      fi  
   else
      echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."
      sleep 8
   fi
else
   echo "There is no directory containing the $PROJECT$FLIGHT images you selected."
   sleep 8
fi

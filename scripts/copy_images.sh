#! /bin/bash
SECONDS=0  # Time script
###----------------------------------------------------------------------------
# Script to tar and copy image files from aircraft to transfer media for a given
# flight. After connecting removable drive, run script to transfer file(s)
###----------------------------------------------------------------------------
# assign list of parameters for transferring data

# On planes and lab stations $PROJECT environment variable should be set by
# the script ads3_environment.sh currently in /home/ads

DATA_LOCATION="/var/r1/$PROJECT/camera_images"
cd /run/media/ads
DRIVE=$(ls)
echo $DRIVE
TRANSFER_MEDIA="/run/media/ads/$DRIVE"

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

if [ $DIR -ne 0 ]; then
   echo "There is no directory containing the $PROJECT$FLIGHT images you selected."
else
   echo "Do you have a removable drive connected?"
   echo "Please type Y or y and press enter to confirm. Anything else and enter will stop script."
   read DRIVE_CONNECTION
   if [ $DRIVE_CONNECTION == "Y" ] || [ $DRIVE_CONNECTION == "y" ]; then
      echo "****************************************************************"
      echo "You entered $DRIVE_CONNECTION, which means you have a drive connected."

      mkdir -p $TRANSFER_MEDIA/$PROJECT
      EXIT_MKDIR="$?"

      if [ "$EXIT_MKDIR" -ne 0 ]; then
         echo "command mkdir -p $TRANSFER_MEDIA/$PROJECT not done, if folder was already made, no issues..."
      else
         echo "command mkdir -p $TRANSFER_MEDIA/$PROJECT was successful"
      fi

      test -d $TRANSFER_MEDIA/$PROJECT/
      DRIVEDIR=$?
      if [ "$DRIVEDIR" -eq 0 ]; then

         if [ $TAR_FILE -gt 0 ]; then
            echo "No .tar file for flight_number_$FLIGHT found, creating tar file."
            tar -cvf $DATA_LOCATION/flight_number_$FLIGHT.tar -C $DATA_LOCATION --exclude='*/sent' flight_number_$FLIGHT/
         fi

         echo "***Starting file transfer. Please wait for transfer and integrity checking to complete.***"
         rsync -cavP --no-perms --no-owner --no-group $DATA_LOCATION/flight_number_$FLIGHT.tar $TRANSFER_MEDIA/$PROJECT/flight_number_$FLIGHT.tar
         echo "***Sync cached data to permanent memory - can take 2-5 minutes.***"
         echo "sync started at $(date)"
         sync
         EXIT_RSYNC="$?"
         echo "rsync exit status: $EXIT_RSYNC"

         echo "****************************************************************"
         echo "Calculating sha256sum for original file(s)..."
         sha256sum $DATA_LOCATION/*$FLIGHT*.tar >> $DATA_LOCATION/sha256sum.ads_station
         echo "************************************************************"
         echo "****************************************************************"
         echo "Calculating sha256sum for copied file(s)..."
         sha256sum $TRANSFER_MEDIA/$PROJECT/*$FLIGHT*.tar
         echo "****************************************************************"

         if [ $EXIT_RSYNC -eq 0 ]; then
            echo "Copy of camera_images .tar file for $PROJECT$FLIGHT SUCCESSFUL."
            echo "You can now safely remove the drive by right-clicking the desktop icon."
            echo "*** Note: This script does not eject the drive in case you still need to copy camera images.***"
         elif [ $EXIT_RSYNC -gt 0 ]; then
            echo "Copy of camera_images .tar file for $PROJECT$FLIGHT UNSUCCESSFUL."
            echo "Please check the files and try again."
         else
            echo "rsync error"
         fi

      else
         echo "Cound not locate dir $TRANSFER_MEDIA/$PROJECT"
      fi

   else
      echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."
   fi
fi

echo "****************************************************************"
echo "*** Note: This script does not eject the drive in case you still need to copy data files.***"
echo "****************************************************************"
echo "Script took $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"

read -p "Press enter key to exit script and close terminal"

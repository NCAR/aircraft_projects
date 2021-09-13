#!/bin/bash
###----------------------------------------------------------------------------
# script to copy .ads files from aircraft to transfer media for a given flight
# after connecting removable drive, run script to transfer file(s)
###----------------------------------------------------------------------------
# assign list of parameters for transferring data

# On planes and lab stations $PROJECT environment variable should be set by 
# the script ads3_environment.sh currently in /home/ads 

DATA_LOCATION="/var/r1/$PROJECT"
TRANSFER_MEDIA="/run/media/ads/*"

echo "Enter flight to copy from $PROJECT e.g. rf01 or ff03:"
read FLIGHT
if [[ $FLIGHT = *"rf"* ]]; then
   echo "Research flight from $PROJECT selected for copying."
elif [[ "$FLIGHT" = *"tf"* ]]; then
   echo "Test flight from $PROJECT selected for copying."
elif [[ "$FLIGHT" = *"ff"* ]]; then
   echo "Ferry flight from $PROJECT selected for copying."
elif [[ "$FLIGHT" = *"cf"* ]]; then
   echo "Calibration flight from $PROJECT selected for copying."
else
   echo "You have selected something other than a research, test, ferry, or calibration flight from $PROJECT."
fi

echo "Do you have a removable drive connected?"
echo "Please type Y or y and press enter to confirm. Anything else and enter will stop script."
read DRIVE_CONNECTION
if [ $DRIVE_CONNECTION == "Y" ] || [ $DRIVE_CONNECTION == "y" ]; then
   mkdir -p $TRANSFER_MEDIA/$PROJECT
   EXIT_MKDIR="$?"

   if [ "$EXIT_MKDIR" -eq 0 ]; then
      echo "WARNING: command mkdir -p $TRANSFER_MEDIA/$PROJECT failed!"
   else
      echo "command mkdir -p $TRANSFER_MEDIA/$PROJECT was successful"
   fi

   echo "************************************************************"
   echo "You entered $DRIVE_CONNECTION, which means you have a drive connected.";
   echo "***Starting file transfer. Please wait for transfer and integrity checking to complete.***"
   rsync -cavP --no-perms  $DATA_LOCATION/*$FLIGHT* $TRANSFER_MEDIA/$PROJECT
   EXIT_RSYNC="$?"

   echo "rsync exit status: $EXIT_RSYNC"
   echo "****Starting file integrity checking. Please wait for process to complete.****"
   echo "Calculating sha256sum for original file(s)..."
   sha256sum $DATA_LOCATION/*$FLIGHT* >> $DATA_LOCATION/checksum
   echo "Calculating sha256sum for copied file(s)..."
   sha256sum $TRANSFER_MEDIA/$PROJECT/*$FLIGHT* >> $TRANSFER_MEDIA/$PROJECT/checksum
   echo "************************************************************"

   if [ $sha_copy == $sha_orig ]; then
      echo "SUCCESS! sha256sums match";
   else
      echo "ERROR! sha256sums do not match";
   fi

   echo "************************************************************"

   if [ "$EXIT_RSYNC" -eq 0 ] && [ $sha_copy == $sha_orig ]; then
      umount $TRANSFER_MEDIA;
      echo "Copy of .ads file(s) for $PROJECT$FLIGHT SUCCESSFUL."
      echo "When terminal closes you can safely remove the drive by right-clicking the desktop icon."
      sleep 80

   elif [ "$EXIT" -gt 0 ] || [ $sha_copy != $sha_orig ]; then
      echo "Copy of .ads file(s) for $PROJECT$FLIGHT UNSUCCESSFUL."
      echo "Check files under /var/r1/$PROJECT and try again."

   else
      echo "rsync error"
      sleep 80
   fi

else
   echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."
   sleep 8

fi

echo "script finished"

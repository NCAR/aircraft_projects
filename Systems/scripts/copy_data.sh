#!/bin/bash
###----------------------------------------------------------------------------
# script to copy .ads files from aircraft to transfer media for a given flight
# after connecting removable drive, run script to transfer file(s)
###----------------------------------------------------------------------------

# assign list of parameters for transferring data
PROJECT="WECAN"

DATA_LOCATION="/var/r1/$PROJECT/"
# DATA_LOCATION="/scr/tmp/taylort/copy_data_tests/WECAN"

TRANSFER_MEDIA="/run/media/ads/*/$PROJECT"
# TRANSFER_MEDIA="/scr/tmp/taylort/copy_data_tests/8845_TEST_MEDIA_8943"

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
echo "Please type Y and press enter to confirm. Anything else and enter will stop script."
read DRIVE_CONNECTION
if [ $DRIVE_CONNECTION == "Y" ]; then
   echo "You entered $DRIVE_CONNECTION, which means you have a drive connected.";
   rsync -av $DATA_LOCATION/*$FLIGHT* $TRANSFER_MEDIA
   EXIT="$?"
   echo "rsync exit status: $EXIT"
   if [ "$EXIT" -eq 0 ]; then
      #umount $TRANSFER_MEDIA;
      echo "Copy of .ads file(s) for $PROJECT$FLIGHT SUCCESSFUL."
      echo "OK to remove drive."
   elif [ "$EXIT" -gt 0 ]; then
      echo "Copy of .ads file(s) for $PROJECT$FLIGHT UNSUCCESSFUL."
      echo "Check files under /var/r1/$PROJECT and try again."
   else
      echo "rsync error"
   fi

else
   echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."
fi

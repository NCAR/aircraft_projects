#!/bin/bash
###----------------------------------------------------------------------------
# script to copy .ads files from aircraft to transfer media for a given flight
# after connecting removable drive, run script to transfer file(s)
###----------------------------------------------------------------------------
# assign list of parameters for transferring data
PROJECT="WECAN"

DATA_LOCATION="/var/r1/$PROJECT"

TRANSFER_MEDIA="/run/media/ads/*/$PROJECT"

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
   echo "You entered $DRIVE_CONNECTION, which means you have a drive connected.";
   rsync -cav $DATA_LOCATION/*$FLIGHT* $TRANSFER_MEDIA
   EXIT="$?"
   echo "rsync exit status: $EXIT"
   if [ "$EXIT" -eq 0 ]; then
      #umount $TRANSFER_MEDIA;
      echo "Copy of .ads file(s) for $PROJECT$FLIGHT SUCCESSFUL."
      echo "You can now safely remove the drive by right-clicking the desktop icon."
   elif [ "$EXIT" -gt 0 ]; then
      echo "Copy of .ads file(s) for $PROJECT$FLIGHT UNSUCCESSFUL."
      echo "Check files under /var/r1/$PROJECT and try again."
   else
      echo "rsync error"
   fi
else
   echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."
fi

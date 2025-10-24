#!/bin/bash
SECONDS=0  # Time this script
###----------------------------------------------------------------------------
# Script to copy .ads files from aircraft to transfer media for a given flight
# After connecting removable drive, run script to transfer file(s)
###----------------------------------------------------------------------------
# assign list of parameters for transferring data

# On planes and lab stations $PROJECT environment variable should be set by 
# the script ads3_environment.sh currently in /home/ads 

DATA_LOCATION="/var/r1/$PROJECT"
DAY=$(date +%4Y%m%d)
SATLOG=hpa_$DAY.log
cd /run/media/ads ## Change to the directory where the removable drive is mounted

echo "Enter flight to copy from $PROJECT e.g. rf01 or ff03:"
read FLIGHT
# Convert flight to lowercase
FLIGHT=$(echo "$FLIGHT" | tr '[:upper:]' '[:lower:]')

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
   echo "****************************************************************"
   echo "You entered $DRIVE_CONNECTION, which means you have a drive connected.";
   DRIVES=($(ls))  # Store the list of drives in an array
   TRANSFER_MEDIA="/run/media/ads"
   if [ ${#DRIVES[@]} -eq 1 ]; then
      DRIVE=${DRIVES[0]}
      TRANSFER_MEDIA="$TRANSFER_MEDIA/$DRIVE"
   elif [ ${#DRIVES[@]} -gt 1 ]; then
      echo "Multiple drives detected. Please select one by entering the corresponding number:"
      for i in "${!DRIVES[@]}"; do
         echo "$((i+1))) ${DRIVES[$i]}"
      done
      read -p "Enter number: " DRIVE_SELECTION
      DRIVE=${DRIVES[$((DRIVE_SELECTION-1))]}
      TRANSFER_MEDIA="$TRANSFER_MEDIA/$DRIVE"
   else
      echo "No drives detected. Exiting."
      exit 1
   fi

   echo "Using drive: $DRIVE"

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

      echo "***Starting file transfer. Please wait for transfer and integrity checking to complete.***"
      rsync -cavP --no-perms  $DATA_LOCATION/*$FLIGHT* $TRANSFER_MEDIA/$PROJECT
      rsync -cavP --no-perms  /var/log/satcom/$SATLOG  $TRANSFER_MEDIA/$PROJECT
      EXIT_RSYNC="$?"
      echo "***Sync cached data to permanent memory - can take 2-5 minutes.***"
      echo "sync started at $(date)"
      sync
      echo "rsync exit status: $EXIT_RSYNC"

      echo "****************************************************************"
      echo "Calculating sha256sum for original file(s)..."
      sha256sum $DATA_LOCATION/*$FLIGHT* >> $DATA_LOCATION/sha256sum.ads_station
      echo "************************************************************"
      echo "****************************************************************"
      echo "Calculating sha256sum for copied file(s)..."
      sha256sum $TRANSFER_MEDIA/$PROJECT/*$FLIGHT*
      echo "****************************************************************"

      if [[ "$EXIT_RSYNC" -eq 0 ]]; then
         echo "***Copy of .ads file(s) matching $PROJECT$FLIGHT SUCCESSFUL.***"
         echo "***You can safely remove the drive by right-clicking the desktop icon.***"
         echo "*** Note: This script does not eject the drive in case you still need to copy camera images.***"

      elif [[ "$EXIT" -gt 0 ]]; then
         echo "***Copy of .ads file(s) for $PROJECT$FLIGHT UNSUCCESSFUL."
         echo "***Check files under /var/r1/$PROJECT and try again."

      else
         echo "Rsync error"
      fi

   else
      echo "Cound not locate dir $TRANSFER_MEDIA/$PROJECT"
   fi

#   echo "********************* CAESAR-specific **************************"
#   echo "Sync GVR data to acserver"
#   rsync -a "gvr:/usr/local/prosensing/data/GVR_L?_2024-0[234]*" $DATA_LOCATION/GVR
#   if [ ! -d $TRANSFER_MEDIA/$PROJECT/GVR ]; then
#       mkdir -p $TRANSFER_MEDIA/$PROJECT/GVR
#   fi
#   rsync -cavP --no-perms $DATA_LOCATION/GVR/GVR*dat $TRANSFER_MEDIA/$PROJECT/GVR
#   echo "****************************************************************"

else
   echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."

fi

echo "****************************************************************"
echo "*** Note: This script does not eject the drive in case you still need to copy camera images.***"
echo "****************************************************************"

echo "Script took $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds"

read -p "Press enter key to exit script and close terminal"

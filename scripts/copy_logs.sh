#!/bin/bash
###----------------------------------------------------------------------------
# script to copy log files from aircraft to transfer media
###----------------------------------------------------------------------------

# On planes and lab stations $PROJECT environment variable should be set by 
# the script ads3_environment.sh currently in /home/ads 

TRANSFER_MEDIA="/run/media/ads/*/"

echo "***********************************************************************"
echo "Script must be run as root user, since log files are owned by root."
echo "/usr/bin/su root"
echo "***********************************************************************"

echo "Enter corresponding flight for logs from $PROJECT e.g. rf01 or ff03:"
read FLIGHT

echo "Do you have a removable drive connected?"
echo "Please type Y or y and press enter to confirm. Anything else and enter will stop script."
read DRIVE_CONNECTION
if [ $DRIVE_CONNECTION == "Y" ] || [ $DRIVE_CONNECTION == "y" ]; then
   cd $TRANSFER_MEDIA/$PROJECT/logs
   mkdir -p $FLIGHT
   EXIT_MKDIR="$?"

   if [ "$EXIT_MKDIR" -gt 0 ]; then
      echo "WARNING: command mkdir -p $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT failed!"
   else
      echo "command mkdir -p $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT was successful"
   fi

   echo "You entered $DRIVE_CONNECTION, which means you have a drive connected.";

   echo "Do you want to copy log files (you will need root privs)?"
   echo "Please type Y or y and press enter to confirm. Anything else and enter will not copy log files."
   read COPY_LOGS
   if [ $COPY_LOGS == "Y" ] || [ $COPY_LOGS == "y" ]; then
      rsync -va /var/log/messages $TRANSER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/ads3.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/ads3_kernel.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/router $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/nagios/nagios.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/boot.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/cron $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/dnf.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /var/log/kdump.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
      rsync -va /tmp/nimbus_*.log $TRANSFER_MEDIA/$PROJECT/logs/$FLIGHT
   else
      echo "Log files are not being copied."
   fi

else
   echo "You don't have a drive connected. Stopping script. Connect a removable drive and restart script."
   sleep 8

fi

echo "***********************************************************************"
echo "Log copying script finished"
echo "***********************************************************************"

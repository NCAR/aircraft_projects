#!/bin/bash 

SYM_LINK="/var/www/html/flight_data/images/latest_forward"
rm -vf $SYM_LINK

echo "Going into auto-check mode, checking every 1 second."

last=`ls -t $IMAGE_DIR | head -n 1`

for ((i = 0; ; i++)); do

  if [ -z $FLIGHT_NUM ] || [ $(($i % 300)) -eq 0 ];
  then
    echo "Checking for flight number change"
    FLIGHT_NUM=`psql -c "SELECT value from global_attributes where key='FlightNumber' " -h acserver.raf.ucar.edu -d real-time -U ads -t | tr -d " " | head -1`
    IMAGE_DIR="/mnt/r1/camera_images/flight_number_$FLIGHT_NUM/forward"
  fi

  curr=`ls -t $IMAGE_DIR | head -n 1`

  ln -sf "$IMAGE_DIR/$curr" "$SYM_LINK"

  if [ $(($i % 30)) -eq 0 ]; then

    if [ $curr = $last ]; then
      echo "Camera Image is not updating ..."
    fi

    last=`ls -t $IMAGE_DIR | head -n 2 | tail -1`
  fi

  sleep 1
done

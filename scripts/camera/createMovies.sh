#!/bin/bash

# Make sure at least one project and one flight are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project> <flight> (e.g rf06 rf07 rf08) ..."
    exit 1
fi

## Get aircraft
PROJECT=$(echo "$1" | tr '[:lower:]' '[:upper:]')
shift  # Remove the project argument so that $@ now contains only flights

AIRCRAFT=$(n_hdr_util ${RAW_DATA_DIR}/${PROJECT}/*.ads | grep 'system name:' | awk '{print $3}')


# Define array of image directions
DIRECTIONS=("forward" "left" "right" "down") 
CAMERA_DIRS=()

for DIR in "${DIRECTIONS[@]}"; do
    IMG_DIR="/scr/raf/Raw_Data/$PROJECT/CAMERA/flight_number_$FLIGHT/$DIR/"
    if [ ! -d "$IMG_DIR" ]; then
        echo "No camera images found for ${DIR} direction. Skipping."
        continue
    fi
    CAMERA_DIRS+=("$DIR")
done

cam_path=${PROJ_DIR}/scripts/camera
proj_path=${PROJ_DIR}/${PROJECT}/${AIRCRAFT}/scripts

for FLIGHT in "$@"; do
    echo "Processing flight: $FLIGHT"

    # Create movieParamFile from template, replacing <flight> with current flight
    sed "s/<flight>/$FLIGHT/g" ${cam_path}/movieParamFile.template > ${proj_path}/movieParamFile
    # Replace <PROJ> with the actual project name
    sed -i.bak "s/<PROJ>/$PROJECT/g" ${proj_path}/movieParamFile

    # Run the movie creation
    ${cam_path}/combineCameras.pl ${proj_path}/movieParamFile $FLIGHT

    echo "Completed flight: $FLIGHT"
done
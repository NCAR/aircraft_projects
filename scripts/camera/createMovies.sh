#!/bin/bash

# PROJECT, AIRCRAFT, and RAW_DATA_DIR are read from the environment
if [ -z "$PROJECT" ] || [ -z "$AIRCRAFT" ]; then
    echo "Error: PROJECT and AIRCRAFT must be set in the environment."
    exit 1
fi

if [ -z "$RAW_DATA_DIR" ]; then
    echo "Error: RAW_DATA_DIR must be set in the environment."
    exit 1
fi

# Make sure at least one flight is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <flight> (e.g rf06 rf07 rf08) ..."
    exit 1
fi

PROJECT=$(echo "$PROJECT" | tr '[:lower:]' '[:upper:]')


# Define array of image directions
DIRECTIONS=("forward" "left" "right" "down")

cam_path=${PROJ_DIR}/scripts/camera
proj_path=${PROJ_DIR}/${PROJECT}/${AIRCRAFT}/scripts

for FLIGHT in "$@"; do
    echo "Processing flight: $FLIGHT"

    CAMERA_DIRS=()
    for DIR in "${DIRECTIONS[@]}"; do
        IMG_DIR="${RAW_DATA_DIR}/$PROJECT/CAMERA/flight_number_$FLIGHT/$DIR/"
        if [ ! -d "$IMG_DIR" ]; then
            echo "No camera images found for ${DIR} direction. Skipping."
            continue
        fi
        CAMERA_DIRS+=("$DIR")
    done

    # Create movieParamFile from template, replacing <flight> with current flight
    sed "s/<flight>/$FLIGHT/g" ${cam_path}/movieParamFile.template > ${proj_path}/movieParamFile
    # Replace <PROJ> with the actual project name
    sed -i.bak "s/<PROJ>/$PROJECT/g" ${proj_path}/movieParamFile

    # Run the movie creation
    ${cam_path}/combineCameras.pl ${proj_path}/movieParamFile $FLIGHT

    echo "Completed flight: $FLIGHT"
done
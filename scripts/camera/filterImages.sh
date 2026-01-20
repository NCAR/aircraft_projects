#!/bin/bash

# Ensure at least one project and one flight are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project> <flight> (e.g. rf06 rf07 rf08) ..."
    exit 1
fi

# Convert project to uppercase
PROJECT=$(echo "$1" | tr '[:lower:]' '[:upper:]')
shift  # Now $@ holds only flight(s)

# Define array of image directions
DIRECTIONS=("forward" "left" "right" "down")

for FLIGHT in "$@"; do
    echo "Processing flight: $FLIGHT for project: $PROJECT"
    
    for DIR in "${DIRECTIONS[@]}"; do
        IMG_DIR="/scr/raf/Raw_Data/$PROJECT/CAMERA/flight_number_$FLIGHT/$DIR/"
        if [ ! -d "$IMG_DIR" ]; then
            echo "No camera images found for ${DIR} direction. Skipping."
            continue
        fi
        perl ./Image_Filter.pl "$IMG_DIR" "-s:60" "-t:5i" "-proj:$PROJECT"
    done

    echo "Completed flight: $FLIGHT"
done
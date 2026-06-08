#!/bin/bash

# PROJECT, AIRCRAFT, and RAW_DATA_DIR are read from the environment.
# PROJECT may be overridden on the command line with -p.
usage() {
    echo "Usage: $0 [-p PROJECT] <flight> (e.g rf06 rf07 rf08) ..."
}

while getopts ":p:h" opt; do
    case $opt in
        p) PROJECT="$OPTARG" ;;
        h) usage; exit 0 ;;
        \?) echo "Error: invalid option -$OPTARG"; usage; exit 1 ;;
        :)  echo "Error: option -$OPTARG requires an argument"; usage; exit 1 ;;
    esac
done
shift $((OPTIND - 1)) # Drop the parsed options so $@ still just holds the flight list

if [ -z "$PROJECT" ] || [ -z "$AIRCRAFT" ]; then
    echo "Error: PROJECT and AIRCRAFT must be set in the environment (or PROJECT via -p)."
    exit 1
fi

if [ -z "$RAW_DATA_DIR" ]; then
    echo "Error: RAW_DATA_DIR must be set in the environment."
    exit 1
fi

# Make sure at least one flight is provided
if [ $# -lt 1 ]; then
    usage
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

    # Per-flight parameter file so the setup can differ per flight movie.
    param_file="${proj_path}/movieParamFile_$FLIGHT"

    # Create the param file from template, unless one already exists (don't
    # overwrite a file the user may have customized).
    if [ -f "$param_file" ]; then
        echo "Using existing $param_file (not overwriting)."
    else
        # Replace <flight> with current flight
        sed "s/<flight>/$FLIGHT/g" ${cam_path}/movieParamFile.template > "$param_file"
        # Replace <PROJ> with the actual project name
        sed -i.bak "s/<PROJ>/$PROJECT/g" "$param_file"
    fi

    # Ask the user whether to run combineCameras.pl or exit.
    read -r -p "Run combineCameras.pl for flight $FLIGHT? [y/N] (or 'q' to quit) " answer
    case "$answer" in
        [Yy]*) ;;
        [Qq]*) echo "Exiting."; exit 0 ;;
        *) echo "Skipping flight: $FLIGHT"; continue ;;
    esac

    # Make sure the param file name ends with this flight designation.
    if [[ "$param_file" != *"$FLIGHT" ]]; then
        echo "Error: param file $param_file does not match flight $FLIGHT. Skipping."
        continue
    fi

    # Run the movie creation
    ${cam_path}/combineCameras.pl "$param_file" $FLIGHT

    echo "Completed flight: $FLIGHT"
done

#!/bin/bash

# PROJECT, AIRCRAFT, and RAW_DATA_DIR are read from the environment.
# PROJECT may be overridden on the command line with -p.
usage() {
    echo "Usage: $0 [-h] [-p PROJECT] <flight> (e.g rf06 rf07 rf08) ..."
}

while getopts ":p:h" opt; do
    case $opt in
        p) PROJECT="$OPTARG" ;;
	h) HIRES=True ;;
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

    # Resolve the camera directory name, which varies by project
    # (camera, CAMERA, or camera_images).
    CAMERA_DIR=""
    for name in camera CAMERA camera_images; do
        if [ -d "${RAW_DATA_DIR}/$PROJECT/${name}" ]; then
            CAMERA_DIR="$name"
            break
        fi
    done
    if [ -z "$CAMERA_DIR" ]; then
        echo "No camera directory (camera/CAMERA/camera_images) found under ${RAW_DATA_DIR}/$PROJECT. Skipping flight $FLIGHT."
        continue
    fi

    # Images come off the aircraft still packed as flight_number_<flight>.tar
    # The pointing direction subdirectories don't exist until that is unpacked,
    # so extract it before scanning for them. combineCameras.pl untars too.
    # This is for backward copatibility for the projects that call it directly
    # rather than through this script. Extraction is skipped when the flight
    # directory is already unpacked, so the tarfile is only ever extracted once.
    cam_dir_path="${RAW_DATA_DIR}/$PROJECT/${CAMERA_DIR}"
    flight_dir="${cam_dir_path}/flight_number_$FLIGHT"
    tarball="${flight_dir}.tar"
    if [ ! -d "$flight_dir" ]; then
        if [ -f "$tarball" ]; then
            echo "Extracting $tarball ..."
            if ! tar -xf "$tarball" -C "$cam_dir_path"; then
                echo "Error: couldn't extract $tarball."
            fi
        else
            echo "No tarfile $tarball found for flight $FLIGHT."
        fi
    fi

    # Record which directions have images. A direction that didn't fly, or a
    # camera that failed, just isn't in the list.
    CAMERA_DIRS=()
    if [ -d "$flight_dir" ]; then
        for DIR in "${DIRECTIONS[@]}"; do
            IMG_DIR="${flight_dir}/$DIR/"
            if [ ! -d "$IMG_DIR" ]; then
                echo "No camera images found for ${DIR} direction. Skipping."
                continue
            fi
            CAMERA_DIRS+=("$DIR")
        done
    fi

    # Nothing to work with, so there's no movie to make for this flight.
    if [ ${#CAMERA_DIRS[@]} -eq 0 ]; then
        echo "No camera images found for flight $FLIGHT. Skipping."
        continue
    fi

    # Select the param file template based on which camera directions we are
    # flying. Incomplete list - needs to be flushed out.
    template_file=""
    if [ ${#CAMERA_DIRS[@]} -eq 4 ]; then
        # All 4 cameras are available.
        template_file="${cam_path}/movieParamFile.template"
    elif [ ${#CAMERA_DIRS[@]} -eq 1 ] && [ "${CAMERA_DIRS[0]}" = "forward" ]; then
        # We only have a forward camera.
        template_file="${cam_path}/movieParamFile_fwd.template"
    fi

    # Per-flight parameter file so the setup can differ per flight movie.
    param_file="${proj_path}/movieParamFile_$FLIGHT"
    if [[ $HIRES == True ]]; then
        param_file="${param_file}hires"
    fi


    # Create the param file from template, unless one already exists (don't
    # overwrite a file the user may have customized).
    if [ -f "$param_file" ]; then
        echo "Using existing $param_file (not overwriting)."
    elif [ -z "$template_file" ]; then
        # An unhandled combination of pointing directions. Write the param
        # file by hand and rerun; the existing file will then be used as-is.
        echo "No template for cameras: ${CAMERA_DIRS[*]}."
        echo "Create $param_file by hand and rerun. Skipping flight $FLIGHT."
        continue
    elif [ ! -f "$template_file" ]; then
        echo "Template $template_file not found. Skipping flight $FLIGHT."
        continue
    else
        echo "Using template $template_file for cameras: ${CAMERA_DIRS[*]}"
        # Replace <flight> with current flight
        sed "s/<flight>/$FLIGHT/g" ${template_file} > "$param_file"
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

    # Make sure the param file name contains this flight designation.
    if [[ "$param_file" != *"$FLIGHT"* ]]; then
        echo "Error: param file $param_file does not match flight $FLIGHT. Skipping."
        continue
    fi

    # Run the movie creation
    ${cam_path}/combineCameras.pl "$param_file" $FLIGHT

    echo "Completed flight: $FLIGHT"
done

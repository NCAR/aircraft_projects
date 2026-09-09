#!/bin/bash
###############################################################################
# Perform camera image gap analysis on flight_number_#f## dirs. Calls
# analyze_frames.py in the proj dir. "tee" splits the output stream so this
# script writes to both standard out and the output file.
#
# This script assumes $PROJECT, $RAW_DATA_DIR, and $PROJ_DIR env vars are set
# Usage:
# - (with manual times):
#    /path/to/analyze_frames.py /path/to/images YYMMDD-HHMMSS YYMMDD-HHMMSS
#
# - (with flt_time piped input):
#    flt_time /path/to/flight.nc | /path/to/analyze_frames.py /path/to/images
#
# - The examples below wrap this in a for loop to loop through image dirs
#   and pipe the output to a file.
#
# THIS SCRIPT SHOULD BE COPIED TO THE PROJECT DIR and updated on a PER-PROJECT
# basis. Things that will need to be changed:
# - flight number range
# - rf, tf, ff
# - whether can use flt_time to determine times or whether the times need to
#   be passed in on the command line to exclude certain times
###############################################################################
# Sample using flt_time. Just update the second number in the for loop to add
# additional flights. This example will process rf01 and rf02
for num in {1..2}; do
  printf "\n====================== Flight rf%02d ======================\n" $num
  flt_time /home/data/${PROJECT}/${PROJECT}rf$(printf '%02d' $num).nc | \
      ${PROJ_DIR}/scripts/camera/analyze_frames.py \
      ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf$(printf '%02d' $num)/
done | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

# Sample setting the times on the command line - one block per flight. This is
# useful if there is a single flight with a refueling stop (flt_time will
# currently report the refuel landing as the end of the flight) or for other
# cases where flt_time doesn't return the desired time.
# When setting times manually, don't forget to adjust for sunrise/sunset and
# not include times when it is dark. This example is taken from INSPYRE rf06
printf "\n====================== Flight rf06 ======================\n" $num
${PROJ_DIR}/scripts/camera/analyze_frames.py \
    ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf06 \
    260808-185629 260809-021420 | \
    tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

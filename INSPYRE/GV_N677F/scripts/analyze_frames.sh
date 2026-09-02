#!/bin/bash
###############################################################################
# Perform camera image gap analysis on flight_number_#f## dirs. Calls 
# analyze_frames.py in the proj dir. "tee" splits the output stream so this
# script writes to both standard out and the output file.
#
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
for num in {1..5}; do
  printf "\n====================== Flight rf%02d ======================\n" $num
  flt_time /home/data/INSPYRE/INSPYRErf$(printf '%02d' $num).nc | \
      ${PROJ_DIR}/scripts/camera/analyze_frames.py \
      ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf$(printf '%02d' $num)/
done | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

# Flights RF06 and RF07 had refueling stops. flt_time doesn't handle that 
# correctly so explicitly pass desired times, including adjustment for sunset
printf "\n====================== Flight rf06 ======================\n" $num
${PROJ_DIR}/scripts/camera/analyze_frames.py \
    ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf06 260808-185629 \
    260809-021420 | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

printf "\n====================== Flight rf07 ======================\n" $num
${PROJ_DIR}/scripts/camera/analyze_frames.py \
    ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf07 260812-165851 \
    260813-020910 | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

# Continue on with files that don't have mid-flight landings
for num in {8..8}; do
  printf "\n====================== Flight rf%02d ======================\n" $num
  flt_time /home/data/INSPYRE/INSPYRErf$(printf '%02d' $num).nc | \
      ${PROJ_DIR}/scripts/camera/analyze_frames.py \
      ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf$(printf '%02d' $num)/
done | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

# RF09 data collection died mid-flight. flt_time returns an end date of
# 1970-01-01 so explicitly set times here
printf "\n====================== Flight rf09 ======================\n" $num
${PROJ_DIR}/scripts/camera/analyze_frames.py \
     ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf09 260820-215833 \
     260821-023620 | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

# Continue on with files that don't have mid-flight landings
for num in {10..13}; do
  printf "\n====================== Flight rf%02d ======================\n" $num
  flt_time /home/data/INSPYRE/INSPYRErf$(printf '%02d' $num).nc | \
      ${PROJ_DIR}/scripts/camera/analyze_frames.py \
      ${RAW_DATA_DIR}${PROJECT}/CAMERA/flight_number_rf$(printf '%02d' $num)/
done | tee ${RAW_DATA_DIR}${PROJECT}/CAMERA/frame_analysis_results.txt

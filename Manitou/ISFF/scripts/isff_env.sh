#!/bin/echo you must source
#
# Use the envset command which does the correct thing for both
# CSH and BASH
#
# These environment variables are used in the nidas XML
envset DATAMNT /scr/isfs
#
envset DATA_ARCHIVE '$DATAMNT/projects/$PROJECT/raw_data'
#
# subdirectory of cal_files for QC files, set to noQC or QC
envset QC_DIR QC
#
# subdirectory of cal_files for sonic QC files, set to boom_normal or slope_normal
envset SONIC_DIR flow_normal
#
# Output netcdf directory
envset NETCDF_DIR netcdf

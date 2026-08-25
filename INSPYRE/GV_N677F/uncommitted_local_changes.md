# Notes on Uncommitted Local Changes
This document contains notes on changes that are NOT checked in for the project. Reasons include needing different processing on different servers (onboard vs the groundstation, for example) or works in progress that are not to be checked in. The intent is to document these changes in case they need to be recreated due to accidental overwriting or other reasons for loss.

**Add additional sections as is helpful**

While the changes should NOT be checked in, this documentation file SHOULD be checked in as a way to track the changes.

## Local Changes - eol-groundstation3

### defaults files
Every defaults file on the ground station during INSPYRE should have the following uncommitted changes:

dsm304; DSC_A2DSensor
```
<!--
        Radiometer calibrations have been commented out just on the groundstation so that
        preliminary data in the netCDF files will be reported in volts. These changes should
        NOT be checked in because we want the cals active on the GV during flights. After
        the project concludes, the radiometer team will provide post-INSPYRE cals and the
        final data will be calibrated using those to W/m-2. See google doc:
        https://docs.google.com/document/d/1UhcwXDoiMAHU7XYKmumRBsP8cZooWdKipGSvt2lrhe8

        There are six calibrations: 4 ``poly` blocks and two `linear` blocks that are
        commented out:
-->
<!--
            <poly units="W m-2">
              <calfile file="VIST.dat" path="${TMP_PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F:${PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F"/>
            </poly>
-->
<!--
            <poly units="degC">
              <calfile file="IRTHT.dat" path="${TMP_PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F:${PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F"/>
            </poly>
-->
<!--
            <poly units="W m-2">
              <calfile file="VISB.dat" path="${TMP_PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F:${PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F"/>
            </poly>
-->
<!--
            <poly units="degC">
              <calfile file="IRBHT.dat" path="${TMP_PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F:${PROJ_DIR}/Configuration/cal_files/Engineering/GV_N677F"/>
            </poly>
-->
<!--
            <linear units="W m-2">
              <calfile file="VISTOT.dat" path="${TMP_PROJ_DIR}/Configuration/cal_files/Instruments/SPN1:${PROJ_DIR}/Configuration/cal_files/Instruments/SPN1"/>
            </linear>
-->
<!--
            <linear units="W m-2">
              <calfile file="VISDIF.dat" path="${TMP_PROJ_DIR}/Configuration/cal_files/Instruments/SPN1:${PROJ_DIR}/Configuration/cal_files/Instruments/SPN1"/>
            </linear>
-->
```

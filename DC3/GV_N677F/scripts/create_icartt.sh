#!/bin/csh

set nc2asc = "/opt/local/bin/nc2asc"

#/opt/local/bin/nc2asc -b RAF-CLOUDS -i DC3rf01.nc -o DC3-RAF-CLOUDS_GV_20120518_R1.ICT
#/opt/local/bin/nc2asc -b RAF-AEROSOL_template -i DC3rf01.nc -o DC3-RAF-AEROSOL_GV_20120518_R1.ICT
#/opt/local/bin/nc2asc -b RAF-NAV_template -i DC3rf01.nc -o DC3-RAF-NAV_GV_20120518_R1.ICT

foreach type (`cat $PROJ_DIR/DC3/GV_N677F/scripts/types`)
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf01FZ.nc -o DC3-RAF-${type}_GV_20120518_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf02FZ.nc -o DC3-RAF-${type}_GV_20120519_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf03FZ.nc -o DC3-RAF-${type}_GV_20120521_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf04FZ.nc -o DC3-RAF-${type}_GV_20120525_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf05FZ.nc -o DC3-RAF-${type}_GV_20120526_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf06FZ.nc -o DC3-RAF-${type}_GV_20120529_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf07FZ.nc -o DC3-RAF-${type}_GV_20120530_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf08FZ.nc -o DC3-RAF-${type}_GV_20120601_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf09FZ.nc -o DC3-RAF-${type}_GV_20120605_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf10FZ.nc -o DC3-RAF-${type}_GV_20120606_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf11FZ.nc -o DC3-RAF-${type}_GV_20120607_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf12FZ.nc -o DC3-RAF-${type}_GV_20120611_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf13FZ.nc -o DC3-RAF-${type}_GV_20120615_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf14FZ.nc -o DC3-RAF-${type}_GV_20120616_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf15FZ.nc -o DC3-RAF-${type}_GV_20120617_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf16FZ.nc -o DC3-RAF-${type}_GV_20120621_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf17FZ.nc -o DC3-RAF-${type}_GV_20120622_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf18FZ.nc -o DC3-RAF-${type}_GV_20120623_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf19FZ.nc -o DC3-RAF-${type}_GV_20120625_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf20FZ.nc -o DC3-RAF-${type}_GV_20120627_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf21FZ.nc -o DC3-RAF-${type}_GV_20120628_R3.ICT
${nc2asc} -b $PROJ_DIR/DC3/GV_N677F/scripts/RAF-${type}_template -i ../DC3rf22FZ.nc -o DC3-RAF-${type}_GV_20120630_R3.ICT
end

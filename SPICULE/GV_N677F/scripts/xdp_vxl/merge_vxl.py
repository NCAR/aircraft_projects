#!/usr/bin/env python3
###############################################################################
# Quick script to merge fill xdp_vxl, when missing, with dp_dpl, and write to
# dpxc
###############################################################################

import os
import glob
import string
import subprocess

datadir = "/scr/raf_data/SPICULE/xdp_vxl/"
class ncUtil():

    def dump_flight_start_date(self, file):
        ''' Retrieve start date of flight from netCDF file '''
        time_start = subprocess.check_output('ncdump '+file+
                 ' -h | grep time_coverage_start',shell=True)
        return(time_start.split(b"= \"")[1].split(b"T")[0].decode("utf-8"))

merge=ncUtil()
# Loop through netCDF files and extract vars to ascii
date = {}
for file in glob.glob(datadir+'*vxl.nc'):
    flight = file.split("xdp_vxl/SPICULE")[1].split("_xdp_vxl.nc")[0]
    os.system('n2asc -b '+flight+'.batch -n')
    date[flight] = merge.dump_flight_start_date(file)

# Create the new variable
for file in glob.glob(datadir+'*asc'):
    dp_dpx=[]
    dp_dpx_flag=[]
    xdp_vxl_array=[]
    seconds=[]
    print(file)
    f = open(file, 'r')
    # Read header line
    line = f.readline()
    if (line.rstrip() != "UTC      XDP_VXL  DP_DPL"):
        print("Not the right file")
    else:
        line = f.readline()
        while (line):
            (time,index,xdp_vxl,dp_dpl) = line.split()
            seconds.append(time)
            xdp_vxl_array.append(xdp_vxl)
            if (xdp_vxl == "-32767"):
                dp_dpx.append(dp_dpl)
                dp_dpx_flag.append('0')
            else:
                dp_dpx.append(xdp_vxl)
                dp_dpx_flag.append('1')
            line = f.readline()

        # Write data to ascii file
        f = open(file+'.dp_dpx','w')
        f.write("UTC     XDP_VXL    DPXC    DPXCflag\n")
        for i,value in enumerate(dp_dpx):
            f.write(seconds[i]+' '+xdp_vxl_array[i]+' '+value+' '+dp_dpx_flag[i]+"\n")
        f.close

# Loop through ascii files and write to netCDF
for file in glob.glob(datadir+'*asc.dp_dpx'):
    # write new netCDF
    flight = file.split("xdp_vxl/SPICULE")[1].split("_xdp_vxl.asc.dp_dpx")[0]
    os.system('asc2cdf -d '+date[flight]+' -: '+file+' '+file+'.nc')
    os.system('ncatted -a units,DPXC,o,c,deg_C '+file+'.nc')
    os.system('ncatted -a long_name,DPXC,o,c,"Merged experimental VCSEL Dew Point" '+file+'.nc')
    os.system('ncatted -a Dependencies,DPXC,c,c,"2 XDP_VXL DP_DPL" '+file+'.nc')
    os.system('ncatted -a units,DPXCflag,o,c,none '+file+'.nc')
    os.system('ncatted -a long_name,DPXCflag,o,c,"Merged experimental VCSEL Dew Point flag" '+file+'.nc')
    os.system('ncatted -a Dependencies,DPXCflag,c,c,"2 XDP_VXL DP_DPL" '+file+'.nc')
    os.system('ncatted -a units,XDP_VXL,o,c,deg_C '+file+'.nc')
    os.system('ncatted -a long_name,DP_VXL,o,c,"Experimental VCSEL Dew Point" '+file+'.nc')
    os.system('ncmerge -v XDP_VXL,DPXC,DPXCflag '+datadir+'SPICULE'+flight+'.nc '+file+'.nc')

# clean up
#os.system('rm '+datadir+'SPICULE*asc*')

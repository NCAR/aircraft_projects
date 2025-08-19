#! /usr/bin/env python3
##############################################################################
# Copyright (2023) University Corporation for Atmospheric Research 
# 
# Script to animate the flight track of the NSF/NCAR RAF airplane
# over a basemap
# ffmpeg can combine this animation with the digital camera movies
##############################################################################

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset

# flight_data and output data file
project = ''
flight = ''
flight_data = ''
save_file = project + '_' + flight + '_FlightTrack.mp4'

# provide the bounds for the basemap, these can be found with flt_area
# but it needs to be evaluated based on padding for the limits
min_lat = 10.0
max_lat = 25.0
min_lon = -88.0
max_lon = -62.0

# create figure object
fig = plt.figure()

# default settings for basemap
# mercator projection, high-resolution
bmap = Basemap(projection='merc', llcrnrlat=10. ,urcrnrlat=25.,llcrnrlon=-88, urcrnrlon=-62, resolution='h')

# blue marble gives terrain incl bathymetry
bmap.bluemarble()
bmap.drawcoastlines()

# generate the flight data based on the GGLON and GGLAT variables
# in a numpy array
# convert missing values np.nan to -32767
anim_file = Dataset(flight_data)
lon = np.asarray(anim_file['GGLON'])
lon = np.array(lon, dtype=float)
lat = np.asarray(anim_file['GGLAT'])
lat = np.array(lat, dtype=float)
lon = np.where(lon == -32767, np.nan, lon)
lat = np.where(lat == -32767, np.nan, lat)

# this is the number of data points
N = lon.size
x,y = bmap(lon, lat)
line, = bmap.plot(x[0], y[0], linewidth = 1, color = 'm')

# function defintion to iterate over the frames
def animFlightData(i):
    line.set_data(x[:i], y[:i])  
    return line

# write the animation and save to file
animObj = animFlightData.FuncAnimation(fig, animate, frames=N, interval=N)
animObj.save(save_file, fps=15, dpi=400)
print('Saving ' + save_file)

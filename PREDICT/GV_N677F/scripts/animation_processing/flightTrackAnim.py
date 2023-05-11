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
from matplotlib import animation
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset

# path to flight data that has been trimmed to start and end time
flight_data = ''
save_file = 'PREDICT_FlightTrack.mp4'

min_lat = #16.0
max_lat = #29.0
min_lon = #-76.0
max_lon = #-63.0

fig = plt.figure()

bmap = Basemap(projection='merc', llcrnrlat = min_lat ,urcrnrlat = max_lat,llcrnrlon = min_lon, urcrnrlon = max_lon, resolution = 'h')

bmap.bluemarble()
bmap.drawcoastlines()

anim_file = Dataset(flight_data)

lon = np.asarray(anim_file['GGLON'])
lon = np.array(lon, dtype=float)
lat = np.asarray(anim_file['GGLAT'])
lat = np.array(lat, dtype=float)
lon = np.where(lon == -32767, np.nan, lon)
lat = np.where(lat == -32767, np.nan, lat)

# latitude and longitude values from the dropsonde extract script
x,y = bmap(-72.128700,24.000300)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-73.428600,28.501300)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-71.916400,28.500300)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-75.266000,28.501600)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-69.043200,24.000700)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-70.606000,23.999800)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-75.499800,27.009100)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-75.501200,24.233900)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-73.855400,24.000100)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-68.670702, 25.592918)
plt.scatter(x, y, marker="X", color = "y")
x,y = bmap(-75.500000,25.459800)
plt.scatter(x, y, marker="X", color = "y")

N = lon.size
x,y = bmap(lon, lat)

line, = bmap.plot(x[0], y[0], linewidth = 1, color = 'm')

def animFlightData(i):
    line.set_data(x[:i], y[:i])  
    return line

animObj = animation.FuncAnimation(fig, animFlightData, frames=N, interval=N)
animObj.save(save_file, fps=15, dpi=400)

print('Saving ' + save_file)

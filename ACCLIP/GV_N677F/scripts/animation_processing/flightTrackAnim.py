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
save_file = 'ACCLIP_FlightTrack.mp4'

min_lat = 32.0
max_lat = 64.0
min_lon =
max_lon =

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

N = lon.size
x,y = bmap(lon, lat)

line, = bmap.plot(x[0], y[0], linewidth = 1, color = 'm', transfrom=ccrs.Geodetic()))

def animFlightData(i):
    line.set_data(x[:i], y[:i])  
    return line

animObj = animation.FuncAnimation(fig, animFlightData, frames=N, interval=N)
animObj.save(save_file, fps=15, dpi=400)

print('Saving ' + save_file)

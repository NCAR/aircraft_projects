#! /usr/bin/env python3 

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from netCDF4 import Dataset
import pandas as pd
flight_data = '/scr/raf_data/ACCLIP/2023_movies/data_trimmed/ACCLIPrf01_trimmed.nc'
anim_file = Dataset(flight_data)

palt = np.asarray(anim_file['GGALT'])
palt = np.array(palt, dtype=float)
palt = np.where(palt == -32767, np.nan, palt)
Dataframe = pd.DataFrame(palt)
df = Dataframe

def update(frame):
    plt.clf()  # Clear the previous frame
    plt.plot(df.index[:frame], df[0][:frame], color="m")
    plt.xlabel('Time [Seconds]')
    plt.ylabel('Altitude [Meters]')
    
    # turn off axis spines
    #ax.xaxis.set_visible(False)
    #ax.yaxis.set_visible(False)
    #ax.set_frame_on(False)

fig, ax = plt.subplots()
#fig.patch.set_alpha(0.)

ani = FuncAnimation(fig, update, frames=len(df), repeat=False)

ani.save('altitude_RF01.mp4', writer='ffmpeg')

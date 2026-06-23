#! /usr/bin/env python3

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

import os

# Provide project, flight
project = "TI3GER-2"
## flights must be a list even if only processing one flight
flights = ["ff01", "ff02", "pp01", "rf01", "rf02", "rf03", "rf04", "rf05", "rf06"]

# Check for required environment variables
if "DATA_DIR" not in os.environ:
    print("Error: DATA_DIR environment variable is not set.")
    exit(1)
if "RAW_DATA_DIR" not in os.environ:
    print("Error: RAW_DATA_DIR environment variable is not set.")
    exit(1)

# Build location of data file from env vars.
dat = os.path.join(os.environ["DATA_DIR"], project)

# Define where the existing digital camera movies are located
flight_movie_dir = os.path.join(os.environ["RAW_DATA_DIR"], project, "Movies/")

## Currently, the flight movie is found by the timeseries_animation.py script, but could be set here
##flight_movie = "rf01.240408.160031_201559.mp4"

# Define where you would like the output .mp4 to be written
output_dir = os.path.join(os.environ["RAW_DATA_DIR"], project, "Animations/")

# Uncomment and edit one of the following types of plots
# Example animation variable selection with two vars in one plot
#Var1 = "GGALT"
#Var2 = "PSX"
#Var3 = "WIC"
#Var4 = "PLWCC"
#Var5 = "CONCS_2DS"
#Var6 = "CONCD_LWI"
#Var7 = "FO3C_ACD"
#Var7a = "ATX"
#Var7b = "DPXC"
#VARLIST = [Var1,Var2,Var7a,Var7b,Var3,Var4,Var5,Var6,Var7,(Var1,Var7a, Var7b),('GGLON', 'GGLAT')]

# Example animation variable selection with two vars plotted against each other
Var1 = "GGALT"
Var2 = "DPXC"
Var3 = "PSX"
Var4 = "WIC"
Var5 = "ATX"
Var6 = "CONCD_RWO"
Var7 = "ATX"
VARLIST = [Var1,Var2,Var3,Var4,Var5,Var6,(Var1,Var7), ('GGLON', 'GGLAT')]

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
LineColor2 = "red"
PointColor = "red"
width="400:"


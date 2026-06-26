#! /usr/bin/env python3

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

import os

# Provide project, flight
project = "TI3GER-2"
## flights must be a list even if only processing one flight
flights = ["ff01", "ff02", "pp01", "rf01", "rf02", "rf03", "rf04", "rf05", "rf06"]

# Plots: values in parens () are plotted against each other on the same plot
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


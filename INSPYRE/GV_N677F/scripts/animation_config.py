#! /usr/bin/env python3

#######################################################################
# Configuration for timeseries_animation.py 
#######################################################################

import os

### Configuration is for project INSPYRE ###

# Provide flight: flights must be a list even if only processing one flight.
# During a deployment this can be left as "rfxx": push_data.py calls
# timeseries_animation.py --flight <flight>, and that argument supersedes this
# list. Only edit this list to process several flights in bulk (e.g.
# post-deployment), which is not the usual deployment case.
flights = ["rfxx"]

# Plots are generated one plot per value in varlist
# Variables within parenthesis are plotted on a single plots
# - Var1 without parens will plot Var1 vs time
# - (Var1, Var2) will plot Var1 on X-axis, Var2 on left Y-axis
# - (Var1, Var2, Var3) will plot Var1 on X-axis, Var2 on left Y-axis and
#    Var3 on right Y-axis
# 
# Add/edit as requested for the project
Var1 = "GGALT"
Var2 = "DPXC"
Var3 = "PSX"
Var4 = "WIC"
Var5 = "ATX"
Var6 = "CONCD_LWO"
VARLIST = [Var1,Var2,Var3,Var4,Var5,Var6,(Var1,Var5), ('GGLON', 'GGLAT')]

# Plot formatting options
dpi = 400 # Lower res will animate faster
fps = 15 # Script checks length against movie file, but this can be set faster or slower at onset
LineColor = "blue"
LineColor2 = "red"
PointColor = "red"
width="400:"


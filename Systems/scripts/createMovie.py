#!/usr/bin/python

import os

flight = raw_input('Input flight designation (e.g. tf01):')
print flight

command = "/home/local/raf/instruments/camera/createMovies/combineCameras.pl /home/local/projects/SOCRATES/GV_N677F/scripts/SOCRATES.paramfile " + flight

os.system(command)

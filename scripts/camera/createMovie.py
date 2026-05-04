#!/usr/bin/python

import os

flight = input('Input flight designation (e.g. tf01):')
print(flight)

command = "combineCameras.pl movieParamFile " + flight

os.system(command)

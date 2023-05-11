#! /usr/bin/env python3

#############################################################################
# python 3 script to extract the first latitude and longitude values
# from a NCAR/EOL/ISF dropsonde file. 
#
# Copyright University Corporation for Atmospheric Research (2023)
#
# Author: Taylor M. Thomas
#
############################################################################
input_file = ""

ds_in = open(input_file, "rt")
for i, line in enumerate(ds_in):
    if i == 14:
        line_string = line[:]
        line_array = line_string.split(" ")

        print("Latitude: " + line_array[15])
        print("Longitude: " + line_array[16])

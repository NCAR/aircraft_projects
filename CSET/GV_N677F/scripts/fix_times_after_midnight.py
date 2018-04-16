#!/usr/bin/python

import re

infile = open("/scr/raf/Prod_Data/CSET/HOLODEC/H2H/CSET-HOLODEC-H2H_GV_20150724.csv","r")
outfile = open("/scr/raf/Prod_Data/CSET/HOLODEC/H2H/CSET-HOLODEC-H2H_GV_20150724.csv.corr","w")

data = False
tomorrow = False
for line in infile.readlines():
    if (re.match("data",line)):
        data = True
        outfile.write(line)
	continue

    if data:
	if not (re.match("end data",line)):
            time,rest = line.split(",",1)
	    if (re.match(r"^0",time)):
	    	tomorrow = True;
	    if tomorrow:
	        line = str(float(time)+86400) + "," + rest

    outfile.write(line)

infile.close()
outfile.close()


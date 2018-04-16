#!/usr/bin/python

import sys
import re
import os.path
from optparse import OptionParser

class ASCII_average(object):
    def __init__(self,rate,input_file):
	self.rate = rate
	self.fileType = ""		# standard followed by file: BADC, ICARTT, etc
	self.input_file = input_file
	self.output_file = ""
	self.timestamp = ""
	self.short_name = {}		# hash relating param short name to reference
	self.unit = {}			# hash relating parameter units to reference
	self.ref = []			# Array relating reference to column number
	self.lines_to_average = [] 	# array of records to be parsed and averaged
					# together by column/parameter
	self.saveline = "none"		# Place to store first line of next time period
	

    def set_output_file(self):
        # Output file is input_file with new rate appended
        self.output_file = str(self.input_file) + "." + str(self.rate)

    def read_badc(self,infile,outfile):
        print "Processing file type " + self.fileType
	line = ""
	while True:
            line = infile.readline()
	    # write the header as-is to the output file
	    outfile.write(line)

	    if (re.match("data",line)):
	        # After "data" line, there is one more line to read/write -
	        # the column header line.
	        line = infile.readline()
	        outfile.write(line)

		# Create hash relating column headers to index. If the column headers 
		# are the index, then this is trivial, but column headers can be 
		# variable names (short_names).
	        columns = line.split(",")
		print "Found " + str(len(columns)) + " columns"
	        for i in range(0,len(columns)): 
		    self.ref.append(columns[i].rstrip())
		return

	    # gather column names and units
	    key,ref,value = line.split(",",2)

	    # BADC_CSV can either have references that are numbers, and a line with a 
	    # key of short_name that relates the variable name (short_name) to the 
	    # reference, or the references can be the variable names and there will 
	    # not be a short_name line. To tell the difference, see if the ref is a 
	    # number or not. Don't forget that ref can have a colon for a range of numbers.
	    if (ref.isdigit() or re.match(r'.*:.*',ref)): # We have a numerical ref 
	        if (re.match("short_name",key)):
	            if (re.match(r'.*:.*',ref)):
		        # Need to unfold range of columns
		        first,last = ref.split(":")
		        for i in range(int(first),int(last)+1):
	                    self.short_name[str(i)] = value.rstrip()
		    else:
	                self.short_name[ref] = value.rstrip()
	    else: # We have an alphanumeric reference. Assume it IS the short name.
		try:
		    self.short_name[ref]
		except:
		    self.short_name[ref] = ref

	    key,ref,value = line.split(",",2)
	    if (re.match("long_name",key)):
	        longname,units = value.split(",")
	        if (re.match(r'.*:.*',ref)):
		    # Need to unfold range of columns
		    first,last = ref.split(":")
		    for i in range(int(first),int(last)+1):
		        self.unit[str(i)] = units.rstrip()
		else:
		    self.unit[ref] = units.rstrip()


    def read_write_header(self,infile,outfile):
	# Read in metadata from ASCII file. Collect variable short names and 
	# units, so know correct averaging to apply (e.g sum counts and average
	# concentrations).

	# Read in each line of header
	line = infile.readline()
	outfile.write(line)

	# Confirm the first line corresponds to the filetype we requested
	match = re.match("Conventions,G,BADC-CSV,1",line)
	if (match):
	    # Found a BADC-CSV file
	    self.fileType = "BADC_CSV"
	else:
	    print "Only implemented for BADC-CSV file type"
	    sys.exit()
	
        
	if (re.match("BADC_CSV",self.fileType)):
	   # Now read/write everything else
	   self.read_badc(infile,outfile)

 
    def read_data(self,infile):
	# Read lines of data file until have rate's worth of data
	line = infile.readline()

	# Watch for format-specific end-of-data marker
	if (re.match("BADC_CSV",self.fileType)):
	    if (re.match("end data",line)):
		return(False)

	if (re.match(r"none",self.saveline)):
	    time,rest = line.split(",",1)
	else: # First line in file
	    time,rest = self.saveline.split(",",1)

	end_time = int(float(time)*self.rate)/self.rate+self.rate
	#print "Average data from " + time + " to " + str(end_time)
	self.timestamp = end_time - self.rate
	# print "Averaged data is timestamped with start of averaging period"

	while (float(time) < float(end_time)):
	    self.lines_to_average.append(line)
	    line = infile.readline()

	    # Watch for format-specific end-of-data marker
	    if (re.match("BADC_CSV",self.fileType)):
	        if (re.match("end data",line)):
	    	    return(False)
	
	    time,rest = line.split(",",1)
	
	self.saveline = line
	return(True)


    def average(self):
	# Average data based on units. Create averaged record
	output_rec = str(self.timestamp) + ','

	# sum all columns of data
	for i in range(1,len(self.ref)):
	    averages = 0.0
	    sig_count = 0
	    for line in self.lines_to_average:
	        columns = line.split(",")

		# Determine significant digits of the value read in
		if (re.search(r'\.',columns[i])):
		    integer_part,significant_digits = columns[i].split('.')
		    if (len(significant_digits) > sig_count):
			sig_count = len(significant_digits)
			#print "sig_count: " + str(sig_count)

		averages +=  float(columns[i])
		#print "Column " + self.ref[i] + ": " + columns[i]
	        #print "Units for column: " + self.unit[self.ref[i]]
	        #print "short_name for column: " + self.short_name[self.ref[i]]
		#print columns[i]
	    #print "---"
	    #print averages;
	    if (re.match(r"^#$",self.unit[self.ref[i]])):
	        # Sum unitless parameters, except flags
	        if (re.match(r".*flag.*",self.short_name[self.ref[i]])):
	 	    # Confirm all the flags are the same, else warn user
		    output_rec += str(averages/len(self.lines_to_average)) + ','
		else:
		    output_rec += str(int(averages)) + ','
	    elif (re.match("#/cm3",self.unit[self.ref[i]])):
	    	# Average concentrations
		#print float(len(self.lines_to_average));
		#print sig_count
		#print round(averages/float(len(self.lines_to_average)),sig_count) 
	        #print "\n\n";
		output_rec += str(round(averages/float(len(self.lines_to_average)),sig_count)) + ','
	    else:
		print "Units not recognized. Code must be updated."
		sys.exit()

	output_rec += '\n'
	#print output_rec
	self.lines_to_average[:] = []
	#print "SAVE: " + self.saveline
	self.lines_to_average.append(self.saveline)

	# print "New Record: " + output_rec
	return(output_rec)

    def write_data(self,outfile,output_rec):
	# Write averaged data to output file
	outfile.write(output_rec)

_usage = """%prog [options]"""

def main(args):
    parser = OptionParser(usage=_usage)
    parser.add_option("--rate", type="int", default=1, 
	    help="Enter output rate in seconds")
    parser.add_option("--input_file",type="string",default="",
	    help="Enter the file to be averaged")
    (options, args) = parser.parse_args(args)

    if not (os.path.isfile(options.input_file)):
        print "Please enter a valid filename using the --input_file option"
	sys.exit()


    averager = ASCII_average(options.rate,options.input_file)
    averager.set_output_file()
    print "Averaged data will be written to " + averager.output_file

    infile = open(averager.input_file,"r")
    outfile = open(averager.output_file,"w")

    averager.read_write_header(infile,outfile)
    state = True
    while state:
        state = averager.read_data(infile)
        output_rec = averager.average()
        averager.write_data(outfile,output_rec)


    # BADC format has the line "end data" after the last data line. Add it here
    if (re.match("BADC_CSV",averager.fileType)):
	averager.write_data(outfile,"end data")

    infile.close()
    outfile.close()
	

if __name__ == "__main__":
    main(sys.argv)

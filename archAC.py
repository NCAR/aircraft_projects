#!/usr/bin/env python
#
################################################################################
# Script to archive raw RAF datasets to the CISL Mass Storage System under the 
# /RAF or /ATD/DATA path.
#
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#  *  Copyright 2008                                                         *
#  *  University Corporation for Atmospheric Research, All Rights Reserved.  *
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
# Note: This script runs only in the project's "Production/archive" subdirectory
#       under the "dmg" login. It accesses dmg-user environment variables and 
#	extracts the project and platform from the path. The complete path MUST
#	follow the pattern /jnet/local/projects/<PROJ>/<PLATFORM>/Production/archive
#
# This script is an attempt to update and consolidate the arch* csh scripts 
# written by Ron Ruth and located in /scr/raf2/Prod_Data/archives/templates. 
# Impetus for it's development comes from the addition of the HAIS instruments
# to the data processing stream for HEFT08, ICE-L, PACDEX and subsequent projects.
#
# All Ron's old template scripts are save in SVN as old versions of this code, 
# and this code is in SVN and deployed to /net/work/bin/scripts/mass_store. Each
# project can archive it from there.
#
# Modified 9/4/2008 Janine Goldstein
#	to rename LRT and HRT files by getting flight, date, and time from netCDF
#	file and creating a filename of the form fltno.yyyymmdd.ShSmSs_EhEmEs.PNI.nc
# Modified 12/8/2009 Janine Aquino (Goldstein)
#	to include tarring camera images by hour and archiving to MSS.
# Modified 6/17/2010 Janine Aquino
#	to be more flexible in matching flight names. Realized I don't need
#	filenameFormat definition. Just match on date/time portion of
#	filename.
#	Updated to omit subdirs called "sent" from archive.
#	Updated to omit subdirs called "removed" from archive.
# Modified 7/9/2010 Janine Aquino
#	to be usable as a module in other scripts, specifically archive.py
#	Only used archive_files and rename functions in archive.py
#       I am sure there are hidden vars that will need to be made global to
#	use other functions
# Modified 9/21/2010 Janine Aquino (Happy Fall!)
#	to fix error in path to tarfile. Use getcwd, not sdir.
# Modified 2/15/2011 Sean Stroble
#	Update to use new /EOL directory structure
# Modified 4/13/2011 Sean Stroble
#       Switch to HPSS
# Modified 5/26/2011 Sean Stroble
#	Added renameKML which will add the timeinterval to the filename of KML 
#	files similar to LRT and HRT files. renameKML will also watch out for 
#	already renamed KML files to avoid adding the timeinterval twice.
# Modified 8/12/2011 Janine Aquino
#	to fix error in path to file when using -r (was duplicating root)
# Modified 8/18/2011 Janine Aquino
#	now removing root completely, so took previous fix back out (no duplicate
#	root)
# Modified 3/27/2014 Janine Aquino
#	remove use of proj.info since this script was the only one still using it, and
#       it only	pulled the calendar year. Just add that as part of the path on the 
#	command line.
#	add auto-removal of camera tarfiles once they are verified to be on HPSS 
#	since they are big and freq. fill up the disk.
#	Skip montage dirs.
################################################################################
# Import modules used by this code. Some are part of the python library. Others
# were written here and will exist in the same dir as this code.
import sys, getopt, re
import os
import string
import re
import time
import tarfile
import subprocess
import smtplib
#import email.MIMEText
from email.MIMEText import MIMEText
from datetime import datetime
from os.path import join
#from subprocess import subprocess.Popen
#from subprocess import subprocess.PIPE

user = "dmg"
rpwd = ""

# For bora logins, $PROJ_DIR is an environment variable set to the 
# project working dir (currently /jnet/local/projects).'''
# File that contains map between project and Mass Store directories where
# production data is archived.
dirmapfile = "/scr/raf/Prod_Data/archives/msfiles/directory_map"

class archRAFdata:

    def sendMail(self, subject, body, email):
	if email == "":
	    email = "janine@ucar.edu";
	msg = MIMEText(body)
	msg['subject'] = subject
	msg['from'] = email
	msg['to'] = email

	s = smtplib.SMTP("ndir.ucar.edu")
	s.sendmail(email, [email], msg.as_string())
	s.quit()

    def setMSSenv(self):
        # Set some constants here so can easily find and change them
        msrcpMachine = "bora"	# the machine to run the msrcp command from
        wpwd = "RAFDMG" 	# the MSS Write PWD
	return [msrcpMachine,wpwd]

    def today(self):
	today = time.strftime("%a, %d %b %Y %H:%M:%S local",time.localtime())
	return today

    def checkuser(self):
        '''
        Check login (only "dmg" login allowed to run this script)
        The old way was "user = os.getlogin()".
        python.org recommends using environ over getlogin.
        (getlogin is available on unix systems only.)'''

        logname= os.environ['LOGNAME']

        if user != logname:
            print "You are logged in as user "+ logname + \
	    ".\n Only the 'dmg' login is allowed to run this script.  Quitting.\n"
	    raise SystemExit

    def checkpath(self):
	'''
	Check current directory to make sure script is being run from the 
	archive subdir and grab the project name from the path as well. This 
	assumes the path is of the form 
	$PROJ_DIR/<PROJ_NAME>/<PLATFORM>/Production/archive'''

	# Get current working directory
	current_dir = os.getcwd()
	# split the path of the current dir into it's subdir components
	path_components = string.split(current_dir,'/')
	# Check the last section of the path. It should be a dir called "archive". 
	# If not,  warn user and exit.
	if path_components[len(path_components)-1] != "archive":
	    print "You are running from "+current_dir+"\n"
	    print 'This script must be run from '+ \
		  os.environ['PROJ_DIR'] + \
	          '/<proj>/<platform>/Production/archive. Quitting.\n'
	    raise SystemExit

	# Check the second to last part of the path. It should be a dir called
	# Production. If not, warn user and exit.
	if path_components[len(path_components)-2] != "Production":
	    print "You are running from "+current_dir+"\n"
	    print 'This script must be run from the '+ \
		  os.environ['PROJ_DIR'] + \
		  '/Production/archive subdir. Quitting.\n'
	    raise SystemExit

	# Determine the platform and project name from the path and return
	# them to the calling routine.
	platform = path_components[len(path_components)-3]
	proj_name = path_components[len(path_components)-4]

	# Create a string containing the path to the dir directly above "archive",
	# which is the Production dir.
	projdir = string.join(path_components[0:len(path_components)-1],'/')

	return [platform,proj_name,projdir,current_dir]

    def projnum (self,dirmapfile):
	'''
	PROJ = 3-digit project number - get from 
	$PROJ_DIR/archives/msfiles/directory_map by searching for the project name
	which we grabbed from the working dir path using checkpath()'''
	dirmap = open(dirmapfile,'r')
	lines = dirmap.readlines()
	dirmap.close()

	for line in lines:
	    match = re.search(proj_name,line)
	    if match:
		proj = string.split(line)[0]
		break
	return proj

    def findfiles(self,path,searchstr):
        '''
        Walk through a dir tree and return a list of all files matching
        searchstring'''
        # root - path to the directory
        # dirs - list of the names of the subdirs in dirpath (excluding . and ..)
        # files - list of the names of the non-directory files in dirpath
        # To get a full path to a file or dir in dirpath, os.path.join(dirpath,name)
	filesfound = []
	for root, dirs, files in os.walk(path):
	    for name in files:
	        match = re.search(searchstr+"$",name)
	        if match:
		    #if flag == "-r": 
		    #	root = string.split(root,'/')[-1]
		    name = os.path.join(root,name)
		    #print "Found "+name
		    filesfound.append(name)
	return filesfound

    def tardir(self,sdir,filedir,tarfilename,tarfiles):
	'''
	Create a tarfile called sibdir.tar containing all the files in the
	dirpath that match pattern. Also create a listing of the contents
	of the tarfile called subdiir.tar.dir. Return the location on disk
	of both the tarfile and the listing file.'''

	# Tar up files. If the path was to a file, or there were
	# no files found in the path, then there is nothing to 
	# tar so don't return anything.
	if len(tarfiles) != 0:
	    print "Creating tarfile for "+os.getcwd()+"/"+filedir

	    # Create the tarfile
	    tar = tarfile.open(tarfilename+".tar","w")
	    tarfiles.sort()
	    for files in tarfiles:
		archname = string.split(files,sdir+"/")
	        tar.add(files,archname[1])
	    tar.list()	# Echo file info to the screen for each file being 
	    		# added to the tarfile
	    tar.close()
	    # Now create tarfile listing to also be archived
	    os.system("tar -tvf "+tarfilename+".tar > "+
		    tarfilename+".tar.dir")
	    return [tarfilename+'.tar',tarfilename+'.tar.dir']
	else:
	    return ["",""]

    def renameKML(self,sdir,sfile):
        path = sdir + sfile

	#Some older KML files were renamed locally before this update
	#We dont want to add the timeinterval twice so watch for these files
	match = re.search('\d{8}.\d{6}.\d{6}', sfile)
	if match:
	    return sfile

	#Use grep to select the dates from the KML file
	p1 = subprocess.Popen(["grep","<when>",path], stdout=subprocess.PIPE)
	data = string.split(p1.communicate()[0], "\n")

	#Extract the begin date and time and fix the formatting
	match = re.search('(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)Z', data[0])
	timeinterval = string.replace(match.group(1),"-","") + "." + string.replace(match.group(2),":","")

	#Extract the end time and fix the formatting
	match = re.search('(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)Z', data[-2])
	timeinterval = timeinterval + "_" + string.replace(match.group(2),":","")

	#add the time interval infront of .kml
	return string.replace(sfile, ".kml", "." + timeinterval + ".kml")


    def rename(self,sdir,sfile):
	path = sdir + sfile
        dfile = ""

	# Get flight number
	# from the filename if we can otherwise from the NetCDF header	
	p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["grep","FlightNumber"], stdin=p1.stdout, stdout=subprocess.PIPE)
	flightnum = string.upper(string.split(p2.communicate()[0],'"')[1])
	
	match = re.search('(\w(F|f)\d\d\w\d?)',sfile)
	if match:
	    flightnum2 = match.group(0).upper()
	    if len(flightnum) >= 4:
		    if flightnum[0:3] == flightnum2[0:3]:
		        flightnum = flightnum2
		    else:
		        print "#WARNING: Ignored possible flight number in filename: " + flightnum2
	
	dfile = dfile+flightnum

	# Get flight date
	p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["grep","FlightDate"], stdin=p1.stdout, stdout=subprocess.PIPE)
	flightdate = string.upper(string.split(p2.communicate()[0],'"')[1])
	dates = string.split(flightdate,'/')
	dfile = dfile+'.'+dates[2]+dates[0]+dates[1]

	# Get Time Interval
	p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["grep","TimeInterval"], stdin=p1.stdout, stdout=subprocess.PIPE)
	timeinterval = string.upper(string.split(p2.communicate()[0],'"')[1])
	timeinterval = string.replace(timeinterval,'-','_')
	timeinterval = string.replace(timeinterval,':','')
	dfile = dfile+'.'+timeinterval+'.PNI.nc'

	#params = ["FlightNumber","FlightDate","TimeInterval"]
	#for param in params:
	    # Dump the header of the file
	#    p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
	#    p2 = subprocess.Popen(["grep",param], stdin=p1.stdout, stdout=subprocess.PIPE)
	#    dfile = dfile + string.upper(string.split(p2.communicate()[0],'"')[1]) + '.'
	#    print dfile

	return dfile

    def parse_date(self,name):
	(root, name) = os.path.split(name)
	match = re.search("[0-9][0-9][0-9][0-9][0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]",name)
	if match:
	    print "match found for date format. Parsing date."
	    name = match.group()
	    index = 0
	    year = "20"+name[index:index+2]
	    month = name[index+2:index+4]
	    day = name[index+4:index+6]
	    hour = name[index+7:index+9]
	    min = name[index+9:index+11]
	    sec = name[index+11:index+13]
	    #print year+"/"+month+"/"+day+" "+hour+":"+min+":"+sec
	    hoursearchstr = name[0:index+9] +'\d\d\d\d.'
	    print "Searching for files matching "+hoursearchstr
	else:
	    print "filename doesn't match \d\d\d\d\d\d.\d\d\d\d\d\d"
	    print "code can't parse date and will die"
	    
	return [year,month,day,hour,min,sec,hoursearchstr]

    def usage(self):
	'''
	Usage statement for this code. This is also the only documentation.
	'''
        if len(sys.argv) < 3 or len(sys.argv) > 7:
	    print '''Usage: archAC.py TYPE <flag> SDIR SFILES <ARCHIVEDIR> [EMAIL]
	    where:	type is data type being archive (SID-2H, ADS, CAMERA)
		(will be used a subdir name on mss)
		flag is an optional argument that can be -r or -t
			use -r to search for source files recursively
			use -t to create tarballs of subdirs in the SDIR
			use -p <pointing> to indicate camera
			use -a to recover and archive tarfiles in current
			    dir 
			use -m to archive movie files to the CAMERA dir on
			    mss.
			pointing for CAMERA files if
			pointing isn't given in path or
			filename. Possible values are FWD,
			DOWN, etc.
		SDIR = source file directory
		SFILES = source file suffix (i.e. ads)
		ARCHIVEDIR -> HPSS dir data will be archived to: EOL/<year>
		EMAIL = Who to send e-mail's too (Optional)'''
	    raise SystemExit
	return

    def archive_files(self,sdir,sfiles,flag,type,mssroot,email = ""):
	'''
        Now archive the data!
	'''
        print '#  '+str(len(sfiles))+' Job(s) submitted on '+ archraf.today()

        command = []
        for spath in sfiles:
            path_components = string.split(spath,'/')
            if flag == "-r": 
		# recursive searching, so path has subdir components
		sfile = path_components[len(path_components)-2]+'/'+\
		        path_components[len(path_components)-1]
	    else:
		# all files are in highest dir, no recursion
	        sfile = path_components[len(path_components)-1]


	    match = re.search("(LRT|lrt)",type)
	    if match:
	        sfile = archraf.rename(sdir,sfile)
	    match = re.search("(HRT|hrt)",type)
	    if match:
	        sfile = archraf.rename(sdir,sfile)
	    match = re.search("(KML|kml)",type)
	    if match:
	        sfile = archraf.renameKML(sdir,sfile)

            (msrcpMachine,wpwd)=archraf.setMSSenv()

            # http://www.mgleicher.us/GEL/hsi/hsi_reference_manual_2/hsi_commands/put_command.html
	    # -P : create intermediate HPSS subdirectories for the file(s) if they do not exist
	    # -d : remove local files after success transfer to HPSS
	    # Only remove camera tarfiles, since they are an intermediate product on local disk and are HUGE.
	    match = re.search('CAMERA',type)
	    if match:
		options = '-d '
	    else:
		options = ''

	    match = re.search(sdir,spath)
	    if match:
	    	command.append('/opt/local/bin/hsi put -P ' + options + spath + ' :' + mssroot + type + '/' + sfile) 
	    else: 
	    	command.append('/opt/local/bin/hsi put -P ' + options + sdir + spath + ' :' + mssroot + type + '/' + sfile) 

        for line in command:
	    print line
	
        process = raw_input("Run the commands as listed? " + \
		"yes == enter, no == anything else: ")
        if process == "":
            for line in command:
		p = subprocess.Popen(line,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
		output, errors = p.communicate();
		result = p.returncode
		#result = os.system(line)
                path_components = string.split(line,'/')
	        sfile = path_components[len(path_components)-1]
	        if result == 0:
	            print "#  hsi job for "+type+"/"+sfile+" -- OK -- "+ archraf.today()
	        else:
	            print "#  hsi job for "+type+"/"+sfile+" -- Failed -- "+ archraf.today()
	            print "#                "+type+"/"+sfile+": error code " + str(result)
		    archraf.sendMail("hsi job for "+type+"/"+sfile+" -- Failed -- " + archraf.today(), "\nSTDOUT:\n" + output + "\n\nSTDERR:\n" + errors, email)



        print "#   Successful completion on "+archraf.today()+"\n"

##########################
### MAIN
##########################
# Create an instance of the archRAFdata object
archraf = archRAFdata()

# Confirm this script  is being run as the dmg user.
#archraf.checkuser()

# Stuff below this line will only be run if the code is run directly.
# If it is used as a module for import into another script, it won't be run.
if __name__ == "__main__":
    
    # Usage: 
    archraf.usage()

    # Read the data type from the command line. It must always
    # be the second item on the line, after calling the script
    type = sys.argv[1]
    print "Processing type " + type
    
    # sys.argv[0] is the path and filename of this script
    # Don't currently need it for anything, so ignore it.

    # Get the rest of the command line arguments off the command line
    index = 2
    pointing = "unknown"
    arg = sys.argv[index]
    if re.search("^-",arg):
        # Assume there is only one flag on the line, else
        # bad things will happen
        flag = arg
        index = index+1
        if flag == "-p":
            arg = sys.argv[index]
            pointing = arg
            index = index+1
    else:
        flag = ""
    sdir = sys.argv[index]
    searchstr = sys.argv[index+1]
    location = sys.argv[index+2]
    match = re.search("EOL",location)
    if not match:
	print "\033[1;4;33mWarning: "+sys.argv[index+2]+" is depreciated!\033[0m\n"
    (dir,calendaryear) = string.split(location,'/')
    #Optional e-mail argument
    if len(sys.argv)-1 >= index+3:
         email = sys.argv[index+3]
    else:
         email = ""

    # Make sure this script is being run from 
    # $PROJ_DIR/<proj>/<platform>/Production/archive.
    (platform,proj_name,projdir,current_dir) = archraf.checkpath()
    
    # Confirm we are running on bora, merlot, or shiraz since these are the big data
    # processing machines and we don't want to step on anyone elses toes.
    # Not Implemented Yet
    
    # Get the list of files to archive and store to array sfiles
    # In Ron's original scripts, the file names were rearranged before writing to the 
    # Mass Store and the new destination filenames were stored in dfiles.
    # Going forward, keep the same filenames, except for LRT and HRT netCDF files,
    # which are renamed using the rename subroutine.
    sfiles = []
    if (type == "CAMERA") & (flag != "-a") & (flag != "-m"):
        aircraft = platform
        print "This project took place aboard the "+aircraft+" aircraft\n"
    
        # List all the files/dirs in the working dir (sdir)
        for root, dirs, files in os.walk(sdir):
            files.sort()
            tarfiles = []
            hoursearchstr = "999999"
            for name in files:
                match = re.search(hoursearchstr,name)
                if not match:
                    print "Found file "+name
                    match = re.search(searchstr,name)
                    if match: 
                        (byr,bmo,bdy,bhr,bmn,bsc,hoursearchstr)=archraf.parse_date(name)
    
    	                fullname = os.path.join(root,name)
    		        print fullname
    		        # Skip sent dirs (don't archive them)
    	                match = re.search("sent",fullname)
    	                if match:
    	                  continue;
    		        # Skip montage dirs (don't archive them)
    	                match = re.search("montage",fullname)
    	                if match:
    	                  continue;
    		        # Skip removed dirs (don't archive them)
    	                match = re.search("removed",fullname)
    	                if match:
    	                  continue;
    
    		        # Get camera location (fwd, etc) from path
    		        # or make user enter on command line.
    		        if re.search('left',fullname):
    			    pointing = 'LEFT'
    		        if re.search('right',fullname):
    			    pointing = 'RIGHT'
    		        if re.search('down',fullname):
    			    pointing = 'DOWN'
    		        if re.search('forward',fullname):
    			    pointing = 'FWD'
    		        if re.search('FWD',fullname):
    		            pointing == 'FWD'
    		        if pointing == "unknown":
    		            print "ERROR: pointing not given in path "+ \
    		            "or filename. Enter using -p on command "+ \
    		            "line."
    	                    raise SystemExit
    
                        # Return an array containing the complete path to
                        # all the files matching searchstr in the path
                        hoursearchstr = hoursearchstr+searchstr
                        print "Finding files in "+root+" that match "+hoursearchstr
                        tarfiles = archraf.findfiles(root,hoursearchstr)
    
                        tarfiles.sort()
                        Efile = tarfiles[len(tarfiles)-1]
                        (eyr,emo,edy,ehr,emn,esc,hoursearchstr)=archraf.parse_date(Efile)
                        # output tarfile name is like 
                        # RF##.FWD.Sdate.Stime_etime.jpg.tar and tar.dir
                        match = re.search("[RrTtFf][Ff][0-9][0-9]",fullname)
                        if not match:
                            print "Flight number not found in image path. Please"
                            print " rename camera dirs to contain flight numbers"
                            print " e.g. RF01\n"
                            raise SystemExit
   
                        flightnum = string.upper(match.group())
                        tarfilename=flightnum+"."+pointing+"."+\
                            byr+bmo+bdy+"."+bhr+bmn+bsc+"_"+\
                            ehr+emn+esc+"."+searchstr
    
                        # Create the tarball
                        [tfile,tfilelist]=archraf.tardir(root,"",tarfilename,tarfiles)
    
                        if tfile != "":
                        # Add the tar file to the array of files to archive
                            sfiles.append(tfile)
                            # Add the tar file list to the array of files to archive
                            sfiles.append(tfilelist)
            sdir = os.getcwd() + '/'
    elif flag == "-r":
        sfiles = archraf.findfiles(sdir,searchstr)
        sdir = sdir + '/'
    elif flag == "-t":
        # List all the files/dirs in the working dir (sdir)
        dirfilelist = os.listdir(sdir)
        dirfilelist.sort()
        for file in dirfilelist:
            # Walk through the dirpath (this will ignore paths that 
            # point to a file and
            # only walk through paths that point to a dir.
            path = join(sdir,file)
    
            # Return an array containing the complete path to all 
            # the files matching searchstr in the path
            print "Finding files in "+path+" that match "+searchstr
            tarfiles = archraf.findfiles(path,searchstr)
    
            # For clarity, the tarfile name should contain the 
            # date (yyyymmdd) and flight number. Start with the 
            # directory name.
            tarfilename = file
    
            # If the directory name does not contain a year, 
            # add it to the tarfile name.
            match = re.search(calendaryear,tarfilename)
            if not match:
                tarfilename = file + "_" + calendaryear
            [tfile,tfilelist]=archraf.tardir(sdir,file,tarfilename,tarfiles)
            if tfile != "":
                # Add the tar file to the array of files to archive
                sfiles.append(tfile)
                # Add the tar file list to the array of files to archive
                sfiles.append(tfilelist)
        sdir = current_dir+"/"
    else:
        #if (flag == "-m"):
        #            sdir = os.getcwd()
    
        # if flag == "-a" do regular processing
        lines = os.listdir(sdir)
        for line in lines:
            match = re.search(searchstr,line)
            if match:
                sfiles.append(line)
        sdir = sdir + '/'
    
    # Sort the files to be processed so they are processed in alphabetical order
    sfiles.sort()
    
    mssroot = ' /'+location+'/'+proj_name.lower()+'/aircraft/'+platform.lower()+'/'
    #Now archive the data!
    archraf.archive_files(sdir,sfiles,flag,type,mssroot,email)
    

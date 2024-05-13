#!/usr/bin/python
#
################################################################################
# Script to archive raw RAF datasets to the CISL Mass Storage System under the 
# /RAF or /ATD/DATA path.
#
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#  *  Copyright 2008                                                         *
#  *  University Corporation for Atmospheric Research, All Rights Reserved.  *
#  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# Import modules used by this code. Some are part of the python library. Others
# were written here and will exist in the same dir as this code.
import sys, re
import os, getpass
import re
import time
import tarfile
import glob
import subprocess
import smtplib
from email.mime.text import MIMEText
from os.path import join
user = "dmg"
rpwd = ""

getuser = getpass.getuser()
print(f"User is [{getuser}]")

if getuser != "eoldata":
    print(f"You are running script as: {getuser}. Change to eoldata and start over.")
    sys.exit()

# For bora logins, $PROJ_DIR is an environment variable set to the 
# project working dir (currently /jnet/local/projects).'''
# File that contains map between project and Mass Store directories where
# production data is archived.
dirmapfile = "/scr/raf/Prod_Data/archives/msfiles/directory_map"
hash_value_file = "/scr/raf/Prod_Data/"+os.environ["PROJECT"]+\
                "/"+os.environ["PROJECT"]+"_archive_hash_file.txt"

calendaryear = os.environ["YEAR"]
print(calendaryear)
scr_dir = '/scr/raf/eoldata'  ##Scratch directory to write and store tarballs before transferring them to the archive
class archRAFdata:
    """
    A collection of methods for archiving RAF data and performing related tasks.

    Methods:
        sendMail(subject, body, email): Sends an email with the specified subject and body to the given email address.
        setMSSenv(): Sets constants for MSS environment.
        today(): Returns the current date and time in a formatted string.
        checkuser(): Checks login to ensure only "dmg" login is allowed to run the script.
        checkpath(): Checks the current directory to ensure the script is being run from the correct location.
        projnum(dirmapfile): Retrieves the project number from a directory map file.
        findfiles(path, searchstr): Walks through a directory tree and returns a list of files matching a search string.
        tardir(sdir, filedir, tarfilename, tarfiles): Creates a tarfile containing files matching a pattern.
        renameKML(sdir, sfile): Renames a KML file by adding a time interval to the filename.
        rename(sdir, sfile): Renames a file based on flight number, date, and time interval.
        parse_date(name): Parses the date from a filename.
        usage(): Displays the usage statement for the script.
        archive_files_cs(sdir, sfiles, flag, type, csroot, email=""): Archives data based on specified parameters.
    """

    def sendMail(self, subject, body, email):
        """
        Sends an email with the specified subject and body to the given email address.

        Args:
            subject (str): The subject of the email.
            body (str): The body content of the email.
            email (str): The recipient email address.

        Returns:
            None

        Raises:
            None
        """
        msg = MIMEText(body)
        msg['subject'] = subject
        msg['from'] = email
        msg['to'] = email

        s = smtplib.SMTP("ndir.ucar.edu")
        s.send_message(msg)  # Use send_message for MIME objects
        s.quit()

    def setMSSenv(self):
        # Set some constants here so can easily find and change them
        msrcpMachine = "bora"	# the machine to run the msrcp command from
        wpwd = "RAFDMG" 	# the MSS Write PWD
        return [msrcpMachine,wpwd]

    def today(self):
        """
        Returns the current date and time in a formatted string.
        """
        return time.strftime("%a, %d %b %Y %H:%M:%S local",time.localtime())

    def create_path(self,path):
        """
        This function checks if a path exists and creates it if not
        Args:
            path (str): The path to check and create.

        Returns:
            None
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def checkuser(self):
        '''
        Check login (only "dmg" login allowed to run this script)
        The old way was "user = os.getlogin()".
        python.org recommends using environ over getlogin.
        (getlogin is available on unix systems only.)'''

        logname= os.environ['LOGNAME']

        if user != logname:
            print(f"You are logged in as user {logname}.\n Only the 'dmg' login is allowed to run this script.  Quitting.\n")
            raise SystemExit

    def checkpath(self):
        '''Check current directory to make sure script is being run from the 
        archive subdir and grab the project name from the path as well. This 
        assumes the path is of the form 
        $PROJ_DIR/<PROJ_NAME>/<PLATFORM>/Production/archive'''

        # Get current working directory
        current_dir = os.getcwd()
        # split the path of the current dir into it's subdir components
        path_components = current_dir.split('/')
        # Check the last section of the path. It should be a dir called "archive". 
        # If not,  warn user and exit.
        if path_components[-1] != "archive":
            print(f"You are running from {current_dir}" + "\n")
            print('This script must be run from '+ \
                    os.environ['PROJ_DIR'] + \
                        '/<proj>/<platform>/Production/archive. Quitting.\n')
            raise SystemExit

	# Check the second to last part of the path. It should be a dir called
	# Production. If not, warn user and exit.
        if path_components[len(path_components)-2] != "Production":
            print(f"You are running from {current_dir}\n")
            print('This script must be run from the '+os.environ['PROJ_DIR'] +'/Production/archive subdir. Quitting.\n')
            raise SystemExit

        # Determine the platform and project name from the path and return
        # them to the calling routine.
        platform = path_components[len(path_components)-3]
        proj_name = path_components[len(path_components)-4]

        # Create a string containing the path to the dir directly above "archive",
        # which is the Production dir.
        projdir = '/'.join(path_components[:-1])

        return [platform,proj_name,projdir,current_dir]

    def projnum(self,dirmapfile):
        '''PROJ = 3-digit project number - get from $PROJ_DIR/archives/msfiles/directory_map by searching for the project name
        which we grabbed from the working dir path using checkpath()
        '''
        with open(dirmapfile,'r') as dirmap:
            lines = dirmap.readlines()
        for line in lines:
            match= re.search(proj_name, line)
            if match:
                proj = line.split()[0]
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
                fullname = os.path.join(root,name)
                match= re.search("removed",fullname)
                if match:
                    continue;
                match = re.search(f"{searchstr}$", name)
            if match:
                name = os.path.join(root,name)
                filesfound.append(name)
        return filesfound

    def tardir(self,sdir,filedir,tarfilename,tarfiles):
        '''
        Create a tarfile called subdir.tar containing all the files in the
        dirpath that match pattern. Also create a listing of the contents
        of the tarfile called subdir.tar.dir. Return the location on disk
        of both the tarfile and the listing file.'''
        # Tar up files. If the path was to a file, or there were
        # no files found in the path, then there is nothing to 
        # tar so don't return anything.
        if len(tarfiles) == 0:
            return ["",""]
        event = os.path.basename(tarfilename)
        match = re.search(calendaryear,event)
        if not match:
            tfilename = event.upper() + "_" + calendaryear
        else:
            tfilename = event.upper()
        print(f"Creating tarfile for {sdir}/{filedir}")
        print(f"Writing tarball to {scr_dir}/{tfilename}")
        os.system(f"tar -cvf {scr_dir}/{tfilename}.tar --directory={sdir} {event}")
        os.system(f"tar -tvf {scr_dir}/{tfilename}.tar > {scr_dir}/{tfilename}.tar.dir")
        return [f'{tfilename}.tar', f'{tfilename}.tar.dir']

    def renameKML(self,sdir,sfile):
        """
        Renames a KML file by adding a time interval to the filename.

        Args:
            sdir (str): The directory path of the KML file.
            sfile (str): The name of the KML file.

        Returns:
            str: The new filename with the added time interval.

        Raises:
            None
        """
        path = sdir + sfile

        #Some older KML files were renamed locally before this update
        #We dont want to add the timeinterval twice so watch for these files
        match= re.search('\d{8}.\d{6}.\d{6}', sfile)
        if match:    
            return sfile

        #Use grep to select the dates from the KML file
        p1 = subprocess.Popen(["grep","<when>",path], stdout=subprocess.PIPE)
        data = p1.communicate()[0].decode('utf-8').split("\n")

        #Extract the begin date and time and fix the formatting
        match = re.search('(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)Z', data[0])
        timeinterval = match[1].replace("-", "") + "." + match[2].replace(":", "")

        #Extract the end time and fix the formatting
        match = re.search('(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)Z', data[-2])
        timeinterval = timeinterval+"_" + match[2].replace(":", "")

        #add the time interval infront of .kml
        return sfile.replace(".kml", f".{timeinterval}.kml")


    def rename(self,sdir,sfile):
        """
        Renames a file based on flight number, date, and time interval.

        Args:
            sdir (str): The directory path of the file.
            sfile (str): The name of the file to be renamed.

        Returns:
            str: The new filename with the added flight number, date, and time interval.
        """
        path = sdir + sfile
        dfile = ""

        # Get flight number
        # from the filename if we can otherwise from the NetCDF header	
        p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep","FlightNumber"], stdin=p1.stdout, stdout=subprocess.PIPE)
        flightnum = (p2.communicate()[0].decode('utf-8').split('"')[1]).upper()
        match= re.search('(\w(F|f)\d\d\w\w?\w?\d?\d?)', sfile)
        if match:
            flightnum2 = match[0].upper()
            if len(flightnum) >= 4:
                if flightnum[:3] == flightnum2[:3]:
                    flightnum = flightnum2
                else:
                    print(f"#WARNING: Ignored possible flight number in filename: {flightnum2}")

        dfile += flightnum

        # Get flight date
        p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep","FlightDate"], stdin=p1.stdout, stdout=subprocess.PIPE)
        flightdate = (p2.communicate()[0].decode('utf-8').split('"')[1]).upper()
        dates = flightdate.split('/')
        dfile = f'{dfile}.{dates[2]}{dates[0]}{dates[1]}'

        # Get Time Interval
        p1 = subprocess.Popen(["/usr/bin/ncdump","-h",path], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep","TimeInterval"], stdin=p1.stdout, stdout=subprocess.PIPE)
        timeinterval = (p2.communicate()[0].decode('utf-8').split('"')[1]).upper()
        timeinterval = timeinterval.replace('-','_')
        timeinterval = timeinterval.replace(':','')
        return f'{dfile}.{timeinterval}.PNI.nc'

    def parse_date(self,name):
        """
        Parses the date components from a filename in a specific format.

        Args:
            name (str): The filename to extract the date components from.

        Returns:
            list: A list containing the year, month, day, hour, minute, second, and search string.
        """
        (root, name) = os.path.split(name)
        match= re.search(
            "[0-9][0-9][0-9][0-9][0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]", name
        )
        if match:
            print("match found for date format. Parsing date.")
            name = match.group()
            index = 0
            year = f"20{name[index:index + 2]}"
            month = name[index+2:index+4]
            day = name[index+4:index+6]
            hour = name[index+7:index+9]
            minute = name[index+9:index+11]
            sec = name[index+11:index+13]
            #print year+"/"+month+"/"+day+" "+hour+":"+min+":"+sec
            hoursearchstr = name[:index+9] + '\d\d\d\d.'
            print(f"Searching for files matching {hoursearchstr}")
        else:
            print("filename doesn't match \d\d\d\d\d\d.\d\d\d\d\d\d")
            print("code can't parse date and will die")

        return [year,month,day,hour,minute,sec,hoursearchstr]

    def usage(self):
        '''
        Usage statement for this code. This is also the only documentation.
        '''
        if len(sys.argv) < 3 or len(sys.argv) > 7:
            print('''Usage: archAC.py TYPE <flag> SDIR SFILES <ARCHIVEDIR> [EMAIL]
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
            EMAIL = Who to send e-mail's too (Optional)''')
            raise SystemExit
        return

    def archive_files_cs(self,sdir,sfiles,flag,type,csroot,email = ""):
        '''Now archive the data!'''
        print(f'#  {len(sfiles)} Job(s) submitted on {archraf.today()}')
        options = ''
        command = []
        for spath in sfiles:
            path_components = spath.split('/')
            sfile = (
                f'{path_components[len(path_components) - 2]}/{path_components[len(path_components) - 1]}'
                if flag == "-r"
                else path_components[len(path_components) - 1]
            )
            match = re.search("(LRT|lrt)", type)
            if match:
                sfile = archraf.rename(sdir,sfile)
            match= re.search("(HRT|hrt)", type)
            if match:
                sfile = archraf.rename(sdir,sfile)
            match = re.search("(SRT|srt)", type)
            if match:
                sfile = archraf.rename(sdir,sfile)
            match= re.search("(KML|kml)", type)
            if match:
                sfile = archraf.renameKML(sdir,sfile)

            (msrcpMachine,wpwd)=archraf.setMSSenv()

            # http://www.mgleicher.us/GEL/hsi/hsi_reference_manual_2/hsi_commands/put_command.html
            # -P : create intermediate HPSS subdirectories for the file(s) if they do not exist
            # -d : remove local files after success transfer to HPSS
            # Only remove camera tarfiles, since they are an intermediate product on local disk and are HUGE.
            match = re.search('CAMERA',type)
            match= re.search(sdir, spath)
            if match:
                command.append(
                        f'rsync {spath} eoldata@data-access.ucar.edu:{csroot}{type}/{sfile}'
                )
            else:
                if 'LRT' in type:
                    command.append(
                        f'rsync {sdir}{spath} {csroot}{type}/{sfile}')
                else:
                    command.append(
                        f'rsync {sdir}{spath} eoldata@data-access.ucar.edu:{csroot}'
                        + type
                        + '/'
                        + sfile
                    )

        for line in command:
            print(line)

        process = input("Run the commands as listed? " + \
                                "yes == enter, no == anything else: ")

        match= re.search('CAMERA', type)
        if match:
            process = ""

        if process == "":
            for line in command:
                p = subprocess.Popen(line,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                output, errors = p.communicate();
                result = p.returncode
                #result = os.system(line)
                path_components = line.split('/')
                sfile = path_components[len(path_components)-1]
                if result == 0:
                    print(f"#  rsync job for {type}/{sfile} -- OK -- {archraf.today()}")
                else:
                    print(f"#  rsync job for {type}/{sfile} -- Failed -- {archraf.today()}")
                    print(f"#                {type}/{sfile}: error code {str(result)}")
                    subj = f"rsync job for {type}/{sfile} -- Failed -- {archraf.today()}"
                    message = f"\nSTDOUT:\n{output.decode('utf-8')}\n\nSTDERR:\n{errors.decode('utf-8')}"
                    archraf.sendMail(subj,message, email)
        print(f"#   Successful completion on {archraf.today()}" + "\n")


##########################
### MAIN
##########################
# Create an instance of the archRAFdata object
archraf = archRAFdata()


# Stuff below this line will only be run if the code is run directly.
# If it is used as a module for import into another script, it won't be run.
if __name__ == "__main__":
    
    # Usage: 
    archraf.usage()

    # Read the data type from the command line. It must always
    # be the second item on the line, after calling the script
    type = sys.argv[1]
    print("Processing type " + type)
    
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
    cs_location = sys.argv[index+2]
    match = re.search("EOL",cs_location)

    #Optional e-mail argument
    if len(sys.argv)-1 >= index+3:
        email = sys.argv[index+3]
    else:
        print("You must supply an email address as the last argument. If the script fails, you will receive an email.")

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
        print("This project took place aboard the "+aircraft+" aircraft\n")
    
        # List all the files/dirs in the working dir (sdir)
        for root, dirs, files in os.walk(sdir):
            files.sort()
            tarfiles = []
            hoursearchstr = "999999"
            for name in files:
                match = re.search(hoursearchstr,name)
                if not match:
                    print("Found file "+name)
                    match = re.search(searchstr,name)
                    if match: 
                        (byr,bmo,bdy,bhr,bmn,bsc,hoursearchstr)=archraf.parse_date(name)
                        fullname = os.path.join(root,name)
                        print(fullname)
                        # Skip sent dirs (don't archive them) 
                        match = re.search("sent",fullname)
                        if match:
                            continue
                        # Skip montage dirs (don't archive them)
                        match = re.search("montage",fullname)
                        if match:
                            continue
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
                        print("ERROR: pointing not given in path "+ \
    		            "or filename. Enter using -p on command "+ \
    		            "line.")
                        raise SystemExit
    
                        # Return an array containing the complete path to
                        # all the files matching searchstr in the path
                    hoursearchstr = hoursearchstr+searchstr
                    print( "Finding files in "+root+" that match "+hoursearchstr)
                    tarfiles = archraf.findfiles(root,hoursearchstr)

                    tarfiles.sort()
                    Efile = tarfiles[len(tarfiles)-1]
                    (eyr,emo,edy,ehr,emn,esc,hoursearchstr)=archraf.parse_date(Efile)
                    # output tarfile name is like 
                    # RF##.FWD.Sdate.Stime_etime.jpg.tar and tar.dir
                    match = re.search("[RrTtFf][Ff][0-9][0-9]",fullname)
                    if not match:
                        print("Flight number not found in image path. Please")
                        print(" rename camera dirs to contain flight numbers")
                        print(" e.g. RF01\n")
                        raise SystemExit

                    flightnum = (match.group()).upper()
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
        pattern = re.compile(r'.*\/[FRT]F[0-1][0-9]$')
        for file in dirfilelist:
            # Walk through the dirpath (this will ignore paths that 
            # point to a file and
            # only walk through paths that point to a dir.
            path = join(sdir,file)
    
            # Return an array containing the complete path to all 
            # the files matching searchstr in the path
            print("Finding files in "+path+" that match "+searchstr)
            #tarfiles = archraf.findfiles(path,searchstr)
            # For clarity, the tarfile name should contain the 
            # date (yyyymmdd) and flight number. Start with the 
            # directory name.
            tarfilename = file
            if pattern.match(path):
                tarfiles = path
            else:
                continue
            # If the directory name does not contain a year, 
            # add it to the tarfile name.
            [tfile,tfilelist]=archraf.tardir(sdir,file,tarfilename,tarfiles)
            if tfile != "":
                # Add the tar file to the array of files to archive
                sfiles.append(tfile)
                # Add the tar file list to the array of files to archive
                sfiles.append(tfilelist)
        sdir = scr_dir +'/'
    else:
        lines = os.listdir(sdir)
        for line in lines:
            #form = rf'^{proj_name}[a-z][a-z][0-9][0-9].nc'
            match = re.search(searchstr,line)
            if match:
            #     if re.search(form,line):
                print(line)
                sfiles.append(line)
        sdir = sdir + '/'
    
    # Sort the files to be processed so they are processed in alphabetical order
    sfiles.sort()
    csroot = cs_location+proj_name.lower()+'/aircraft/'+platform.lower()+'/'
    #Make sure archive directory exists and if not, create it
    # archraf.create_path(csroot+type)

    # Now archive the data!
    archraf.archive_files_cs(sdir,sfiles,flag,type,csroot,email)

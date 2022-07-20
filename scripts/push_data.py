#! /bin/python3

#  It takes a flight number designation and then using it gets raw ads
#  file, netCDF file and kml file for that flight number (verifying with the
#  user where needed) and does several things:
#  1: Processes the .ads file to create field data as defined in fieldProc_setup.py
#  2: zips up the ads file
#  3: Creates plots using an Rstudio script
#  4: copies nc, kml, 2d, ads to NAS dirs for storage and to sync to Boulder

import os
import re
import sys
import glob
import ftplib
import syslog
import time
import datetime
import glob
import time
import string
import smtplib
from email.mime.text import MIMEText
from collections import OrderedDict

class FieldData():

    def read_env(self, env_var):
        """
        Read and set environment var
        """
        try:
            var = os.environ[env_var]
            return(var)
        except KeyError:
            print("Please set the environment variable " + env_var)
            sys.exit(1)

    def ensure_dir(self, f):
        """ 
        Check if the directory exists and make if not
        """
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    def print_message(self, message):
        """ 
        Set up message printing on the screen as well as in the email message
        """
        global final_message
        print(message)
        final_message = final_message + message

    def rsync_file(self, file, out_dir):
        """
        Rsync file to output dir and record success status
        """
        command = 'rsync '+file+" "+out_dir
        if os.system(command) == 0:
            proc_file = 'Yes-NAS'
            return(str(proc_file));
        else:
            message = '\nERROR!: syncing file: '+command+'\n'
            fielddata.print_message(message)

    def find_lrt_netcdf(self, filetype):
        """
        See if a LRT file exists already and query user about what to do.
        """
        process=False
        reprocess=False
        nclist = glob.glob(data_dir+'*'+flight+'.'+filetype)
        if nclist.__len__() == 1:
            ncfile = nclist[0]
            print("Found a netCDF file: "+ncfile)
            # Since found a netCDF file, query user if they want to reprocess the data,
            # or if they just want to ship the data to the NAS/ftp site.
            reproc = ''
            while reproc == '' and reproc != 'R' and reproc != 'S':
                reproc = input('Reprocess? (R) or Ship? (S):')
            if reproc == 'R':
                process = True
                reprocess = True
            else: # Ship only
                process = False
                reprocess = False
        elif nclist.__len__() == 0:
            print("No files found matching form: "+data_dir+'*'+flight+'.'+filetype)
            print("We must process!")
            process = True
            ncfile = data_dir+file_prefix+".nc"
        else:
            print("More than one "+filetype+" file found.")
            ncfile=fielddata.step_through_files(nclist)

        if ncfile == '' :
            print("No NetCDF file identified!")
            print("Aborting")
            sys.exit(0)

        return(process,reprocess,ncfile)

    def find_file(self, data_dir, flight, project, filetype, fileext, flag, date=""):
        """
        See if a file exists already and query user about what to do.

        Look for files in data_dir that match the filename pattern *[rtfc]f##.ext
        ICARTT files follow the NASA convention project_platform_date_R[A-Z0-9].ict
        so must be handled separately.
        Note that LRT files are handled as a special case by find_lrt_netcdf

        Input:
            flight - flight type designator and number eg rf01
            project - project + flight e.g. ACCLIPrf01
            filetype - s for sample rate, h for high rate, etc
            fileext - .asc, .nc, etc
        Return:
            datafile - Name of file found
            flag - True if file should be reprocessed
        """
        datafile = ''
        if fileext == 'ict':
            pattern = data_dir + project + '*' + date + '*' + fileext
            # pattern2 is a dummy placeholder. will overwrite the output
            # filename to match the strict ICARTT filename convention.
            #pattern2 = data_dir + project + date + '.' + fileext
            datalist = glob.glob(pattern)
        else:
            # pattern needs a star to match the ads file
            pattern = data_dir + "*" + flight + filetype + '.' + fileext
            # pattern2 is the name of files to regenerate, other than ads
            #pattern2 = data_dir + project + flight + filetype + '.' + fileext
            datalist = glob.glob(pattern)

        if (datalist.__len__() == 1):
            # Found a single file of the type we are looking for [eg ads or lrt or
            # nc, etc. Find out if user wants to reprocess the file?
            if (flag == False):
                reproc = input('Found file: ' + datalist[0] + '. Reprocess?(Y/N)')
                if reproc == 'Y':
                   flag = True
            datafile = datalist[0]  # Return name of file that was found
        elif datalist.__len__() == 0:
            # Did not find any files with the extension we are looking for
            print("No files found matching form: " + pattern)
            if fileext == 'ads':
                # If we can't find an ads file, then there is nothing to do.
                print("Aborting...")
                sys.exit(0)
            else:
                # Any other files that can't be found can be regenerated
                if process:
                    print("We are scheduled to process all is good")
                    datafile = pattern2
                else:
                    # but if the file is not marked to be regenerated in the
                    # fieldProc_setup.py file, then we have a probem.
                     print("We have an nc file but not "+fileext+" file.... " +
                           "aborting...")
                     sys.exit(0)
        else:
             # Found multiple files that match the type we are looking for.
             # Step through the files and let the user decide which is the one we
             # should work with
             print("More than one "+fileext+" file found.")
             datafile=fielddata.step_through_files(datalist, fileext)

        if datafile == '' :
            # If after all this we haven't identified a file, abort processing.
            print("No "+datafile+" file identified!")
            print("Aborting...")
            sys.exit(0)

        return(flag, datafile)

    def step_through_files(self, datalist, fileext):
        """
        Handle multiple files of a given type for a single flight

        Input:
            datalist - list of files of the same type
            fileext - file type extesion, just used for user messages
        Return: File from list selected by user
        """
        datafile = ''
        if reprocess == True:
            print("Stepping through files, please select the right one.")
            i = 0
            while datafile == '':  # Loop until user chooses
                ans = input(datalist[i]+'? (Y/N)')
                if ans == 'Y' or ans == 'y':
                    datafile = datalist[i]
                if i < datalist.__len__() - 1:
                    i = i + 1
                else:
                    i = 0
        else:
            # Not processing so just return the first file, which is all that we
            # need to successfully set off shipping
            datafile = datalist[0]
            print('Ship is set to True so no need to choose ' + fileext +
                  'to process.')
        return(datafile)

    def process_netCDF(self, rawfile, ncfile, pr, config_ext):
        """"
        Run nimbus to create a .nc file (LRT, HRT, or SRT)
        """
        # If there is a setup file for this flight in proj_dir/Production
        # use that. If not, create one.

        nimConfFile = proj_dir+"Production/setup_"+flight+config_ext

        if not os.path.exists(nimConfFile):
            cf = open(nimConfFile, 'w')
            sdir,sfilename = os.path.split(rawfile)
            line = "if=${RAW_DATA_DIR}/"+project+"/"+sfilename+'\n'
            cf.write(str(line))
            sdir,sfilename = os.path.split(ncfile)
            line = "of=${DATA_DIR}/"+project+"/"+sfilename+'\n'
            cf.write(str(line))
            line = "pr="+pr+'\n'
            cf.write(str(line))
            cf.close()

        command = "/opt/local/bin/nimbus -b "+nimConfFile
        print("about to execute nimbus I hope: "+command)

        res = os.system(command)
        print('\nresult of nimbus call = '+str(res))
        print()
        return(True)
        return(rawfile)

    def process_threeVCPI(self, aircraft, project, flight, twods_raw_dir, oapfile_dir):
        """
        Process 3vCPI
        """
        print("\n\n *****************  3VCPI **************************\n")
        mkdir_fail = False
        first_base_file = ''
        catted_file = 'base_'+flight+'all.2DSCPI'
        catted_2d_file = 'base_'+flight+'all.2d'
        os.chdir(twods_raw_dir)
        if os.path.isfile(catted_file):
            os.remove(catted_file)
        file_list = glob.glob(twods_raw_dir+'base*2DSCPI')
        if len(file_list) > 0:
            os.chdir(twods_raw_dir)
            filenum = 1
            for file in file_list:
                if filenum == 1:
                    first_base_file = file
                command = 'cat '+file+' >> '+catted_file
                print("cat 3vcPIfiles:"+command)
                os.system(command)

            command = translate2ds + '-project ' + project + ' -flight ' + flight \
                    +' -platform '+aircraft + ' -sn SPEC001 -f ' + catted_file + ' -o .'
            print(' 3v-cpi command:' + command)
            os.system(command)

            # move 2DS file to the RAF naming convention and location
            if not os.path.isdir(oapfile_dir):
                try:
                    os.mkdir(oapfile_dir)
                except:
                    message= "\nERROR: Could not make oapfile directory:"+oapfile_dir
                    message= message +  "\n  - skipping 2d file gen/placement\n"
                    fielddata.print_message(message)
                    mkdir_fail = True
            if not mkdir_fail:
                twod_dir,fb_filename=os.path.split(first_base_file)
                datetime = fb_filename.split('.')[0].split('e')[1] #Pull out of base{datetime}.2d
                command = 'mv '+catted_2d_file+' '+oapfile_dir+'20'+datetime+'_'+flight+'.2d'
                print(' mv command: '+command)
                os.system(command)
                threevcpi2d_file = oapfile_dir+'20'+datetime+'_'+flight+'.2d'

                # Merge 3v-cpi data into netCDF file
                command = 'process2d '+threevcpi2d_file+' -o '+ncfile
                print("3v-cpi merge cmd: "+command)
                if os.system(command) == 0:
                    proc_3vcpi_files = 'Yes'

    def reorder_nc(self, ncfile):
        """
        Reorder netcdf file
        """
        command = "ncReorder "+ncfile+" tmp.nc";
        print("about to execute : "+command)
        os.system(command)

        command = "/bin/mv tmp.nc "+ncfile;
        print("about to execute : "+command)
        if os.system(command) == 0:
            proc_nc_file  =    'Yes'
        else:
            message= "ERROR: NC Reorder failed! But NetCDF file should be fine\n"
            fielddata.print_message(message)
            proc_nc_file  =    'Yes'
        return(proc_nc_file)

    def zip_file(self, filename,datadir):
        """
        Create Zip file
        """
        os.chdir(datadir)
        command = "zip " + filename + ".zip " + filename
        if os.system(command) != 0:
            message =  "\nERROR!: Zipping up " + filename + " with command:\n  "
            message = message + command
            fielddata.print_message(message)

fielddata = FieldData()

project = fielddata.read_env("PROJECT")
print("project: "+ project)
data_dir = fielddata.read_env("DATA_DIR") + '/' + project.upper() + '/'
raw_dir  = fielddata.read_env("RAW_DATA_DIR") + '/' + project.upper() + '/'

# Get aircraft from proj dir
aircraft = os.listdir(fielddata.read_env("PROJ_DIR") + '/' + project)[0]
print("aircraft: "+ aircraft)
proj_dir  = fielddata.read_env("PROJ_DIR") + '/' + project + '/' + aircraft + '/'

# Initialization
sys.path.insert(0,proj_dir+'/scripts')
from fieldProc_setup import *

# Query user for the flight designation and place to send output
flight = input('Input flight designation (e.g. tf01):')
email = input('Input email address to send results:')
Batch = proj_dir + 'scripts/nc2asc.bat'
zip_dir = '/tmp/'
qc_ftp_site = 'catalog.eol.ucar.edu'
qc_ftp_dir = '/pub/incoming/catalog/'+ project.lower()

def setup():
    """
    Create objects for multiple processing inputs
    """
    if aircraft == "GV_N677F":
        raircraft = 'aircraft.NSF_NCAR_GV.'
    elif aircraft == "C130_N130AR":
        raircraft = 'aircraft.NSF_NCAR_C-130.'
    else:
        print("Unknown aircraft "+aircraft+" Update code\n")
        sys.exit(1)

    print("Processing " +project+ " from " +aircraft+ ".   If incorrect, edit ~/ads3_environment.")
    print("Expecting to find .ads files in "+raw_dir+".")
    return raircraft

setup()

# *************************  Dictionaries ************************
# These are directories where instrument-specific data files (not
# RAF standard data) can be found.
inst_dir = {
    "ADS"   : raw_dir,
    "LRT"   : data_dir,
    "KML"   : data_dir,
    "HRT"   : data_dir,
    "SRT"   : data_dir,
    "ICARTT": data_dir,
    "IWG1"  : data_dir,
    "PMS2D" : raw_dir+'PMS2D/',
    "twods" : raw_dir+'3v_cpi/2DS/'+ project.upper() +'_'+ flight.upper() + '/',
    "oap"   : raw_dir+'3v_cpi/oapfiles/',
    "cpi"   : raw_dir+'3v_cpi/CPI/'+project.upper() + '_' + flight.upper() + '/',
    }

# Add extensions here for file types you want to process
# This should ONLY contain extensions based on files you want to process
# Populate from config file fieldProc_setup.py based on True/False settings.
file_ext = OrderedDict ([("ADS" , "ads"), ("LRT" , "nc"), ("KML" , "kml")])
if HRT:
    file_ext["HRT"] =  "nc"
if SRT:
    file_ext["SRT"] =  "nc"
if ICARTT:
    file_ext["ICARTT"] = "ict"
if IWG1:
    file_ext["IWG1"] = "iwg"
if PMS2D:
    file_ext["PMS2D"] = "2d"
if threeVCPI:
    file_ext["threeVCPI"] = "2ds"

# Dictionary to hold data file names
filename = {}

# NetCDF filename rate indicator
file_type = {
    "ADS" : "",
    "LRT" : "",
    "KML" : "",
    "HRT" : "h",
    "SRT" : "s",
    "ICARTT" : "",
    "IWG1" : "",
    "PMS2D" : "",
    }

# nimbus processing rates (for use in config files)
rate = {
    "LRT" : "1",
    "HRT" : "25",
    "SRT" : "0",
    }

# nimbus config filename extensions
config_ext = {
    "LRT" : "",
    "HRT" : "h",
    "SRT" : "s",
    }

# This dictionary contains a list of all file types you want to report
# status on.
status = {
   "ADS"         : { "proc" : "N/A", "ship" : "No!", "stor" : "No!"},
   "LRT"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "KML"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "HRT"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "SRT"         : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "ICARTT"      : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "IWG1"        : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "PMS2D"       : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "threeVCPI"   : { "proc" : "No!", "ship" : "No!", "stor" : "No!"},
   "QCplots"     : { "proc" : "No!", "ship" : "No!", "stor" : "No!"}
   }

######################   Begin main function  ############################

# Create the project- and flight-specific filename prefix (e.g. WECANrf01)
file_prefix =   project + flight

# Prepare for final message information
final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
final_message = final_message + 'Process and Push log for Project:' + project
final_message = final_message + '  Flight:'+flight+'\r\n'


# Make sure the directory to store processed data exists.
fielddata.ensure_dir(data_dir)

# 3VCPI
threevcpi2d_file = ''

# Confirm code exists for RStudio plotting
if not os.path.exists(rstudio_dir):
  print('RStudio DataReview has not been checked out at : '+ rstudio_dir)
  print('QC plots cannot be generated.')

def process():
    ###################  Beginning of Processing ##############################
    ## Get the netCDF, kml, icartt, IWG1 and raw ADS files for working with ##

    # First the LRT netCDF. We use this to determine if code has been run before
    # because we ALWAYS generate a LRT data file for every flight.
    # Determine if we are in process, reprocess, or ship mode.
    (process,reprocess,filename['LRT']) = fielddata.find_lrt_netcdf(file_ext['LRT'])

    # Next get the ADS file so we can determine the flight date. This is needed
    # in order to indentify the correct ICARTT file, since ICARTT files follow the
    # NASA naming convention and don't use our flight numbering system.
    (reprocess, filename['ADS']) = \
        fielddata.find_file(inst_dir['ADS'], flight, project, file_type['ADS'],
                  file_ext['ADS'], process)

    # Get the flight date from the ADS filename
    file_name = filename["ADS"].split(raw_dir)[1]
    date = file_name[:15]
    date = re.sub('_','', date)

    # Now everthing else (skip LRT) using the NCAR/EOL/RAF flight number to
    # identify the file associated with the current flight.
    for key in file_ext:
        if (key == "LRT") or (key == "ADS"):
            next;
        else:
            (reprocess, filename[key]) = \
                fielddata.find_file(inst_dir[key], flight, project, file_type[key],
                          file_ext[key], process, date[0:8])

    if process:
        for key in file_ext:

            # Process the ads data to desired netCDF frequencies
            if ((key == "LRT" or key == "HRT" or key == "SRT") and process):
                res=fielddata.process_netCDF(filename["ADS"],filename[key],rate[key],config_ext[key])
                if res:
                    status[key]["proc"]= fielddata.reorder_nc(filename[key])
                else:
                    status[key]["proc"] = False

            # Generate IWG1 file from LRT, if requested
            if (key == "IWG1"):
                command = "nc2iwg1 "+filename["LRT"]+" -o "+filename[key];
                print("about to execute : "+command)
                if os.system(command) == 0:
                    status[key]["proc"] = 'Yes'
    
            # Generate ICARTT file from LRT, if requested
            if (key == "ICARTT"):
                command = "nc2asc -i "+filename["LRT"]+" -o "+ data_dir+"temp_filename." -b "+nc2ascBatch;
                print("about to execute : "+command)
                if os.system(command) == 0:
                    status[key]["proc"] = 'Yes'

            # Convert SPEC file form to oap file form
            if (key == "threeVCPI"):
                fielddata.process_threeVCPI(aircraft,project,flight,inst_dir["twods"],inst_dir["oap"])

            # Fast 2D data, extract first, then process.
            if (key == "PMS2D"):
                fielddata.ensure_dir(inst_dir["PMS2D"])
                file_name = filename["ADS"].split(raw_dir)[1]
                fileelts = file_name.split('.')
                filename["PMS2D"] = inst_dir["PMS2D"] + fileelts[0] + '.2d'

                if not os.path.exists(filename["PMS2D"]):
                    # General form of extract2d from RAW_DATA_DIR is:
                    # Extract2d PMS2D/output.2d input.ads
                    command = 'extract2d '+filename["PMS2D"]+' '+filename["ADS"]
                    message = '\nExtracting 2D from ads:'+command+'\n'
                    print(message)
                    os.system(command)

                if os.path.exists(filename["PMS2D"]):
                    # Process 2D data into netCDF file.  General form is:
                    # Process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
                    command = 'process2d '+filename["PMS2D"]+' -o '+filename["LRT"]
                    print('2D merge command: '+command)
                    if os.system(command) == 0:
                        status["PMS2D"]["proc"] = 'Yes'
                        #status["PMS2D"]["ship"] = 'Yes'
                        #status["PMS2D"]["stor"] = 'Yes'

    # Run Al Cooper's R code for QA/QC production
    # Currently requires being run from the ~/RStudio/QAtools directory.
    # To run interactively: launch rstudio, then type "shiny::runApp()"
    if Rstudio:
        os.chdir(rstudio_dir+"aircraft_QAtools")
        command = "Rscript DataReview.R "+project+" "+flight
        print("about to execute : "+command)
        os.system(command)

        command = "cp -p "+project+flight+"Plots.pdf /home/ads/Desktop"
        print("copying QAQC pdf to desktop")
        os.system(command)

process()

def setup_shipping():
    """
    Beginning of Shipping
    """
    print("")
    print("************************** Begin Shipping Data ***************")
    for key in file_ext:
        print(key+" file = "+filename[key])
        print(os.system("ls -l "+filename[key]))
    print("**************************************************************")
    print("")
    print(" We're not done yet. Please be patient.")

    if NAS:
        if NAS_permanent_mount == False:
            # Mount NAS
            command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
            print('\r\nMounting nas: '+command)
            os.system(command)

        # Put copies of files to local store
        # in dirs to sync to ftp site in Boulder...
        nas_sync_dir = nas_mnt_pt+'/FTP_sync/EOL_data/RAF_data/'
        # and in dirs for local use...
        nas_data_dir = nas_mnt_pt+'/EOL_data/RAF_data/'

        print("")
        print("*************** Copy files to NAS scratch area ***************")
        for key in file_ext:
            fielddata.ensure_dir(nas_data_dir)
            if (key == "ADS"):
                if (not reprocess) and process:
                    print('Copying '+filename[key]+' to '+nas_data_dir+'/ADS')
                    status[key]["stor"] = fielddata.rsync_file(filename[key],nas_data_dir+'/ADS')
                elif (key == "PMS2D"):
                    print('Copying '+filename[key]+' to '+nas_data_dir+'/PMS2D/')
                    status[key]["stor"] = fielddata.rsync_file(filename[key],nas_data_dir+'/PMS2D/')
                else:
                    print('Copying '+filename[key]+' to '+nas_data_dir+'/'+key)
                    status[key]["stor"] = fielddata.rsync_file(filename[key],nas_data_dir+'/'+key)

        if catalog:
            fielddata.ensure_dir(nas_data_dir+"/qc")
            print('Copying QC plots to '+nas_data_dir+"/qc")
            status[key]["stor"] = fielddata.rsync_file(rstudio_dir+"/QAtools/"+raircraft+date+".RAF_QC_plots.pdf",nas_data_dir+"/qc")

        print("")

setup_shipping()

def setup_email():
    """
     Set up email
    """
    emailfilename = 'email.addr.txt'
    emailfile = data_dir+emailfilename
    command = 'rm '+emailfile
    print(command)
    os.system(command)
    fo = open(emailfile, 'w+')
    fo.write(email+'\n')
    fo.close()

setup_email()

def setup_zip():
    """
    ZIP up the files as per expectations back home
    this only affects non-ads files
    """
    if sendzipped:
        for key in file_ext:
            if (key == "ADS"):
                print("Raw .ads file found but not zipping, if zip_ads is set, will bzip .ads file next.")
            elif (key == "PMS2D"):
                print("Raw .2d file found but not zipping.")
            else:
                data_dir,file_name = os.path.split(filename[key])
                print(key+" filename = "+file_name)
                print("data_dir = "+data_dir)
                fielddata.zip_file(file_name,inst_dir[key])

setup_zip()

def datadump():
    """
    Data_dump section
    Project specific data_dump's for indivual users.
    """
    #if datadump:
    #    # PICARRO data - extract and write to nas_sync_dir
    #    ddfilename = 'picarro_'+flight+'.asc'
    #    command = 'data_dump -i 10,600 -A '+rawfile+' > '+data_dir+'/'+ddfilename
    #    os.system(command)
    #    command = 'zip '+nas_sync_dir+'picarro_'+flight+'.zip '+data_dir+'/'+ddfilename
    #    os.system(command)

    # Put QC files into catalog and to the NAS if it exists
    if catalog:
        try:
            print("")
            print("*************************** Catalog transfer *****************")
            print('opening FTP connection to: ' + qc_ftp_site)
            print('- putting QC data in directory: ' + qc_ftp_dir)

            ftp = ftplib.FTP(qc_ftp_site)
            ftp.login("anonymous", email)
            ftp.cwd(qc_ftp_dir)

            print("Renaming file "+project+flight+"Plots.pdf")
            command = "/bin/mv "+rstudio_dir+"/QAtools/"+project+flight+"Plots.pdf "+rstudio_dir+"/QAtools/"+raircraft+date+".RAF_QC_plots.pdf"
            print("about to execute : "+command)
            if os.system(command) == 0:
                status["QCplots"]["ship"] =    'Yes-Cat'
                print("Sending file "+raircraft+date+".RAF_QC_plots.pdf to catalog")
                os.chdir(rstudio_dir+"/QAtools")
                file = open(raircraft+date+".RAF_QC_plots.pdf", 'r')
                print(ftp.storbinary('STOR ' + raircraft+date+".RAF_QC_plots.pdf", file))
                file.close()
            else:
                message= "ERROR: Rename of plots failed\n"

        except ftplib.all_errors as e:
            print("")
            print('Error writing QC data to server')
            print(e)
            try:
                ftp.quit()
            except ftplib.all_errors as e:
                print('Could not close ftp connection:')
                print(e)

        print("*************************** End Catalog transfer *************\n")

datadump()

def setup_FTP():
    # No NAS this project, so put files to EOL server. Put
    # zipped files if they exist.
    if FTP == True:
        try:
            print('opening FTP connection to: ' + ftp_site)

            ftp = ftplib.FTP(ftp_site)
            ftp.login(user, password)
            print('')

        except ftplib.all_errors as e:
            print ('')
            print('Error connecting to FTP site ' + ftp_site)
            print(e)
            ftp.quit()

        print('Putting files:')
        print('')

        # At each execution, ftp all .ads files from project
        print('Starting ftp process for all available .ads files')
        for rawfilename in os.listdir(raw_dir):
            if rawfilename.endswith('.ads'):
                try:
                    os.chdir(raw_dir)
                    ftp.cwd('/'+ftp_data_dir+'/ADS')
                    ftp.storbinary('STOR '+rawfilename, open(rawfilename, 'rb'))
                    status["ADS"]["stor"] = 'Yes-FTP'
                    print(rawfilename+' ftp successful!')
                except:
                    print(rawfilename+' not sent')
            else:
                pass
            
        for fn in os.listdir(data_dir):
            if fn.endswith('.ict'):
                try:
                    os.chdir(data_dir)
                    ftp.cwd('/'+ftp_data_dir+'/ICARTT')
                    ftp.storbinary('STOR '+fn, open(fn, 'rb'))
                    status["ICARTT"]["stor"] = 'Yes-FTP'
                except Exception as e:
                    print(e)
  
            elif fn.endswith('.kml'):
                try:
                    os.chdir(data_dir)
                    ftp.cwd('/'+ftp_data_dir+'/KML')
                    ftp.storbinary('STOR '+fn, open(fn, 'rb'))
                    status["KML"]["stor"] = 'Yes-FTP'
                except Exception as e:
                    print(e)
                
        for key in file_ext:
            print('')
            try:
                os.chdir(inst_dir[key])
            except ftplib.all_errors as e:
                print('Could not change to local dir '+inst_dir[key])
                print(e)
                continue

            print('Putting '+filename[key]+' to '+ftp_site+':/'+ftp_data_dir+'/'+key)
            if filename[key] != '':
                try:
                    data_dir,file_name = os.path.split(filename[key])
                    if sendzipped:
                        file_name = file_name+'.zip'
                    else:
                        file_name = file_name
                        ftp.cwd('/'+ftp_data_dir+'/'+key)
                except ftplib.all_errors as e:
                    # Attempt to create needed dir
                    print ('Attempt to create dir /'+ftp_data_dir+'/'+key)
                    try:
                        ftp.mkd('/'+ftp_data_dir+'/'+key)
                    except:
                        print('Make dir '+ftp_data_dir+'/'+key+' failed')
                        print(e)
                        continue
                    # Try to change to dir again
                    try:
                        ftp.cwd('/'+ftp_data_dir+'/'+key)
                    except:
                        print('Change dir to '+ftp_data_dir+'/'+key+' failed')
                        print(e)
                        continue

                if file_name in ftp.nlst():
                    print('File '+file_name+' already exists on ftp server.')
                    print('File will not be transfered to ftp site')
                    print('To force transfer, delete file from ftp site and rerun in Ship mode')
                    continue

                try:
                    file = open(file_name, 'rb')
                    print(ftp.storbinary('STOR ' + file_name, file))
                    file.close()
                    status[key]["stor"] = 'Yes-FTP'

                    print(datetime.datetime.now().time())
                    print('Finished putting data file')
                    print('')

                except ftplib.all_errors as e:
                    print('Error writing '+file_name+' to '+ftp_site+':/'+ftp_data_dir+'/'+key)
                    print(e)
                    continue

            else:
                print('Filename is empty - nothing to write')

        ftp.quit()

setup_FTP()

# Put file onto NAS for BTSyncing back home.
if NAS == True:
  print("")
  print("***** Copy files to NAS sync area for transfer back home *****")

  if reprocess or (not reprocess and not process):
    final_message = final_message + '\n***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'
    final_message = final_message + 'Reprocessing so assume ADS already shipped during first processing\n'
    final_message = final_message + 'If this is not the case, run\n\n'
    final_message = final_message + '"cp /home/data/Raw_Data/'+project+'/*'+flight+'.ads '+nas_sync_dir+'/ADS"\n\n'
    final_message = final_message + '"cp /home/data/Raw_Data/'+project+'/*'+flight+'.ads '+nas_data_dir+'/ADS"\n\n'
    final_message = final_message + 'when this script is complete\n\n'
    final_message = final_message + '***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'

  if zip_ADS:
      # Now only zip up the ADS file, if requested
      raw_dir,rawfilename = os.path.split(filename["ADS"])
      print("zipping "+rawfilename)
      zip_raw_file = zip_dir + rawfilename + '.bz2'
      print("rawfilename = "+zip_raw_file)
      os.chdir(raw_dir)
      #if not os.path.exists(zip_raw_file):
      print("Compressing ADS file with command:")
      command = "bzip2 -kc " + rawfilename + " > " + zip_raw_file
      print(command)
      os.system(command)
      print("")
  else:
      print('.ads file not being zipped due to preference')

  # mount the NAS and put files to it
  if NAS_permanent_mount == False:
     # Mount NAS
     command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
     print('\r\nMounting nas: '+command)
     os.system(command)

  for key in file_ext:
    os.chdir(inst_dir[key])
    if (key == "ADS"):
        if ship_ADS == True:
            if zip_ADS == True:
                print('Copying '+zip_raw_file+' file to '+nas_sync_dir+'/ADS')
                fielddata.rsync_file(zip_raw_file,nas_sync_dir+'/ADS')
                print('Done')
            else:
                print('Copying '+filename[key]+' file to '+nas_sync_dir+'/ADS')
                fielddata.rsync_file(filename[key],nas_sync_dir+'/ADS')
                print('Done')
        else:
            pass
    elif (key == "PMS2D"):
        print('Copying '+filename[key]+' file to '+nas_sync_dir+'/PMS2D')
        status[key]["ship"] = fielddata.rsync_file(filename[key],nas_sync_dir+'/PMS2D')
        print('Done')
    else:
      if sendzipped == True:
        print('Copying '+filename[key]+'.zip file to '+nas_sync_dir+'/'+key)
        status[key]["ship"] = fielddata.rsync_file(filename[key]+'.zip',nas_sync_dir+'/'+key)
        print('Done')
      else:
        print('Copying '+filename[key]+' file to '+nas_sync_dir+'/'+key)
        status[key]["ship"] = fielddata.rsync_file(filename[key],nas_sync_dir+'/'+key)
        print('Done')


final_message = final_message + '\nREPORT on shipping of files. \n\n'
final_message = final_message + 'File Type\tStor\tShip\n'

for key in file_ext:
  if key != "ADS":
    final_message = final_message +key+'\t\t'+str(status[key]["stor"])+'\t'+str(status[key]["ship"])+'\n'
  else:
    pass
  final_message = final_message +key+'\t\t'+str(status[key]["stor"])+'\t'+str(status[key]["ship"])+'\n'

final_message = final_message + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

print(final_message)
msg = MIMEText(final_message)
msg['Subject'] = 'Process & Push message for:'+project+'  flight:'+flight
msg['From'] = 'ads@groundstation'
msg['To'] = email

s = smtplib.SMTP('localhost')
s.sendmail('ads@groundstation',email, msg.as_string())
s.quit()

print("\r\nSuccessful completion. Close window to exit.")
sys.exit(1)


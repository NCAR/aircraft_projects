#! /bin/python3

#  It takes a flight number designation and then using it gets raw ads
#  file, netCDF file and kml file for that flight number (verifying with the
#  user where needed) and does several things:
#  1: Processes the .ads file to create field data
#     as defined in fieldProc_setup.py
#  2: zips up the ads file (if defined)
#  3: Creates plots using an Rstudio script (if defined)
#  4: copies nc, kml, 2d, ads to NAS dirs for storage and to sync to Boulder OR
#  5: copies nc, kml, 2d, ads, to FTP directly
#
#  August 2022 TMT: Refactor to create functions within class FieldData
#  Copyright University Corporation for Atmospheric Research (2022)

import os
import re
import glob
import ftplib
import sys
import datetime
import smtplib
import argparse
from email.mime.text import MIMEText
from collections import OrderedDict
import logging
sys.path.insert(0, '/home/local/projects/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, datadump, GDRIVE, rclone_staging_dir

class FieldData():

    def __init__(self):
        '''
        Define __init_ function to create objects for paths
        and various dictionaries for dirs, filenames, etc.
        '''
        self.logger = logging.getLogger(__name__)  
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler('/tmp/push_data.log')
        self.formatter = logging.Formatter('%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        #self.parse_args()
        #self.project = self.args.PROJECT[0]
        self.project = self.getProject()
        print('Project: ' + self.project)
        self.data_dir = self.getDataDir() + '/' + self.project.upper() + '/'
        self.raw_dir = self.getRawDir() + '/' + self.project.upper() + '/'
        self.aircraft = os.listdir(self.getProjDir() + '/' + self.project)[0]
        print('Aircraft: ' + self.aircraft)
        self.proj_dir = self.getProjDir() + '/' + self.project + '/' + self.aircraft + '/'
        self.nc2ascBatch = self.proj_dir + 'scripts/nc2asc.bat'
        self.zip_dir = '/tmp/'
        self.qc_ftp_site = 'catalog.eol.ucar.edu'
        self.qc_ftp_dir = '/pub/incoming/catalog/' + self.project.lower()
        self.flight = self.readFlight()
        self.email = self.readEmail()
        self.rclone_staging_dir = rclone_staging_dir
        process = False
        reprocess = False

        self.setup(self.aircraft, self.project, self.raw_dir)
        self.createInstDir(self.raw_dir, self.data_dir, self.project, self.flight)
        self.createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)
        self.createFilenameDict()
        self.createFileType()
        self.createRate()
        self.createConfigExt()
        self.createStatus()
        self.createFilePrefix(self.project, self.flight)
        self.initializeFinalMessage(self.flight, self.project)
        self.ensureDataDir(self.data_dir)

    def parse_args(self):
        # set up argument parsing
        parser = argparse.ArgumentParser(
            description='Provide project (e.g. TI3GER):')

        # define input file(s) to process
        parser.add_argument('PROJECT', type=str, nargs='*',
                            help='Provide name of project.')

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        self.args = parser.parse_args()
        return(self.args)


    def createFileExt(self, HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI):
        '''
        Create an ordered dictionary containing the file extensions by
        file type. Uses the settings from fieldProc_setup.py
        '''
        self.file_ext = OrderedDict([("ADS", "ads"), ("LRT", "nc"), ("KML", "kml")])
        if HRT:
            self.file_ext["HRT"] = "nc"
        if SRT:
            self.file_ext["SRT"] = "nc"
        if ICARTT:
            self.file_ext["ICARTT"] = "ict"
        if IWG1:
            self.file_ext["IWG1"] = "iwg"
        if PMS2D:
            self.file_ext["PMS2D"] = "2d"
        if threeVCPI:
            self.file_ext["threeVCPI"] = "2ds"

        return self.file_ext

    def createFilenameDict(self):
        self.filename = {}
        return self.filename

    def createFileType(self):
        '''
        NetCDF filename rate indicator
        '''
        self.file_type = {
            "ADS": "",
            "LRT": "",
            "KML": "",
            "HRT": "h",
            "SRT": "s",
            "ICARTT": "",
            "IWG1": "",
            "PMS2D": "",
            }
        return self.file_type

    def createInstDir(self, raw_dir, data_dir, project, flight):
        '''
        These are directories where instrument-specific data files (not
        RAF standard data) can be found.
        '''
        self.inst_dir = {
                   "ADS": raw_dir,
                   "LRT": data_dir,
                   "KML": data_dir,
                   "HRT": data_dir,
                   "SRT": data_dir,
                   "ICARTT": data_dir,
                   "IWG1": data_dir,
                   "PMS2D": raw_dir,
                   "twods": raw_dir + '3v_cpi/2DS/' + project.upper() + '_' + flight.upper() + '/',
                   "oap": raw_dir + '3v_cpi/oapfiles/',
                   "cpi": raw_dir + '3v_cpi/CPI/' + project.upper() + '_' + flight.upper() + '/',
                   }
        return self.inst_dir

    def createStatus(self):
        '''
        This dictionary contains a list of all file types you want to report
        status on.
        '''
        self.status = {"ADS": {"proc": "N/A", "ship": "No!", "stor": "No!"},
                       "LRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "KML": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "HRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "SRT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "ICARTT": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "IWG1": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "PMS2D": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "threeVCPI": {"proc": "No!", "ship": "No!", "stor": "No!"},
                       "QCplots": {"proc": "No!", "ship": "No!", "stor": "No!"}}
        return self.status

    def createFilePrefix(self, project, flight):
        '''
        Create the project- and flight-specific filename prefix (e.g. WECANrf01)
        '''
        self.file_prefix = project + flight
        return self.file_prefix

    def createRate(self):
        '''
        nimbus processing rates (for use in config files)
        '''
        self.rate = {
            "LRT": "1",
            "HRT": "25",
            "SRT": "0",
            }
        return self.rate

    def createConfigExt(self):
        '''
        nimbus config filename extensions
        '''
        self.config_ext = {"LRT": "", "HRT": "h", "SRT": "s", }
        return self.config_ext

    def ensureDataDir(self, data_dir):
        self.ensure_dir(data_dir)

    def initializeFinalMessage(self, flight, project):
        '''
        Prepare for final message information
        '''
        self.final_message = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\r\n'
        self.final_message = self.final_message + 'Process and Push log for Project:' + project
        self.final_message = self.final_message + '  Flight:'+flight+'\r\n'
        return self.final_message

    def readFlight(self):
        '''
        Read user input to determine the event
        '''
        self.flight = input('Input flight designation (e.g. tf01):')
        return self.flight

    def readEmail(self):
        '''
        Read user input to determine the email address
        '''
        self.email = input('Input email address to send results:')
        return(self.email)

    def read_env(self, env_var):
        '''
        Read and set environment var
        '''
        try:
            var = os.environ[env_var]
            return(var)
        except KeyError:
            message = 'Please set the environment variable ' + env_var
            self.logger.error(message)
            print(message)
            sys.exit(1)

    def ensure_dir(self, f):
        '''
        Check if the directory exists and make if not
        '''
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    def print_message(self, message):
        '''
        Set up message printing on the screen as well as in the email message
        '''
        message = ''
        self.logger.info(message)
        print(message)

    def rsync_file(self, file, out_dir):
        '''
        Rsync file to output dir and record success status
        '''
        command = 'rsync '+file+" " + out_dir
        if os.system(command) == 0:
            proc_file = 'Yes-NAS'
            return(str(proc_file))
        else:
            rsync_message = '\nERROR!: syncing file: ' + command + '\n'
            self.print_message(rsync_message)

    def find_lrt_netcdf(self, filetype, flight, data_dir, file_prefix):
        '''
        See if a LRT file exists already and query user about what to do.
        '''
        process = False
        reprocess = False
        nclist = glob.glob(data_dir + '*' + flight + '.' + filetype)
        if nclist.__len__() == 1:
            self.ncfile = nclist[0]
            message = "Found a netCDF file: "+self.ncfile
            self.logger.info(message)
            print(message)
            # Since found a netCDF file
            # query user if they want to reprocess the data,
            # or if they just want to ship the data to the NAS/ftp site.
            reproc = ''
            while reproc == '' and reproc != 'R' and reproc != 'S':
                reproc = input('Reprocess? (R) or Ship? (S):')
            if reproc == 'R':
                process = True
                reprocess = True
            # Ship only
            else:
                process = False
                reprocess = False
        elif nclist.__len__() == 0:
            message = "No files found matching form: " +\
                  data_dir + '*' + flight + '.' + filetype
            self.logger.info(message)
            print(message)
            message = "We must process!"
            self.logger.info(message)
            print(message)
            process = True
            self.ncfile = data_dir + file_prefix + ".nc"
        else:
            message = "More than one " + filetype + " file found."
            self.logger.info(message)
            print(message)
            self.ncfile = self.step_through_files(nclist, fileext, reprocess)

        if self.ncfile == '':
            message = "No NetCDF file identified! Aborting"
            self.logger.info(message)
            print(message)
            sys.exit(0)

        return(process, reprocess, self.ncfile)

    def find_file(self, data_dir, flight, project,
                  filetype, fileext, flag, reprocess, date=""):
        '''
        See if a file exists already and query user about what to do.

        Look for files in data_dir that match the
        filename pattern *[rtfc]f##.ext ICARTT files follow the
        NASA convention project_platform_date_R[A-Z0-9].ict
        so must be handled separately. Note that LRT files are
        handled as a special case by find_lrt_netcdf

        Input:
            flight - flight type designator and number eg rf01
            project - project + flight e.g. ACCLIPrf01
            filetype - s for sample rate, h for high rate, etc
            fileext - .asc, .nc, etc
        Return:
            datafile - Name of file found
            flag - True if file should be reprocessed
        '''
        datafile = ''
        if fileext == 'ict':
            pattern = data_dir + project + '*' + fileext
            datalist = glob.glob(pattern)
        else:
            # pattern needs a star to match the ads file
            pattern = data_dir + "*" + flight + filetype + '.' + fileext
            # pattern2 is the name of files to regenerate, other than ads
            # pattern2 = self.data_dir + project + flight + filetype + '.' + fileext
            datalist = glob.glob(pattern)

        if (datalist.__len__() == 1):
            # Found a single file of the type we are looking for
            # [eg ads or lrt or nc, etc.
            # Find out if user wants to reprocess the file?
            datafile = datalist[0]  # Return name of file that was found
        elif datalist.__len__() == 0:
            # Did not find any files with the extension we are looking for
            message = "No files found matching form: " + pattern
            self.logger.info(message)
            print(message)
            if fileext == 'ads':
                # If we can't find an ads file, then there is nothing to do.
                message = "Aborting..."
                self.logger.info(message)
                print(message)
                sys.exit(0)
            else:
                # Any other files that can't be found can be regenerated
                if flag:
                    message = "We are scheduled to process all is good."
                    self.logger.info(message)
                    print(message)
                    datafile = pattern
                else:
                    # but if the file is not marked to be regenerated in the
                    # fieldProc_setup.py file, then we have a probem.
                    message = "We have an nc file but not "+fileext+" file.... " +\
                          "aborting..."
                    self.logger.info(message)
                    print(message)
                    sys.exit(0)
        else:
            # Found multiple files that match the type we are looking for.
            # Step through the files and let the user decide
            # which is the one we should work with
            message = "More than one " + fileext + " file found."
            self.logger.info(message)
            print(message)
            datafile = self.step_through_files(datalist, fileext,
                                               reprocess)

        if datafile == '':
            # If after all this we haven't identified a file, abort processing.
            message = "No " + datafile + " file identified! Aborting..."
            self.logger.info(message)
            print(message)
            sys.exit(0)

        return(flag, datafile)

    def step_through_files(self, datalist, fileext, reprocess):
        """
        Handle multiple files of a given type for a single flight

        Input:
            datalist - list of files of the same type
            fileext - file type extesion, just used for user messages
        Return: File from list selected by user
        """
        datafile = ''
        if reprocess is True:
            message = "Stepping through files, please select the right one."
            self.logger.info(message)
            print(message)
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
            # Not processing so just return the first file,
            # which is all that we need to successfully set off shipping
            datafile = datalist[0]
            message = 'Ship is set to True so no need to choose ' + fileext +\
                  'to process.'
            self.logger.info(message)
            print(message)
        return(datafile)

    def process_netCDF(self, rawfile, ncfile, pr, config_ext, proj_dir, flight, project, flags):
        """"
        Run nimbus to create a .nc file (LRT, HRT, or SRT)
        """
        # If there is a setup file for this flight in proj_dir/Production
        # use that. If not, create one.
        nimConfFile = proj_dir+"Production/setup_"+flight+config_ext

        if not os.path.exists(nimConfFile):
            cf = open(nimConfFile, 'w')
            sdir, sfilename = os.path.split(rawfile)
            line = "if=${RAW_DATA_DIR}/" + project + "/" + sfilename + '\n'
            cf.write(str(line))
            sdir, sfilename = os.path.split(ncfile)
            line = "of=${DATA_DIR}/" + project + "/" + project + flight + config_ext + '.nc\n'
            cf.write(str(line))
            line = "pr=" + pr + '\n'
            cf.write(str(line))
            cf.close()

        # execute nimbus in batch mode using the config file
        command = "/opt/local/bin/nimbus" + flags + nimConfFile
        message = "about to execute nimbus I hope: " + command
        self.logger.info(message)
        print(message)
        res = os.system(command)
        message = '\nresult of nimbus call = '+str(res)
        self.logger.info(message)
        print(message)
        return(True)
        return(rawfile)

    def process_threeVCPI(self, aircraft, project, flight,
                          twods_raw_dir, oapfile_dir):
        """
        Process 3vCPI
        """
        message = "\n\n *****************  3VCPI **************************\n"
        self.logger.info(message)
        print(message)
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
                message = "cat 3vcPIfiles:"+command
                self.logger.info(message)
                print(message)
                os.system(command)

            command = translate2ds + '-project ' + project
            + ' -flight ' + flight + ' -platform ' + aircraft
            + ' -sn SPEC001 -f ' + catted_file + ' -o .'
            message = ' 3v-cpi command:' + command
            self.logger.info(message)
            print(message)
            os.system(command)

            # move 2DS file to the RAF naming convention and location
            if not os.path.isdir(oapfile_dir):
                try:
                    os.mkdir(oapfile_dir)
                except Exception as e:
                    self.logger.error(e)
                    print(e)              
                    message = "\nERROR: Couldnt make oapfile dir:"
                    + oapfile_dir
                    message = message + "\nskipping 2d file gen/placement\n"
                    self.print_message(message)
                    mkdir_fail = True
            if not mkdir_fail:
                twod_dir, fb_filename = os.path.split(first_base_file)
                # Pull out of base{datetime}.2d
                datetime = fb_filename.split('.')[0].split('e')[1]
                command = 'mv ' + catted_2d_file + ' ' + oapfile_dir + '20' + datetime + '_' + flight + '.2d'
                message = ' mv command: ' + command
                self.logger.info(message)
                print(message)
                os.system(command)
                threevcpi2d_file = oapfile_dir + '20' + datetime + '_' + flight + '.2d'

                # Merge 3v-cpi data into netCDF file
                command = 'process2d ' + threevcpi2d_file + ' -o ' + ncfile
                message = "3v-cpi merge cmd: " + command
                self.logger.info(message)
                print(message)
                if os.system(command) == 0:
                    proc_3vcpi_files = 'Yes'

    def reorder_nc(self, ncfile):
        """
        Reorder netcdf file
        """
        command = "nccopy -u " + ncfile + " tmp.nc"
        message = "about to execute : " + command
        self.logger.info(message)
        print(message)
        os.system(command)

        command = "/bin/mv tmp.nc " + ncfile
        message = "about to execute : " + command
        self.logger.info(message)
        print(message)
        if os.system(command) == 0:
            proc_nc_file = 'Yes'
        else:
            message = "ERROR: ncreorder failed, but NetCDF should be ok\n"
            self.print_message(message)
            proc_nc_file = 'Yes'
        return(proc_nc_file)

    def zip_file(self, filename, datadir):
        """
        Create Zip file
        """
        os.chdir(datadir)
        command = "zip " + filename + ".zip " + filename
        if os.system(command) != 0:
            message = "\nERROR!: Zipping up " + filename + " with command:\n  "
            message = message + command
            self.print_message(message)

    def getProject(self):
        return(self.read_env('PROJECT'))

    def getDataDir(self):
        return(self.read_env('DATA_DIR'))

    def getRawDir(self):
        return(self.read_env('RAW_DATA_DIR'))

    def getProjDir(self):
        return(self.read_env('PROJ_DIR'))

    def setup(self, aircraft, project, raw_dir):
        """
        Create objects for multiple processing inputs
        """
        if aircraft == "GV_N677F":
            raircraft = 'aircraft.NSF_NCAR_GV.'
        elif aircraft == "C130_N130AR":
            raircraft = 'aircraft.NSF_NCAR_C-130.'
        else:
            message = "Unknown aircraft " + aircraft + " Update code\n"
            self.logger.info(message)
            print(message)
            sys.exit(1)

        message = "Processing " + project + " from " + aircraft +\
              ". If incorrect, edit ~/ads3_environment."
        self.logger.info(message)
        print(message)
        message = "Expecting to find .ads files in " + raw_dir + "."
        self.logger.info(message)
        print(message)
        return raircraft

    def process(self, file_ext, data_dir, flight, filename, raw_dir, status, project):
        '''
        Beginning of Processing ##############################
        Get the netCDF, kml, icartt, IWG1 and raw ADS files for working with ##

        First the LRT netCDF. We use this to determine if code has been run before
        because we ALWAYS generate a LRT data file for every flight.
        Determine if we are in process, reprocess, or ship mode.
        '''
        (process, reprocess, self.filename['LRT']) = self.find_lrt_netcdf(self.file_ext['LRT'], self.flight, self.data_dir, self.file_prefix)
        # Next get the ADS file so we can determine the flight date. This is needed
        # in order to identify the correct ICARTT file, since ICARTT files follow the
        # NASA naming convention and don't use our flight numbering system.
        (reprocess, filename['ADS']) = \
            self.find_file(self.inst_dir['ADS'], self.flight, self.project, self.file_type['ADS'],
                           self.file_ext['ADS'], process, reprocess, self.file_prefix)

        # Get the flight date from the ADS filename
        file_name = filename["ADS"].split(raw_dir)[1]
        self.date = file_name[:15]
        self.date = re.sub('_', '', self.date)

        # Now everthing else (skip LRT) using the NCAR/EOL/RAF flight number to
        # identify the file associated with the current flight.
        for key in file_ext:
            if (key == "HRT") or (key == "SRT"):

                (reprocess, filename[key]) = \
                    self.find_file(self.inst_dir[key], self.flight, self.project, self.file_type[key],
                                   self.file_ext[key], process, reprocess, self.date[0:8])
        if process:
            for key in file_ext:

                # Process the ads data to desired netCDF frequencies
                if (key == "LRT"):
                    self.flags = " -b "
                    res = self.process_netCDF(self.filename["ADS"], self.filename[key], self.rate[key], self.config_ext[key], self.proj_dir, self.flight, self.project, self.flags)
                    if res:
                        self.status[key]["proc"] = self.reorder_nc(self.filename[key])
                    else:
                        self.status[key]["proc"] = False

                # Process the ads data to desired netCDF frequencies
                if (key == "HRT"):
                    self.flags = " -b "
                    res = self.process_netCDF(self.filename["ADS"], self.ncfile, self.rate[key], self.config_ext[key], self.proj_dir, self.flight, self.project, self.flags)
                    if res:
                        self.status[key]["proc"] = self.reorder_nc(self.ncfile)
                    else:
                        self.status[key]["proc"] = False

                # Process the ads data to desired netCDF frequencies
                if (key == "SRT"):
                    self.flags = " -b "
                    res = self.process_netCDF(self.filename["ADS"], self.ncfile, self.rate[key], self.config_ext[key], self.proj_dir, self.flight, self.project, self.flags)
                    if res:
                        self.status[key]["proc"] = self.reorder_nc(self.ncfile)
                    else:
                        self.status[key]["proc"] = False

                # Generate IWG1 file from LRT, if requested
                if (key == "IWG1"):
                    command = "nc2iwg1 "+self.filename["LRT"]+" -o "+data_dir + project + flight + '.' + file_ext["IWG1"]
                    message = "about to execute : "+command
                    self.logger.info(message)
                    print(message)
                    if os.system(command) == 0:
                        self.status[key]["proc"] = 'Yes'

                # Generate ICARTT file from LRT, if requested
                if (key == "ICARTT"):
                    command = "nc2asc -i " + filename["LRT"] + " -o " + self.data_dir + "tempfile.ict -b " + self.nc2ascBatch
                    message = "about to execute : " + command
                    self.logger.info(message)
                    print(message)
                    if os.system(command) == 0:
                        status[key]["proc"] = 'Yes'

                # Convert SPEC file form to oap file form
                if (key == "threeVCPI"):
                    self.process_threeVCPI(aircraft, project, flight, self.inst_dir["twods"], self.inst_dir["oap"])

                # Fast 2D data, extract first, then process.
                if (key == "PMS2D"):
                    self.ensure_dir(self.inst_dir["PMS2D"] + 'PMS2D')
                    file_name = filename["ADS"].split(raw_dir)[1]
                    fileelts = file_name.split('.')
                    filename["PMS2D"] = self.inst_dir["PMS2D"] + 'PMS2D/' + fileelts[0] + '.2d'

                    if not os.path.exists(filename["PMS2D"]):
                        # General form of extract2d from RAW_DATA_DIR is:
                        # Extract2d PMS2D/output.2d input.ads
                        command = 'extract2d '+filename["PMS2D"]+' '+filename["ADS"]
                        message = '\nExtracting 2D from ads:'+command+'\n'
                        self.logger.info(message)
                        print(message)
                        os.system(command)

                    if os.path.exists(filename["PMS2D"]):
                        # Process 2D data into netCDF file.  General form is:
                        # Process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
                        command = 'process2d '+filename["PMS2D"]+' -o '+filename["LRT"]
                        mesage = '2D merge command: '+command

                        if os.system(command) == 0:
                            status["PMS2D"]["proc"] = 'Yes'
                            # status["PMS2D"]["ship"] = 'Yes'
                            # status["PMS2D"]["stor"] = 'Yes'

        # Now everthing else (skip LRT) using the NCAR/EOL/RAF flight number to
        # identify the file associated with the current flight.
        for key in file_ext:
            if (key == "LRT") or (key == "ADS"):
                next
            elif (key == "PMS2D"):
                (reprocess, filename[key]) = \
                    self.find_file(self.inst_dir[key] + "PMS2D/", self.flight,
                                   self.project, self.file_type[key],
                                   self.file_ext[key], process, reprocess,
                                   self.date[0:8])
            else:
                (reprocess, filename[key]) = \
                    self.find_file(self.inst_dir[key], self.flight, self.project, self.file_type[key],
                                   self.file_ext[key], process, reprocess, self.date[0:8])

        # Generate the QAtools_notebook HTML and copy to desktop
        # This should be inside the "if process" block so it doesn't get rerun when
        # user selects ship, but still need to define filename even if not processing...
        # logic needs work.
        filename["QAtools_output"] = project+flight+".html"
        if QA_notebook:
            os.chdir("/home/local/aircraft_QAtools_notebook/")
            command = "./auto_export.py --project "+project+" --flight "+flight
            message = "about to execute : "+command
            self.logger.info(message)
            print(message)
            os.system(command)

            command = "cp -p "+filename["QAtools_output"] + " /home/ads/Desktop"
            message = "copying QAQC html to desktop"
            self.logger.info(message)
            print(message)
            os.system(command)

    def setup_shipping(self, file_ext, filename, process, reprocess, status):
        """
        Beginning of Shipping
        """
        if NAS_permanent_mount is False:
            # Mount NAS
            command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
            message = '\r\nMounting nas: ' + command
            self.logger.info(message)
            print(message)

            os.system(command)

        # Put copies of files to local store
        # in dirs to sync to ftp site in Boulder...
        self.nas_sync_dir = nas_mnt_pt+'/FTP_sync/EOL_data/RAF_data/'
        # and in dirs for local use...
        self.nas_data_dir = nas_mnt_pt+'/EOL_data/RAF_data/'

        message = ""
        self.logger.info(message)
        print(message)

        message = "*************** Copy files to NAS scratch area ***************"
        self.logger.info(message)
        print(message)

        for key in file_ext:
            self.ensure_dir(self.nas_data_dir)
            if (key == "ADS"):
                message = 'Copying ' + filename[key] + ' to ' + self.nas_data_dir + '/ADS'
                self.logger.info(message)
                print(message)
                status[key]["stor"] = self.rsync_file(filename[key], self.nas_data_dir + '/ADS')
            elif (key == "PMS2D"):
                message = 'Copying ' + filename[key] + ' to ' + self.nas_data_dir + '/PMS2D/'
                self.logger.info(message)
                print(message)
                status[key]["stor"] = self.rsync_file(filename[key], self.nas_data_dir + '/PMS2D/')
            else:
                message = 'Copying ' + filename[key] + ' to ' + self.nas_data_dir + '/' + key
                self.logger.info(message)
                print(message)
                status[key]["stor"] = self.rsync_file(filename[key], self.nas_data_dir + '/' + key)

        #if catalog:
        #    self.ensure_dir(self.nas_data_dir + "/qc")
        #    message = 'Copying QC plots to ' + self.nas_data_dir + "/qc"
        #    self.logger.info(message)
        #    print(message)
        #    status[key]["stor"] = self.rsync_file(rstudio_dir + "/QAtools/" + raircraft + date + ".RAF_QC_plots.pdf", self.nas_data_dir + "/qc")

        return self.nas_data_dir, self.nas_sync_dir

    def setup_email(self, data_dir, email):
        """
        Set up email
        """
        emailfilename = 'email.addr.txt'
        emailfile = data_dir+emailfilename
        command = 'rm '+emailfile
        os.system(command)
        fo = open(emailfile, 'w+')
        fo.write(email+'\n')
        fo.close()

    def setup_zip(self, file_ext, data_dir, filename, inst_dir):
        """
        ZIP up the files as per expectations back home
        this only affects non-ads files
        """
        for key in file_ext:
            if (key == "ADS"):
                message = "Raw .ads file found but not zipping, if zip_ads is set, will bzip .ads file next."
                self.logger.info(message)
                print(message)
            elif (key == "PMS2D"):
                message = "Raw .2d file found but not zipping."
                self.logger.info(message)
                print(message)
            else:
                data_dir, file_name = os.path.split(filename[key])
                message = key + " filename = " + file_name
                self.logger.info(message)
                print(message)
                message = "data_dir = " + data_dir
                self.logger.info(message)
                print(message)
                self.zip_file(file_name, inst_dir[key])

    def GDrive(self, data_dir, raw_dir, status, file_ext, inst_dir, filename, rclone_staging_dir):
        '''No NAS this project, so put files to Google Drive. Put
        zipped files if they exist.
        '''
        print('\nPutting files to rclone staging location for shipment to Google Drive:\n')

        # Keep this set to False unless you have time / bandwidth to ship all
        # ads files.
        if ship_all_ADS is True:
            message = 'Starting rsync process for all available .ads files'
            self.logger.info(message)
            print(message)
            for rawfilename in os.listdir(inst_dir['ADS']):
                if rawfilename.endswith('.ads'):
                    try:
                        os.chdir(inst_dir['ADS'])
                        os.system('rsync -u *.ads ' + rclone_staging_dir + 'ADS')
                        status["ADS"]["stor"] = 'Yes-GDrive-staging'
                        message = rawfilename + ' rsync successful!'
                        self.logger.info(message)
                        print(message)
                    except Exception as e:
                        message = rawfilename + ' not copied to local staging'
                        self.logger.info(message)
                        print(message)
                        self.logger.error(e)
                        print(e)
                    try:
                        os.system('rclone copy ' + rclone_staging_dir + '/ADS' + ' gdrive_eolfield:/' + os.environ['PROJECT'] + '/EOL_data/RAF_data/ADS --ignore-existing')
                        status["ADS"]["ship"] = 'Yes-GDrive'
                        message = rawfilename + ' rclone successful!'
                        self.logger.info(message)
                        print(message)
                    except:
                        message = rawfilename + ' not rcloned to Google Drive'
                        self.logger.info(message)
                        print(message)
                        self.logger.error(e)
                        print(e)
                else:
                    pass
        else:
            # Loop through requested file extensions to be copied to GDrive
            for key in file_ext:
                print('\n' + key + '\n')

                if ship_ADS is False and key == 'ADS':
                    # Skip ads if requested in fieldProc_setup.py
                    continue
                else:
                    # For all requested extensions, confirm local dir where
                    # data file is located exists
                    try:
                        print("Data dir is " + inst_dir[key])
                        os.path.exists(inst_dir[key])
                    except Exception as e:
                        print('Data dir ' + inst_dir[key] +  ' does not exist')
                        print(e)
                        self.logger.error(e)
                        continue

                if filename[key] != '':
                    print('Instrument file is ' + filename[key])
                    # Get instrument filename; used for error reporting
                    data_dir, file_name = os.path.split(filename[key])

                    # For all requested extensions, confirm there is an
                    # instrument-specific dir within the rclone_staging_dir
                    print("GDrive rclone staging dir for instrument is " +
                          rclone_staging_dir + key)
                    if not os.path.exists(rclone_staging_dir + key):
                        e = 'Instrument dir ' + rclone_staging_dir + key + \
                              ' does not exist'
                        print(e)
                        self.logger.error(e)
                        # Attempt to create needed dir
                        print('Attempt to create dir ' + rclone_staging_dir +
                              key)
                        try:
                            pass
                            os.system('mkdir ' + rclone_staging_dir + key)
                        except Exception as e:
                            print('Make dir ' + rclone_staging_dir + key +
                                  ' failed')
                            print(e)
                            self.logger.error(e)
                            continue
                        # Confirm dir exists again
                        if not os.path.exists(rclone_staging_dir + key):
                            e = rclone_staging_dir + '/' + key + \
                                  ' still does not exist. Cannot stage ' + \
                                  key + ' data'
                            print(e)
                            self.logger.error(e)
                            continue

                    # Copy files to staging area and match desired rclone structure
                    try:
                        print('rsync -u ' + filename[key] + ' ' + rclone_staging_dir + key)
                        # os.system doesn't throw an error so this try/except
                        # never fails even if rsync fails. Need to use subprocess.Popen()
                        # This is true every place os.system is used in a try/except
                        os.system('rsync -u ' + filename[key] + ' ' + rclone_staging_dir + key)
                        status[key]["stor"] = 'Yes-GDrive-staging'
                        print(datetime.datetime.now().time())
                        print('Finished rsyncing ' + key + ' file to staging location')
                        print('')

                    except Exception as e:
                        print('Error rsyncing data file to staging location ' + file_name)
                        print(e)
                        self.logger.error(e)
                        continue

                    # Use rclone to sync files to GDrive. Could rclone all at
                    # once, but chose to sync a file at a time so can report
                    # status.
                    try:
                        print('rclone copy ' + rclone_staging_dir + key +
                              ' gdrive_eolfield:' + os.environ['PROJECT'] +
                              '/EOL_data/RAF_data/' + key + ' --ignore-existing --low-level-retries 20')
                        os.system('rclone copy ' + rclone_staging_dir + key +
                                  ' gdrive_eolfield:' + os.environ['PROJECT'] +
                                  '/EOL_data/RAF_data/' + key +
                                  ' --ignore-existing --low-level-retries 20')
                        status[key]["ship"] = 'Yes-GDrive'
                        print(datetime.datetime.now().time())
                        print('Finished rclone to GDrive for ' + file_name)
                        print('')

                    except Exception as e:
                        print('Error with rclone process for ' + file_name +
                              '. File not copied to GDrive')
                        print(e)
                        self.logger.error(e)
                        continue

            ##Rsync the QAtools html to the google drive
            if QA_notebook:
                key = 'QAtools_output'
                print('\n' + key + '\n')
                print('Notebook file is '+ filename[key])
                print("GDrive rclone staging dir for QATools is " +
                      rclone_staging_dir + key)
                if not os.path.exists(rclone_staging_dir + key):
                    e = 'Output dir ' + rclone_staging_dir + key + ' does not exist'
                    print(e)
                    self.logger.error(e)
                    print('Attempt to create dir ' + rclone_staging_dir +
                      key)
                    try:
                    # Attempt to create needed dir
                        os.mkdir(rclone_staging_dir + key)
                    except Exception as e:
                        print('Make dir ' + rclone_staging_dir + key + ' failed')
                        print(e)
                        self.logger.error(e)
                        pass
                try:
                    print('rsync -u /home/local/aircraft_QAtools_notebook/' +
                           filename[key] + ' ' + rclone_staging_dir + key)
                    os.system('rsync -u /home/local/aircraft_QAtools_notebook/' +
                               filename[key] + ' ' + rclone_staging_dir + key)
                    print(datetime.datetime.now().time())
                    print('Finished rsyncing ' + key + ' file to staging location')
                    print('')
                except:
                    print('Error with rsync process for ' + key +
                          '. File not copied to staging location')
                    pass
                try:
                    print('rclone copy ' + rclone_staging_dir + key + '/' +
                          filename[key] +
                          ' gdrive_eolfield:' + os.environ['PROJECT'] +
                          '/EOL_data/RAF_data/' + key + ' --ignore-existing --low-level-retries 20')
                    os.system('rclone copy ' + rclone_staging_dir + key + '/' +
                              filename[key] +
                              ' gdrive_eolfield:' + os.environ['PROJECT'] +
                              '/EOL_data/RAF_data/' + key +
                              ' --ignore-existing --low-level-retries 20')
                except Exception as e:
                    print('Error with rclone process for ' + key +
                          '. File not copied to GDrive')
                    print(e)
                    self.logger.error(e)

                # Hack to handle the pdf
                pdffilename = re.sub('html', 'pdf', filename[key])
                os.system('rsync -u /home/local/aircraft_QAtools_notebook/' +
                          pdffilename + ' ' + rclone_staging_dir + key)
                os.system('rclone copy ' + rclone_staging_dir + key + '/' +
                          pdffilename +
                          ' gdrive_eolfield:' + os.environ['PROJECT'] +
                          '/EOL_data/RAF_data/' + key +
                          ' --ignore-existing --low-level-retries 20')

    def setup_FTP(self, data_dir, raw_dir, status, file_ext, inst_dir, filename):
        '''No NAS this project, so put files to EOL server. Put
        zipped files if they exist.
        '''
        try:
            message = 'Opening FTP connection to: ' + ftp_site
            self.logger.info(message)
            print(message)
            ftp = ftplib.FTP(ftp_site)
            ftp.login(user, password)
            print('')

        except ftplib.all_errors as e:
            message = 'Error connecting to FTP site ' + ftp_site
            self.logger.error(message)
            print(message)
            self.logger.error(e)
            print(e)
            ftp.quit()

        print('Putting files to FTP site:')
        print('')

        # When ftping, put PMS2D file in PMS2D subdir
        inst_dir['PMS2D'] = inst_dir['PMS2D'] + 'PMS2D/'

        # If set in config file script will FTP all ads in rdat
        # Keep this set to False unless you have time / bandwidth
        if ship_all_ADS is True:
            message = 'Starting ftp process for all available .ads files'
            self.logger.info(message)
            print(message)
            for rawfilename in os.listdir(inst_dir['ADS']):
                if rawfilename.endswith('.ads'):
                    try:
                        os.chdir(inst_dir['ADS'])
                        ftp.cwd('/' + ftp_data_dir + '/ADS')
                        ftp.storbinary('STOR ' + rawfilename, open(rawfilename, 'rb'))
                        status["ADS"]["stor"] = 'Yes-FTP'
                        message = rawfilename + ' ftp successful!'
                        self.logger.info(message)
                        print(message)
                    except Exception as e:
                        message = rawfilename + ' not sent'
                        self.logger.info(message)
                        print(message)
                        self.logger.error(e)
                        print(e)

        else:
            # Loop through requested file extensions to be copied to ftp area
            for key in file_ext:
                print('\n' + key + '\n')

                if ship_ADS is False and key == 'ADS':
                    # Skip ads if requested in fieldProc_setup.py
                    continue
                else:
                    try:
                        os.chdir(inst_dir[key])
                        print('Attempt to change to local dir ' + inst_dir[key])
                    except ftplib.all_errors as e:
                        print('Could not change to local dir ' + inst_dir[key])
                        print(e)
                        self.logger.error(e)
                        continue

                if filename[key] != '':
                    print('Instrument file is ' + filename[key])
                    # Get instrument filename; used for error reporting
                    data_dir, file_name = os.path.split(filename[key])

                    try:
                        print('Attempt to change to ftp dir /' + ftp_data_dir + '/' + key)
                        ftp.cwd('/' + ftp_data_dir + '/' + key)
                    except ftplib.all_errors as e:
                        print('Could not change to dir ' + ftp_data_dir + '/' + key)
                        print(e)
                        # Attempt to create needed dir
                        print('Attempt to create dir /' + ftp_data_dir + '/' + key)
                        try:
                            ftp.mkd('/' + ftp_data_dir + '/' + key)
                        except Exception as e:
                            print('Make dir /' + ftp_data_dir + '/' + key + ' failed')
                            print(e)
                            self.logger.error(e)
                            continue
                        # Try to change to dir again
                        try:
                            ftp.cwd('/' + ftp_data_dir + '/' + key)
                        except Exception as e:
                            print('Change dir to ' + ftp_data_dir + '/' + key + ' failed')
                            print(e)
                            self.logger.error(e)
                            continue

                if file_name in ftp.nlst():
                    print('File ' + file_name + ' already exists on ftp server.')
                    print('File will not be transfered to ftp site')
                    print('To force transfer, delete file from ftp site and rerun in Ship mode')
                    continue

                # Transfer files to FTP site
                try:
                    print('Transferring file...')
                    file = open(file_name, 'rb')
                    print(ftp.storbinary('STOR ' + file_name, file))
                    file.close()
                    status[key]["stor"] = 'Yes-FTP'

                    print(datetime.datetime.now().time())
                    print('Finished putting data file')
                    print('')

                except ftplib.all_errors as e:
                    print('Error writing ' + file_name + ' to ' + ftp_site + ':/' + ftp_data_dir + '/' + key)
                    print(e)
                    self.logger.error(e)
                    continue

        ftp.quit()

        # Revert PMS2D ftp special case
        inst_dir['PMS2D'] = re.sub('PMS2D/', '',inst_dir['PMS2D'])
        print("After FTP: " + inst_dir['PMS2D'])


    def setup_NAS(self, process, reprocess, file_ext, inst_dir, status, flight, project, email, final_message, filename, nas_sync_dir, nas_data_dir):
        # Put file onto NAS for BTSyncing back home.
        print("")
        print("***** Copy files to NAS sync area for transfer back home *****")

        if reprocess or (not reprocess and not process):
            final_message = final_message + '\n***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'
            final_message = final_message + 'Reprocessing so assume ADS already shipped during first processing\n'
            final_message = final_message + 'If this is not the case, run\n\n'
            final_message = final_message + '"cp /home/data/Raw_Data/' + project + '/*' + flight + '.ads ' + nas_sync_dir + '/ADS"\n\n'
            final_message = final_message + '"cp /home/data/Raw_Data/' + project + '/*' + flight + '.ads ' + nas_data_dir + '/ADS"\n\n'
            final_message = final_message + 'when this script is complete\n\n'
            final_message = final_message + '***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'

        if zip_ADS:
            # Now only zip up the ADS file, if requested
            raw_dir, rawfilename = os.path.split(filename["ADS"])
            print("zipping " + rawfilename)
            zip_raw_file = zip_dir + rawfilename + '.bz2'
            print("rawfilename = " + zip_raw_file)
            os.chdir(raw_dir)
            # if not os.path.exists(zip_raw_file):
            print("Compressing ADS file with command:")
            command = "bzip2 -kc " + rawfilename + " > " + zip_raw_file
            print(command)
            os.system(command)
            print("")
        else:
            print('.ads file not being zipped due to preference')

        # mount the NAS and put files to it
        if NAS_permanent_mount is False:
            # Mount NAS
            command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
            print('\r\nMounting nas: '+command)
            os.system(command)

        for key in file_ext:
            os.chdir(inst_dir[key])
            if (key == "ADS"):
                if ship_ADS is True:
                    if zip_ADS is True:
                        print('Copying ' + zip_raw_file + ' file to ' + nas_sync_dir + '/ADS')
                        self.rsync_file(zip_raw_file, nas_sync_dir + '/ADS')
                        print('Done')
                    else:
                        print('Copying ' + filename[key] + ' file to ' + nas_sync_dir + '/ADS')
                        status[key]["ship"] = self.rsync_file(filename[key], nas_sync_dir + '/' + key)
                        print('Done')
                else:
                    pass
            elif (key == "PMS2D"):
                print('Copying ' + filename[key] + ' file to ' + nas_sync_dir + '/PMS2D')
                status[key]["ship"] = self.rsync_file(filename[key], nas_sync_dir + '/PMS2D')
                print('Done')
            else:
                if sendzipped is True:
                    print('Copying ' + filename[key] + '.zip file to ' + nas_sync_dir + '/' + key)
                    status[key]["ship"] = self.rsync_file(filename[key] + '.zip', nas_sync_dir + '/' + key)
                    print('Done')
                else:
                    print('Copying ' + filename[key] + ' file to ' + nas_sync_dir + '/' + key)
                    status[key]["ship"] = self.rsync_file(filename[key], nas_sync_dir + '/' + key)
                    print('Done')

    def report(self, final_message, status, project, flight, email, file_ext):
        final_message = final_message + '\nREPORT on shipping of files. \n\n'
        final_message = final_message + 'File Type\tStor\tShip\n'

        for key in file_ext:
            final_message = final_message + key + '\t\t' + str(status[key]["stor"]) + '\t' + str(status[key]["ship"]) + '\n'

        final_message = final_message + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"

        print(final_message)
        msg = MIMEText(final_message)
        msg['Subject'] = 'Process & Push message for:' + project + '  flight:' + flight
        msg['From'] = 'ads@groundstation'
        msg['To'] = email

        s = smtplib.SMTP('localhost')
        s.sendmail('ads@groundstation', email, msg.as_string())
        s.quit()

        print("\r\nSuccessful completion. Close window to exit.")

def main():

    # instantiate FieldData class
    fielddata = FieldData()

    # process data
    fielddata.process(fielddata.file_ext, fielddata.data_dir, fielddata.flight, fielddata.filename, fielddata.raw_dir, fielddata.status, fielddata.project)

    # set up the email functionality
    fielddata.setup_email(fielddata.data_dir, fielddata.email)

    # Zip files only if set to True
    if sendzipped:
        fieldata.setup_zip(fielddata.file_ext, fielddata.data_dir, fielddata.filename, fielddata.inst_dir)

    # Call FTP function if the FTP flag is set to True
    if FTP:
        fielddata.setup_FTP(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename)

    # Call GDrive function if the GDRIVE flag is set to True
    if GDRIVE:
        fielddata.GDrive(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename, fielddata.rclone_staging_dir)

    # Call NAS functions if the NAS flag is set to True
    if NAS:
        fielddata.setup_shipping(fielddata.file_ext, fielddata.filename, process, reprocess, fielddata.status)
        fielddata.setup_NAS(process, reprocess, fielddata.file_ext, fielddata.inst_dir, fielddata.status, fielddata.flight, fielddata.project, fielddata.email, fielddata.final_message, fielddata.filename, fielddata.nas_sync_dir, fielddata.nas_data_dir)

    # Call the report function which appends the final message for emailing 
    fielddata.report(fielddata.final_message, fielddata.status, fielddata.project, fielddata.flight, fielddata.email, fielddata.file_ext)


if __name__ == '__main__':

    main()

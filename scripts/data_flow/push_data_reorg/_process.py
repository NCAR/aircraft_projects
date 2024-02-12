from _repetition import *
import os
import re


def process_netCDF(self, rawfile, ncfile, pr, config_ext, proj_dir, flight, project, flags):
    """"
    Run nimbus to create a .nc file (LRT, HRT, or SRT)
    """
    # If there is a setup file for this flight in proj_dir/Production
    # use that. If not, create one.
    nimConfFile = proj_dir + "Production/setup_" + flight + config_ext

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
    command = "/usr/local/bin/nimbus" + flags + nimConfFile
    message = "about to execute nimbus I hope: " + command
    log_and_print(message)
    res = os.system(command)
    message = '\nresult of nimbus call = ' + str(res)
    log_and_print(message)
    return True

def process_threeVCPI(self, aircraft, project, flight,
                      twods_raw_dir, oapfile_dir):
    """
    Process 3vCPI
    """
    message = "\n\n *****************  3VCPI **************************\n"
    log_and_print(message)
    mkdir_fail = False
    first_base_file = ''
    catted_file = 'base_' + flight + 'all.2DSCPI'
    catted_2d_file = 'base_' + flight + 'all.2d'
    os.chdir(twods_raw_dir)
    if os.path.isfile(catted_file):
        os.remove(catted_file)
    file_list = glob.glob(twods_raw_dir + 'base*2DSCPI')
    if len(file_list) > 0:
        os.chdir(twods_raw_dir)
        filenum = 1
        for file in file_list:
            if filenum == 1:
                first_base_file = file
            command = 'cat ' + file + ' >> ' + catted_file
            message = "cat 3vcPIfiles:" + command
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
                log_and_print(e,'error')
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
            log_and_print(message)
            os.system(command)
            threevcpi2d_file = oapfile_dir + '20' + datetime + '_' + flight + '.2d'

            # Merge 3v-cpi data into netCDF file
            command = 'process2d ' + threevcpi2d_file + ' -o ' + ncfile
            message = "3v-cpi merge cmd: " + command
            log_and_print(message)
            if os.system(command) == 0:
                proc_3vcpi_files = 'Yes'



def process(self, file_ext, data_dir, flight, filename, raw_dir, status, project):
    '''
    Beginning of Processing ##############################
    Get the netCDF, kml, icartt, IWG1 and raw ADS files for working with ##

    First the LRT netCDF. We use this to determine if code has been run before
    because we ALWAYS generate a LRT data file for every flight.
    Determine if we are in process, reprocess, or ship mode.
    '''
    (process, reprocess, self.filename['LRT']) = self.find_lrt_netcdf(self.file_ext['LRT'], self.flight, self.data_dir,
                                                                      self.file_prefix)
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
                res = self.process_netCDF(self.filename["ADS"], self.filename[key], self.rate[key],
                                          self.config_ext[key], self.proj_dir, self.flight, self.project, self.flags)
                if res:
                    self.status[key]["proc"] = self.reorder_nc(self.filename[key])
                else:
                    self.status[key]["proc"] = False

            # Process the ads data to desired netCDF frequencies
            if (key == "HRT"):
                self.flags = " -b "
                res = self.process_netCDF(self.filename["ADS"], self.ncfile, self.rate[key], self.config_ext[key],
                                          self.proj_dir, self.flight, self.project, self.flags)
                if res:
                    self.status[key]["proc"] = self.reorder_nc(self.ncfile)
                else:
                    self.status[key]["proc"] = False

            # Process the ads data to desired netCDF frequencies
            if (key == "SRT"):
                self.flags = " -b "
                res = self.process_netCDF(self.filename["ADS"], self.ncfile, self.rate[key], self.config_ext[key],
                                          self.proj_dir, self.flight, self.project, self.flags)
                if res:
                    self.status[key]["proc"] = self.reorder_nc(self.ncfile)
                else:
                    self.status[key]["proc"] = False

            # Generate IWG1 file from LRT, if requested
            if (key == "IWG1"):
                command = "nc2iwg1 " + self.filename["LRT"] + " -o " + data_dir + project + flight + '.' + file_ext[
                    "IWG1"]
                message = "about to execute : " + command
                self.logger.info(message)
                print(message)
                if os.system(command) == 0:
                    self.status[key]["proc"] = 'Yes'

            # Generate ICARTT file from LRT, if requested
            if (key == "ICARTT"):
                command = "nc2asc -i " + filename[
                    "LRT"] + " -o " + self.data_dir + "tempfile.ict -b " + self.nc2ascBatch
                message = "about to execute : " + command
                log_and_print(message)
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
                    command = 'extract2d ' + filename["PMS2D"] + ' ' + filename["ADS"]
                    message = '\nExtracting 2D from ads:' + command + '\n'
                    log_and_print(message)
                    os.system(command)

                if os.path.exists(filename["PMS2D"]):
                    # Process 2D data into netCDF file.  General form is:
                    # Process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
                    command = 'process2d ' + filename["PMS2D"] + ' -o ' + filename["LRT"]
                    mesage = '2D merge command: ' + command

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
    if QA_notebook:
        os.chdir("/home/local/aircraft_QAtools_notebook/")
        command = "./auto_export.py --project " + project + " --flight " + flight
        message = "about to execute : " + command
        log_and_print(message)
        os.system(command)

        command = "cp -p " + project + flight + ".html /home/ads/Desktop"
        message = "copying QAQC html to desktop"
        log_and_print(message)
        os.system(command)



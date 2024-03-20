from scripts.data_flow.push_data_reorg._logging import *
import os
import re


def _process_netCDF(self, rawfile, ncfile, pr, config_ext, proj_dir, flight, project, flags):
    """"
    Run nimbus to create a .nc file (LRT, HRT, or SRT)
    """
    # If there is a setup file for this flight in proj_dir/Production
    # use that. If not, create one.
    nimConfFile = f"{proj_dir}Production/setup_{flight}{config_ext}"

    if not os.path.exists(nimConfFile):
        with open(nimConfFile, 'w') as cf:
            sdir, sfilename = os.path.split(rawfile)
            line = "if=${RAW_DATA_DIR}/" + project + "/" + sfilename + '\n'
            cf.write(str(line))
            sdir, sfilename = os.path.split(ncfile)
            line = "of=${DATA_DIR}/" + project + "/" + project + flight + config_ext + '.nc\n'
            cf.write(str(line))
            line = f"pr={pr}" + '\n'
            cf.write(str(line))
    # execute nimbus in batch mode using the config file
    command = f"/usr/local/bin/nimbus{flags}{nimConfFile}"
    message = f"about to execute nimbus I hope: {command}"
    if not run_and_log(command, message):
        log_and_print('\nrNimbus call failed')
        return False

    return True

def _process_threeVCPI(self, aircraft, project, flight,
                    twods_raw_dir, oapfile_dir):
    """
    Process 3vCPI
    """
    message = "\n\n *****************  3VCPI **************************\n"
    log_and_print(message)
    mkdir_fail = False
    first_base_file = ''
    catted_file = f'base_{flight}all.2DSCPI'
    catted_2d_file = f'base_{flight}all.2d'
    os.chdir(twods_raw_dir)
    if os.path.isfile(catted_file):
        os.remove(catted_file)
    file_list = glob.glob(f'{twods_raw_dir}base*2DSCPI')
    if len(file_list) > 0:
        os.chdir(twods_raw_dir)
        filenum = 1
        for file in file_list:
            if filenum == 1:
                first_base_file = file
            command = 'cat ' + file + ' >> ' + catted_file
            message = "cat 3vcPIfiles:" + command
            run_and_log(command,message)

        command = translate2ds + '-project ' + project
        + ' -flight ' + flight + ' -platform ' + aircraft
        + ' -sn SPEC001 -f ' + catted_file + ' -o .'
        message = ' 3v-cpi command:' + command
        run_and_log(command, message)

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
            run_and_log(command, message)
            threevcpi2d_file = oapfile_dir + '20' + datetime + '_' + flight + '.2d'

            # Merge 3v-cpi data into netCDF file
            command = 'process2d ' + threevcpi2d_file + ' -o ' + ncfile
            message = "3v-cpi merge cmd: " + command
            if run_and_log(command, message):
                proc_3vcpi_files = 'Yes'



import os
import subprocess

def process(self, file_ext, data_dir, flight, filename, raw_dir, status, project):
    """Coordinates file processing for the project.

    Args:
        file_ext (dict): Dictionary of file extensions and their processing flags.
        data_dir (str): Base data directory.
        flight (str): Flight designation.
        filename (dict): Dictionary containing filenames for each instrument.
        raw_dir (str): Directory containing raw data files.
        status (dict): Dictionary to track file processing status.
        project (str): Project identifier.
    """

    # LRT netCDF - Determine processing mode
    process, reprocess, filename['LRT'] = self.find_lrt_netcdf(
        self.file_ext['LRT'], flight, data_dir, self.file_prefix
    )

    # ADS - Extract flight date
    reprocess, filename['ADS'] = self.find_file(
        self.inst_dir['ADS'], flight, project, self.file_type['ADS'],
        self.file_ext['ADS'], process, reprocess, self.file_prefix
    )
    self.date = self._extract_date_from_ads_filename(filename['ADS'], raw_dir)

    # Other Instruments (using flight number)
    for key in file_ext:
        if key in ('HRT', 'SRT'): 
            reprocess, filename[key] = self.find_file(
                self.inst_dir[key], flight, project, self.file_type[key],
                self.file_ext[key], process, reprocess, self.date[:8]
            )   

    # Process and Generate Files
    if process: 
        if key in ('LRT', 'HRT', 'SRT'):
            self._process_core_data(file_ext, filename, data_dir, flight, project, self.rate, self.config_ext)
        self._generate_derived_files(data_dir, filename, project, flight, file_ext)
        if (key == "threeVCPI"):
            self.process_threeVCPI(aircraft, project, flight, self.inst_dir["twods"], self.inst_dir["oap"])
        if key in ("ICARTT","IWG1"):
            self._generate_derived_files(data_dir,filename, project, flight, key)
    # Process PMS2D Files
        if key == "PMS2D":
            self._process_pms2d_files(file_ext, filename, data_dir, flight, project)

    # QA Notebook Generation
    if QA_notebook:
        self._generate_qa_notebook(project, flight)


def _extract_date_from_ads_filename(self, filename, raw_dir):
    file_name = filename["ADS"].split(raw_dir)[1]
    self.date = file_name[:15]
    self.date = re.sub('_', '', self.date)

def _process_core_data(self, key, filename, data_dir, flight, project, rates, config_ext):
    # Process the ads data to desired netCDF frequencies

    _ncfile = self.filename[key] if key == 'LRT' else self.ncfile
    self.flags = " -b "
    if res := self.process_netCDF(
        self.filename["ADS"],
        _ncfile,
        self.rate[key],
        self.config_ext[key],
        self.proj_dir,
        self.flight,
        self.project,
        self.flags,
    ):
        self.status[key]["proc"] = self.reorder_nc(_ncfile)
    else:
        self.status[key]["proc"] = False



def _generate_derived_files(self, data_dir, filename, project, flight, key):
        # Generate IWG1 file from LRT, if requested
    command_dict = {'IWG1':"nc2iwg1 " + self.filename["LRT"] + " -o " + data_dir + project + flight + '.' + file_ext["IWG1"],
                    'ICARTT':"nc2asc -i " + filename["LRT"] + " -o " + self.data_dir + "tempfile.ict -b " + self.nc2ascBatch}
    message = f"about to execute : {command_dict[key]}"
    if run_and_log(command_dict[key],message):
        self.status[key]["proc"] = 'Yes'


def _process_pms2d_files(self, key, file_ext, filename, data_dir, flight, project):

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
        message = f'2D merge command: {command}'
        if run_and_log(command, message):
            status["PMS2D"]["proc"] = 'Yes'

def _generate_qa_notebook(self, project, flight):
    os.chdir("/home/local/aircraft_QAtools_notebook/")
    command = f"./auto_export.py --project {project} --flight {flight}"
    run_and_log(command, f"about to execute : {command}")
    command = f"cp -p {project}{flight}.html /home/ads/Desktop"
    run_and_log(command, "copying QAQC html to desktop")
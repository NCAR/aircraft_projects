import _logging
import logging
import os, glob, sys
import re
import _findfiles
import subprocess
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import  translate2ds, QA_notebook, SYNCTHING, syncthing_staging_dir


myLogger = _logging.MyLogger()
class Process:
    """Coordinates file processing for the push_data.
    
    Methods:
    __init__: Initializes the Process class.
    process_core_data: Process the core data for a given key. This calls on the helper methods _process_netCDF and _reorder_nc.
        If _process_netCDF is successful, then the netcdf created is moved with _reorder_nc and the status of the processing is set to 'Yes'
    _process_netCDF: Run nimbus to create a .nc file (LRT, HRT, or SRT) and returns a boolean value based on the success of the execution.
    _reorder_nc: Moves a netcdf file and returns 'Yes' if successful
    extract_date_from_ads_filename(fname, rawdir): Extracts the date from the ADS filename.
    process_threeVCPI: Process 3vCPI using the helper methods _move_merge_threeVCPI.    
    _move_merge_threeVCPI: Moves the catted_2d_file to the specified oapfile_dir with a new filename based on the flight and datetime.
    generate_derived_files: Generates derived files from the LRT file and returns 'Yes' if successful. 
    process_pms2d_files: Process PMS2D files and returns 'Yes' if successful.
    generate_qa_notebook: Generates a QA notebook for the specified project and flight.
    
    
    Class Variables:
    stat: Dictionary to track file processing status.
    nc2ascBatch: Path to the nc2asc batch file.
    """
    
    def __init__(self, file_ext: dict, data_dir: str, flight:str, filename:dict, raw_dir, status, project, aircraft,
                inst_dir, rate, config_ext,file_type,proj_dir,file_prefix):
        
        """Coordinates file processing for the project.

        Args:
            file_ext (dict): Dictionary of file extensions and their processing flags.
            data_dir (str): Base data directory.
            flight (str): Flight designation.
            filename (dict): Dictionary containing filenames for each instrument.
            raw_dir (str): Directory containing raw data files.
            status (dict): Dictionary to track file processing status.
            project (str): Project identifier.
            aircraft (str): Aircraft identifier.
            inst_dir (dict): Dictionary of instrument directories.
            rate (dict): Dictionary of netCDF processing rates.
            config_ext (dict): Dictionary of netCDF configuration extensions.
            file_type (dict): Dictionary of file types.
            proj_dir (str): Project directory.
            file_prefix (str): Project and flight number prefix for filenames
        
        
        """
        ## Assign the dictionary values to the class variable to track the status of the processing
        self.stat = status
        
        self.nc2ascBatch = proj_dir + 'scripts/nc2asc.bat'
        findFiles = _findfiles.FindFiles()
        # LRT netCDF - Determine processing mode
        process, filename['LRT'] = findFiles.find_lrt_netcdf(
            file_ext['LRT'], flight, data_dir, file_prefix
        )
        
        self.ncfile =filename['LRT'] ## Set the default ncfile to the LRT file
        
        # Next get the ADS file so we can determine the flight date. This is needed
        # in order to identify the correct ICARTT file, since ICARTT files follow the
        # NASA naming convention and don't use our flight numbering system.
        process, filename['ADS'],self.PMS2D_ADS = findFiles.find_file(
            inst_dir['ADS'], flight, project, file_type['ADS'],
            file_ext['ADS'], process, process, file_prefix
        )

        # ADS - Extract flight date
        self.extract_date_from_ads_filename(filename['ADS'], raw_dir)

        # Other Instruments (using flight number)
        for key in file_ext:
            if key in ('HRT', 'SRT'): 
                process, filename[key] = findFiles.find_file(
                    inst_dir[key], flight, project, file_type[key],
                    file_ext[key], process, process, self.date[:8]
                )   

        # Process and Generate Files
        if process: 
            for key in file_ext:
                if key in ('LRT', 'HRT', 'SRT'):
                    myLogger.log_and_print(f"Processing {key} data")
                    self.process_core_data(key,filename, proj_dir, flight, project, rate, config_ext)
                if (key == "threeVCPI"):
                    self.process_threeVCPI(aircraft, project, flight, inst_dir["twods"], inst_dir["oap"])
                if key in ("ICARTT","IWG1"):
                    self.generate_derived_files(data_dir,filename, project, flight, key, file_ext)
            # Process PMS2D Files
                if key == "PMS2D":
                    self.process_pms2d_files(inst_dir, raw_dir, filename)
        
        for key in file_ext:
            if (key == "LRT") or (key == "ADS"):
                next
            elif (key == "PMS2D"):
                (process, filename[key]) = \
                    findFiles.find_file(inst_dir[key] + "PMS2D/", flight,
                                project, file_type[key],
                                file_ext[key], process, process,
                                self.date)
            else:
                (process, filename[key]) = \
                    findFiles.find_file(inst_dir[key], flight,
                                project, file_type[key],
                                file_ext[key], process, process,
                                self.date)
        # QA Notebook Generation
        if process and QA_notebook:
            self.generate_qa_notebook(project, flight)

    def process_core_data(self, key, filename, proj_dir, flight, project, rate, config_ext):
        """
        Process the core data for a given key.
        Args:
            key (str): The key representing the type of core data.
            filename (dict): A dictionary containing filenames for different data types.
            proj_dir (str): The project directory.
            flight (str): The flight identifier.
            project (str): The project identifier.
            rate (dict): A dictionary containing data rates for different data types.
            config_ext (dict): A dictionary containing configuration extensions for different data types.
        Returns:
            bool: True if the processing is successful, False otherwise.
        """

        _ncfile = filename[key] if key == 'LRT' else self.ncfile
        self.flags = " -b "

        res = self._process_netCDF(
            filename["ADS"],
            _ncfile,
            rate[key],
            config_ext[key],
            proj_dir,
            flight,
            project,
            self.flags,
        )
        if res:
            self.stat[key]["proc"] = self._reorder_nc(_ncfile)
        else:
            self.stat[key]["proc"] = False
            
    def _process_netCDF(self, rawfile, ncfile, rate, config_ext, proj_dir, flight, project, flags):
        """
        Run nimbus to create a .nc file (LRT, HRT, or SRT)

        Args:
            rawfile (str): The path to the raw ads file.
            ncfile (str): The path to the output .nc file.
            rate (str): The processing rate ('', 'h', 's').
            config_ext (str): The configuration file extension.
            proj_dir (str): The project directory.
            flight (str): The flight number.
            project (str): The project name.
            flags (str): Additional flags for nimbus.

        Returns:
            bool: True if nimbus execution is successful, False otherwise.
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
                line = f"pr={rate}\n"
                cf.write(str(line))
        # execute nimbus in batch mode using the config file
        command = f"/opt/local/bin/nimbus{flags}{nimConfFile}"
        message = f"about to execute nimbus I hope: {command}"
        if not myLogger.run_and_log(command, message):
            myLogger.log_and_print('Nimbus call failed',log_level='warning')
            return False

        return True

    def process_threeVCPI(self, aircraft, project, flight,
                            twods_raw_dir, oapfile_dir):
        """
        Process 3vCPI.
        Args:
            aircraft (str): The aircraft name.
            project (str): The project name.
            flight (str): The flight number.
            twods_raw_dir (str): The directory path for raw 2D files.
            oapfile_dir (str): The directory path for output OAP files.
        Raises:
            OSError: If the oapfile_dir cannot be created.

        """
        message = "\n\n *****************  3VCPI **************************\n"
        myLogger.log_and_print(message)
        mkdir_fail = False
        first_base_file = ''
        catted_file = f'base_{flight}all.2DSCPI'
        catted_2d_file = f'base_{flight}all.2d'
        os.chdir(twods_raw_dir)
        if os.path.isfile(catted_file):
            os.remove(catted_file)
        if file_list := glob.glob(f'{twods_raw_dir}base*2DSCPI'):
            os.chdir(twods_raw_dir)
            filenum = 1
            for file in file_list:
                if filenum == 1:
                    first_base_file = file
                command = f'cat {file} >> {catted_file}'
                message = f"cat 3vcPIfiles:{command}"
                myLogger.run_and_log(command,message)

            command = f'{translate2ds}-project {project}'
            + ' -flight ' + flight + ' -platform ' + aircraft
            + ' -sn SPEC001 -f ' + catted_file + ' -o .'
            message = f' 3v-cpi command:{command}'
            myLogger.run_and_log(command, message)

            # move 2DS file to the RAF naming convention and location
            if not os.path.isdir(oapfile_dir):
                try:
                    os.mkdir(oapfile_dir)
                except OSError as e:
                    myLogger.log_and_print(e,'error')
                    message = "\nERROR: Couldnt make oapfile dir:"+ oapfile_dir+"\nskipping 2d file gen/placement\n"
                    myLogger.log_and_print(message)
                    mkdir_fail = True
            if not mkdir_fail:
                self._move_merge_threeVCPI(
                    first_base_file, catted_2d_file, oapfile_dir, flight
                )
    def _reorder_nc(self, ncfile):
        """
        Reorder netcdf file
        """
        command = f"nccopy -u {ncfile} tmp.nc"
        message = f"about to execute : {command}"
        myLogger.run_and_log(command,message)

        command = f"/bin/mv tmp.nc {ncfile}"
        message = f"about to execute : {command}"
        if not myLogger.run_and_log(command, message):
            myLogger.log_and_print("ERROR: ncreorder failed, but NetCDF should be ok\n")
        return 'Yes'

    def _move_merge_threeVCPI(self, first_base_file, catted_2d_file, oapfile_dir, flight):
        """
        Moves the catted_2d_file to the specified oapfile_dir with a new filename based on the flight and datetime.
        Then merges the 3v-cpi data from the moved file into a netCDF file.

        Args:
            first_base_file (str): Path to the first base file.
            catted_2d_file (str): Path to the catted 2d file.
            oapfile_dir (str): Directory where the moved file will be stored.
            flight (str): Flight identifier.
        """
        twod_dir, fb_filename = os.path.split(first_base_file)
        # Pull out of base{datetime}.2d
        datetime = fb_filename.split('.')[0].split('e')[1]
        command = f'mv {catted_2d_file} {oapfile_dir}20{datetime}_{flight}.2d'
        message = f' mv command: {command}'
        myLogger.run_and_log(command, message)
        threevcpi2d_file = f'{oapfile_dir}20{datetime}_{flight}.2d'

        # Merge 3v-cpi data into netCDF file
        command = f'process2d {threevcpi2d_file} -o {self.ncfile}'
        message = f"3v-cpi merge cmd: {command}"
        if myLogger.run_and_log(command, message):
            self.proc_3vcpi_files = 'Yes'


    def extract_date_from_ads_filename(self, fname, raw_dir):
        """
        Returns the date from the ADS filename based on the filname structure
        raw_dir/YYYYMMDD_HHMMSS*.ads
        Args:
            fname (str): The filename of the ADS file.
            raw_dir (str): The raw data directory.
        """
        file_name = fname.split(raw_dir)[1]
        self.date = file_name.split('_')[0]


    def generate_derived_files(self, data_dir, filename, project, flight, key,file_ext):
        if key == "IWG1":
            # Generate IWG1 file from LRT
            output_file = data_dir + project + flight + '.' + file_ext["IWG1"]
            command = f"nc2iwg1 {filename['LRT']} -o {output_file}"
            message = f"Generating IWG1 file: {command}"
            if myLogger.run_and_log(command, message):
                self.stat[key]["proc"] = 'Yes'
        elif key == "ICARTT":
            # Generate ICARTT file from LRT
            command = f"nc2asc -i {filename['LRT']} -o {data_dir}tempfile.ict -b {self.nc2ascBatch}"
            message = f"Generating ICARTT file: {command}"
            if myLogger.run_and_log(command, message):
                self.stat[key]["proc"] = 'Yes'
        else:
            myLogger.log_and_print(f"Unknown derived file type: {key}", log_level='warning')

    def process_pms2d_files(self, inst_dir, raw_dir, filename):
        """
        Process PMS2D files.

        Args:
            inst_dir (dict): Dictionary containing the directory paths for instrument data.
            raw_dir (str): Directory path for raw data.
            filename (dict): Dictionary containing the filenames for different data files.
        """
        myLogger.ensure_dir(inst_dir["PMS2D"] + 'PMS2D')
        file_name = self.PMS2D_ADS.split(raw_dir)[1]
        fileelts = file_name.split('.')
        filename["PMS2D"] = inst_dir["PMS2D"] + 'PMS2D/' + fileelts[0] + '.2d'

        if not os.path.exists(filename["PMS2D"]):
            # General form of extract2d from RAW_DATA_DIR is:
            # Extract2d PMS2D/output.2d input.ads
            command = 'extract2d ' + filename["PMS2D"] + ' ' + self.PMS2D_ADS
            message = '\nExtracting 2D from ads:' + command + '\n'
            myLogger.run_and_log(command,message)
        
        if os.path.exists(filename["PMS2D"]):
            # Process 2D data into netCDF file.  General form is:
            # Process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
            command = 'process2d ' + filename["PMS2D"] + ' -o ' + filename["LRT"]
            message = f'2D merge command: {command}'
            if myLogger.run_and_log(command, message):
                self.stat["PMS2D"]["proc"] = 'Yes'

    def generate_qa_notebook(self, project, flight):
        """
        Generates a QA notebook for the specified project and flight.

        Args:
            project (str): The name of the project.
            flight (str): The flight number.
        """
        os.chdir("/home/local/aircraft_QAtools_notebook/")
        command = f"./auto_export.py --project {project} --flight {flight}"
        myLogger.run_and_log(command, f"about to execute : {command}")
        command = f"cp -p {project}{flight}.html /home/ads/Desktop"
        command = f"cp -p {project}{flight}.pdf /home/ads/Desktop"
        myLogger.run_and_log(command, "copying QAQC html to desktop")
        if SYNCTHING:
            command = f"cp -p {project}{flight}.html {project}{flight}.pdf {syncthing_staging_dir}/QA_Tools"
            myLogger.run_and_log(command, "copying QAQC html and pdf to syncthing staging dir")
        

import _logging
import logging
import os, glob, sys
import re
import _findfiles
import subprocess
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import  translate2ds, QA_notebook


myLogger = _logging.MyLogger()
class Process:
    def __init__(self, file_ext, data_dir, flight, filename, raw_dir, status, project, aircraft,
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
        """
        self.stat = status
        #QA_notebook=False ##TEMPORARY FOR TESTING
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
        process, filename['ADS'] = findFiles.find_file(
            inst_dir['ADS'], flight, project, file_type['ADS'],
            file_ext['ADS'], process, process, file_prefix
        )
        # ADS - Extract flight date
        self._extract_date_from_ads_filename(filename['ADS'], raw_dir)
    

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
                    self._process_core_data(key,filename, proj_dir, flight, project, rate, config_ext)
                if (key == "threeVCPI"):
                    self._process_threeVCPI(aircraft, project, flight, inst_dir["twods"], inst_dir["oap"])
                if key in ("ICARTT","IWG1"):
                    self._generate_derived_files(data_dir,filename, project, flight, key, file_ext)
            # Process PMS2D Files
                if key == "PMS2D":
                    self._process_pms2d_files(inst_dir, raw_dir, filename)
        
        for key in file_ext:
            if (key == "LRT") or (key == "ADS"):
                next
            elif (key == "PMS2D"):
                (process, filename[key]) = \
                    findFiles.find_file(inst_dir[key] + "PMS2D/", flight,
                                project, file_type[key],
                                file_ext[key], process, process,
                                self.date[0:8])
            else:
                (process, filename[key]) = \
                    findFiles.find_file(inst_dir[key], flight,
                                project, file_type[key],
                                file_ext[key], process, process,
                                self.date[0:8])
        # QA Notebook Generation
        if process and QA_notebook:
            self._generate_qa_notebook(project, flight)

    
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
                line = f"pr={pr}\n"
                cf.write(str(line))
        # execute nimbus in batch mode using the config file
        command = f"/opt/local/bin/nimbus{flags}{nimConfFile}"
        message = f"about to execute nimbus I hope: {command}"
        if not myLogger.run_and_log(command, message):
            myLogger.log_and_print('Nimbus call failed',log_level='warning')
            return False

        return True

    def _process_threeVCPI(self, aircraft, project, flight,
                        twods_raw_dir, oapfile_dir):
        """
        Process 3vCPI
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
                self._move_merge_threeVCPI_(
                    first_base_file, catted_2d_file, oapfile_dir, flight
                )


    def _move_merge_threeVCPI_(self, first_base_file, catted_2d_file, oapfile_dir, flight):
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


    def _extract_date_from_ads_filename(self, fname, raw_dir):
        file_name = fname.split(raw_dir)[1]
        self.date = file_name[:15]
        self.date = re.sub('_', '', self.date)

    def _process_core_data(self, key, filename, proj_dir, flight, project, rate, config_ext):
        # Process the ads data to desired netCDF frequencies

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


    def _generate_derived_files(self, data_dir, filename, project, flight, key,file_ext):
            # Generate IWG1 file from LRT, if requested
        command_dict = {'IWG1':"nc2iwg1 " + filename["LRT"] + " -o " + data_dir + project + flight + '.' + file_ext["IWG1"],
                        'ICARTT':"nc2asc -i " + filename["LRT"] + " -o " + data_dir + "tempfile.ict -b " + self.nc2ascBatch}
        message = f"about to execute : {command_dict[key]}"
        if myLogger.run_and_log(command_dict[key],message):
            self.stat[key]["proc"] = 'Yes'


    def _process_pms2d_files(self, inst_dir, raw_dir, filename):

        myLogger.ensure_dir(inst_dir["PMS2D"] + 'PMS2D')
        file_name = filename["ADS"].split(raw_dir)[1]
        fileelts = file_name.split('.')
        filename["PMS2D"] = inst_dir["PMS2D"] + 'PMS2D/' + fileelts[0] + '.2d'

        if not os.path.exists(filename["PMS2D"]):
            # General form of extract2d from RAW_DATA_DIR is:
            # Extract2d PMS2D/output.2d input.ads
            command = 'extract2d ' + filename["PMS2D"] + ' ' + filename["ADS"]
            message = '\nExtracting 2D from ads:' + command + '\n'
            myLogger.log_and_print(message)
            os.system(command)

        if os.path.exists(filename["PMS2D"]):
            # Process 2D data into netCDF file.  General form is:
            # Process2d $RAW_DATA_DIR/$proj/PMS2D/input.2d -o $DATA_DIR/$proj/output.nc
            command = 'process2d ' + filename["PMS2D"] + ' -o ' + filename["LRT"]
            message = f'2D merge command: {command}'
            if myLogger.run_and_log(command, message):
                self.stat["PMS2D"]["proc"] = 'Yes'

    def _generate_qa_notebook(self, project, flight):
        os.chdir("/home/local/aircraft_QAtools_notebook/")
        command = f"./auto_export.py --project {project} --flight {flight}"
        myLogger.run_and_log(command, f"about to execute : {command}")
        command = f"cp -p {project}{flight}.html /home/ads/Desktop"
        myLogger.run_and_log(command, "copying QAQC html to desktop")
        
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
        

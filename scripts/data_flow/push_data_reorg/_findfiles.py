from _repetition import *

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
        else:
                            # pattern needs a star to match the ads file
                pattern = f"{data_dir}*{flight}{filetype}.{fileext}"
        datalist = glob.glob(pattern)
        if (datalist.__len__() == 1):
                # Found a single file of the type we are looking for
                # [eg ads or lrt or nc, etc.
                # Find out if user wants to reprocess the file?
                datafile = datalist[0]  # Return name of file that was found
        elif datalist.__len__() == 0:
                            # Did not find any files with the extension we are looking for
                message = f"No files found matching form: {pattern}"
                self.logger.info(message)
                print(message)
                if fileext == 'ads':
                        self._extracted_from_find_file_41("Aborting...")
                elif flag:
                        message = "We are scheduled to process all is good."
                        log_and_print(message)
                        datafile = pattern
                else:
                        # but if the file is not marked to be regenerated in the
                        # fieldProc_setup.py file, then we have a probem.
                        message = f"We have an nc file but not {fileext} file.... aborting..."
                        self._extracted_from_find_file_41(message)
        else:
                # Found multiple files that match the type we are looking for.
                # Step through the files and let the user decide
                # which is the one we should work with
                message = f"More than one {fileext} file found."
                self.logger.info(message)
                print(message)
                datafile = self.step_through_files(datalist, fileext,
                                                reprocess)

        if datafile == '':
                # If after all this we haven't identified a file, abort processing.
                message = f"No {datafile} file identified! Aborting..."
                self._extracted_from_find_file_41(message)
        return(flag, datafile)


# TODO Rename this here and in `find_file`
def _extracted_from_find_file_41(self, message):
        self.logger.info(message)
        print(message)
        sys.exit(0)

def step_through_files(self, datalist, fileext, reprocess):
    """
    Handle multiple files of a given type for a single flight.

    Input:
        datalist (list): List of files of the same type.
        fileext (str): File type extension (for user messages).
        reprocess (bool): Whether to prompt the user for file selection.

    Return:
        str: The chosen file from the list, or empty string if user cancels.
    """
    if not reprocess:
        log_and_print(f'Ship is set to True so no need to choose {fileext} to process.')
        return datalist[0]  # No need to choose, return the first file
    i = 0
    while reprocess:  # Loop continuously until user chooses a file
        log_and_print("Stepping through files, please select the right one.")
        datafile = datalist[i]
        message = f"Is this the correct {fileext} file? ({datafile}) (Y/N):"
        ans = input(message).lower()
        if ans == 'y':
            return datafile
        if ans =='n':
            i = (i + 1) % len(datalist)
        else:
            ('Invalid input: select y or n')
            
            
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
        log_and_print(message)
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
        log_and_print(message)
        message = "We must process!"
        log_and_print(message)
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

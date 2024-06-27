import glob,os,logging, sys

class FindFiles:
    def __init__(self):
        self.logger = logging.getLogger('myLogger')
        
    def find_file(self, data_dir, flight, project, filetype, fileext, flag, reprocess, date=""):
        """Finds a file and prompts the user for selection if needed.

        Args:
            data_dir (str): Directory to search for files.
            flight (str): Flight type designator and number (e.g., "rf01").
            project (str): Project and flight combination (e.g., "ACCLIPrf01").
            filetype (str): File type character (e.g., "s" for sample rate).
            fileext (str): File extension (e.g., "asc", "nc").
            flag (bool): Whether file regeneration is allowed.
            reprocess (bool): Whether to prompt the user for file selection.
            date (str, optional): Date for ICARTT file naming convention.

        Returns:
            tuple: (flag, datafile)
                flag (bool): Indicates if file should be reprocessed.
                datafile (str): Path to the selected file, or an empty string if none found.
        """

        if fileext == 'ict':
            pattern = os.path.join(data_dir, f'{project}*{fileext}')
        else:
            pattern = os.path.join(data_dir, f"*{flight}{filetype}.{fileext}")

        datalist = glob.glob(pattern)

        if not datalist:
            self._handle_no_files_found(pattern, fileext, flag)
            return flag, '' 

        elif len(datalist) == 1:
            datafile = datalist[0]
            return flag, datafile

        else:  # Multiple files found
            message = f"More than one {fileext} file found."
            self.logger.info(message)
            datafile = self.step_through_files(datalist, fileext,
                                                    reprocess)
            return flag, datafile
        
    def _handle_no_files_found(self, pattern, fileext, flag):
        """Handles the case where no files are found. Logs, prints messages, and potentially aborts."""
        message = f"No files found matching form: {pattern}"
        self.logger.info(message)

        if fileext == 'ads':
            self.logger.error("Aborting...")
            sys.exit(0)
        elif flag:
            self.logger.info("We are scheduled to process all is good.")
        else:
            message = f"We have an nc file but no {fileext} file.... aborting..."
            self.logger.error(message)
            sys.exit(0)


    def _select_file_from_list(self, datalist, fileext):
        """Prompts the user to select the correct file from a list.

        Args:
            data_list (list): List of files of the same type.
            file_extension (str): File type extension (for user messages).

        Returns:
            str: The chosen file from the list, or None if user cancels.
        """
        i=0
        while True:
            self.logger.info("Stepping through files, please select the right one.")
            current_file = datalist[i % len(datalist)]
            self.loffer.info(f"Reviewing file: {current_file}")

            confirmation = input(f"Is this the correct {fileext} file? ({current_file}) (Y/N): ").lower()
            if confirmation == 'y':
                return current_file
            elif confirmation == 'n':
                i += 1  
            else:
                print("Invalid input: Please select 'Y' or 'N'.")


    def step_through_files(self, datalist, fileext, reprocess):
            """Handles multiple files of a given type for a single flight.

        Args:
            datalist (list): List of files of the same type.
            file_extension (str): File type extension (for user messages).
            reprocess (bool): Whether to prompt the user for file selection.

        Returns:
            str: The chosen file from the list, or an empty string if the 
                user cancels or if 'reprocess' is False.
        """

            if not reprocess:
                self.logger.info(f'Ship is set to True so no need to choose {fileext} to process.')
                return datalist[0]  

            return self._select_file_from_list(self, datalist, fileext)

                
                
    def find_lrt_netcdf(self, filetype, flight, data_dir, file_prefix):
            '''
        See if a LRT file exists already and query user about what to do.
        '''
            process = False
            reprocess = False
            nclist = glob.glob(f'{data_dir}/*{flight}.{filetype}')
            if nclist.__len__() == 1:
                    self.ncfile = nclist[0]
                    message = f"Found a netCDF file: {self.ncfile}"
                    self.logger.info(message)
                    # Since found a netCDF file
                    # query user if they want to reprocess the data,
                    # or if they just want to ship the data to the NAS/ftp site.
                    reproc = ''
                    while not reproc and reproc != 'R' and reproc != 'S':
                            reproc = input('Reprocess? (R) or Ship? (S):')
                    if reproc == 'R':
                        process = True
                        reprocess = True
                    # Ship only
                    else:
                        process = False
                        reprocess = False
            elif nclist.__len__() == 0:
                    message = f"No files found matching form: {data_dir}*{flight}.{filetype}"
                    self.logger.info(message)
                    self.logger.info("We must process!")
                    process = True
                    self.ncfile = data_dir + file_prefix + ".nc"
            else:
                    self.logger.info(f"More than one {filetype} file found.")
                    self.ncfile = self.step_through_files(nclist, filetype, reprocess)

            if self.ncfile == '':
                self.logger.error("No NetCDF file identified! Aborting")
                sys.exit(0)

            return(process, reprocess, self.ncfile)

# PUSH_DATA Readme to understand data flow

## push_data: main()

This is the main file of the push_data module that calls on all of the classes to process and push the data for a field project. It performs the following:

    1. Creates an instance of the Setup class.
    2. Sets up the message for email.
    3. Assigns the initial status to the status variable to track the status of the data processing.
    4. Creates an instance of the Process class.
    5. Gets the status of the data processing after the Process class has been called.
    6. Calls the zip function if the sendzipped flag is set to True.
    7. Calls the FTP class if the FTP flag is set to True.
    8. Calls the GDrive class if the GDRIVE flag is set to True.
    9. Calls the NAS class if the NAS flag is set to True.
    10. Calls the report function from the setup class to append to the final message and send the status email.

## Environment variables

A number of environment variables need to be set for the script to run properly:

- $PROJECT --> name of project
- $AIRCRAFT --> name of aircraft
- $RAW_DATA_DIR --> the raw data directory variable set on the computer running push_data
- $PROJ_DIR  --> the project directory set on the computer running push_data

## Project Process Setup

The project specific setup constants and filepaths are defined in fieldProcSetup.py in the filepath $PROJ_DIR/$PROJECT/$AIRCRAFT/scripts

- raw_dir --> path of raw data directory; should be the combination of environment variables `$RAW_DATA_DIR + $PROJECT`
- proj_dir --> path of raw data directory; should be the combination of environment variables `$PROJ_DIR + / + $PROJECT + / + $AIRCRAFT`
- zip_dir --> path of the zip directory; should be `'/tmp/'`
- qc_ftp_site --> FTP server website;  `'catalog.eol.ucar.edu'`
- qc_ftp_dir --> FTP server directory; should be  `'/pub/incoming/catalog/ + project` with project in lowercase

File Paths:

- nc2ascBatch -->  path of n2asc file; should be environment variables `$PROJ_DIR +$PROJECT + / + $AIRCRAFT+/scripts/nc2asc.bat`

## Classes

### Setup

The Setup class is designed to initialize and prepare the push_data environment for processing and handling within a project. When initialized, it calls upon all the methods to set up the initial variables needed to process and push data. For more details on the individual methods see the documentation in _setup.py

`__init__`

The `__init__` method performs the following steps:

 1. Sets up a logger object for logging. `init__logger` and creates an instance of the MyLogger class for logging the setup
 2. Reads and stores the environment variables: `read_env(variable)`
 3. Initializes the constants for file extensions, directories, and tracking progress throughout: `create_status`, `createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)`,`createRate()`,`createConfigExt()`,`createFilePrefix(PROJECT, FLIGHT)`,`createFileType()`
 4. Parses user input for flight number and user email to send results: `readEmail()`, `readFlight()`
 5. Initializes email message for sending results.

`report`

The `report` method is not accessed in the `__init__` method, but once the Setup class is initialized it can be called to send the report to the user's email address.

### Process

The Process class is designed to automate and streamline the handling of various data files. The class provides a structured approach to executing a series of processing steps, such as converting raw data into netCDF format, reordering netCDF files, and processing 3vCPI data. Additionally, it includes methods for extracting dates from filenames and moving merged files to specified directories. The class is initialized with a comprehensive set of parameters. When initialized in push_data, the Process class is passed these parameters from the Setup class.

`__init__`

The `__init__` method performs the following steps:

 1. Tracks the processing status with the class variable `self.stat` which is passed the current version of the processing status.
 2. Determines the LRT netCDF processing modes using the FindFiles Class
 3. Find ADS files and extracts the date from the filename
 4. Processes other file types based on flight number
 5. Process and generate files: if the `process` flag from Step 2 is set to `True` it iterates over the keys in the file extension dictionary and performs the following
    - `process_core_data` for each key to call nimbus and create the netcdf files
    - If threeVCPI is set to TRUE in fieldProc_setup.py then `process_threeVCPI` will process 2d and OAP files.
    - If PMS2D is set to True then `process_pms2d_files` will be called
 6. Once the processing is done, it loops through the file extensions again and finds additional files except for ADS and LRT.
 7. If QATools is set to True, a `generate_QAtools` is run and a QA ipynb is exported as an html.

### GDrive

The GDrive class is designed to ship files to Google Drive via an rclone staging location.

`__init__`

The `__init__` method performs the following steps:

 1. Initializes the instance with the provided `data_dir`, `status`, `file_ext`, `inst_dir`, and `filename` parameters.
 2. Logs a message indicating the start of the process to put files to the rclone staging location for shipment to Google Drive.
 3. Checks the global variable `ship_all_ADS`. If it is set to True, it calls the `_ship_all_ads` method to ship all ADS files to the specified `rclone_staging_dir`.
 4. If ship_all_ADS is not True, it iterates over each key in the file_ext dictionary:
Prints the key (representing an instrument or file type).
 5. If the key is 'ADS' and the global variable `ship_ADS` is False, it skips the current iteration to not ship ADS files.
 6. Checks if the directory specified by the current key in `inst_dir` exists. If not, logs an error message and continues to the next iteration.
 7. If the directory exists and the filename for the current key is not an empty string, it calls the `_transfer_instrument_files` method to transfer the instrument files to the `rclone_staging_dir`.

### DataShipping

The __init__ method of the DataShipping class (in _NAS.py) performs the following steps:

 1. Initializes the instance with the provided parameters: `file_ext`, `filename`, `status`, `process`, `reprocess`, `inst_dir`, `flight`, `project`, and `final_message`.
 2. Sets the instance variable stat to the provided status.
 3. Sets the instance variable zip_dir to /tmp/.
 4. Checks if `NAS_permanent_mount` is False. If so, it constructs a command to mount the NAS using NFS, logs this action, and executes the command using os.system.
 5. Sets the instance variable nas_sync_dir to the path where files will be synced for FTP transfer.
 6. Sets the instance variable nas_data_dir to the path where files will be stored for local use.
 7. Logs a message indicating the start of copying files to the NAS scratch area.
 8. Iterates over each key in the file_ext dictionary:
 9. Sets dir_key to the current key. If the key is 'PMS2D', it appends a slash to dir_key.
 10. Logs a message indicating the copying of the file specified by the current key to the NAS data directory.
 11. Calls the rsync_file method to copy the file to the NAS data directory and updates the status dictionary for the current key with the result.
 12. Calls the setup_NAS method with the provided parameters to complete the setup process.

### SetupZip

The SetupZip class sets up the zipping functionality if the datafiles needs to be zipped before being transfered.
The `__init__` method of the SetupZip class performs the following steps:

 1. Iterates over each key in the file_ext dictionary:
    - If the key is "ADS", logs a message about finding a raw .ads file but not zipping it. Indicates that if zip_ads is set, it will bzip the .ads file next.
    - If the key is "PMS2D", logs a message about finding a raw .2d file but not zipping it.
    - For all other keys, it performs the following:
 2. Splits the filename into data_dir and file_name using os.path.split.
 3. Logs a message with the key and the file_name.
 4. Logs a message with the data_dir.
 5. Calls the `zip_file` method with file_name and the corresponding directory from inst_dir based on the key to

### TransferFTP

The TransferFTP class is used if the project is using FTP to transfer files around.
 TransferFTP `__init__` Method Overview

The `__init__` method of the `TransferFTP` class performs the following steps to transfer files to an FTP server:

1. It initializes the instance with the provided `status`, `file_ext`, `inst_dir`, and `filename` parameters. These parameters are essential for tracking file transfer status, managing file extensions, handling instrument directories, and dealing with filenames for each instrument, respectively.

2. Attempts to Connect to the FTP Server:
    - It tries to establish a connection to the FTP server using the `_connect_to_ftp` method.
    - If the connection is successful, it proceeds with the file transfer process.
    - In case of any errors during the connection (caught as `ftplib.all_errors`), it logs and prints the error message using `myLogger.log_and_print` and then exits the initialization process.

3. File Transfer Decision:
    - The method decides whether to transfer all ADS files or only selected files based on the `ship_all_ADS` flag.
    - If `ship_all_ADS` is `True`, it calls `_transfer_all_ads` method to transfer all ADS files.
    - If `ship_all_ADS` is `False`, it calls `_transfer_selected_files` method to transfer only the selected files based on file extensions, instrument directories, and filenames.

4. Quit FTP Session: After completing the file transfers, it gracefully closes the FTP session using `self.ftp.quit()`.

5. Revert Special Case for PMS2D Directory:
    - After the FTP session is closed, it reverts a special case for the `PMS2D` instrument directory by removing the `PMS2D/` prefix from its path.
    - This step ensures that the `inst_dir` dictionary reflects the correct directory paths after the FTP transfer process.

This method effectively handles the initialization and setup for transferring files to an FTP server, including error handling, logging, and conditional file transfer based on specific criteria.

### FindFiles

The FindFiles class is a collection of helper methods for the Process Class to find the datafiles based on the input parameters.

`find_file`

Searches for a specific file in a given directory and handles different scenarios based on the search results. It returns the name of the found file and a flag indicating whether the file should be reprocessed.

The method takes in several parameters: `data_dir` (the directory to search for files), `flight` (the flight type designator and number), `project` (the project + flight), `filetype` (the type of file to search for), `fileext` (the file extension), `flag` (a flag indicating whether the file should be reprocessed), `reprocess` (a flag indicating whether the files should be reprocessed), and an optional date parameter.

The method first initializes an empty string variable called datafile. It then constructs a pattern based on the file extension and searches for files that match the pattern using the glob.glob function. The search results are stored in a list called datalist.

Based on the number of files found, the method handles different scenarios:

1. If only one file is found, it prompts the user to decide whether to reprocess the file.
2. If no files are found, it logs and prints an error message. If the file extension is 'ads', it aborts the processing. Otherwise, if the flag is True, it sets datafile to the pattern and logs and prints a message indicating that all is good. Otherwise, it aborts the processing.
3. If multiple files are found, it logs and prints a message indicating that more than one file is found, and then calls the step_through_files method to allow the user to select a file from the list.
4. Finally, if datafile is still an empty string, it logs and prints an error message and aborts the processing. Otherwise, it returns the flag and datafile.

`step_through_files`

Handles multiple files of a given type for a single flight. It allows the user to select a file from a list of files, either by stepping through them or by returning the first file if a flag is set.

The method takes in three parameters: `datalist` (a list of files of the same type), `fileext` (the file type extension, used for user messages), and `reprocess` (a flag indicating whether the files should be reprocessed).

The method initializes an empty string variable called `datafile`. If `reprocess` is `True`, it enters a loop where it prompts the user to select a file from the datalist until a file is chosen. If `reprocess` is `False`, it sets datafile to the first file in the datalist.

After the loop or assignment, it logs and prints a message indicating the selected file, and then returns `datafile`.

`find_lrt_netcdf`

The `find_lrt_netcdf` method is designed to locate and manage LRT (Low-Rate Time) NetCDF files within a specified directory. It performs several key operations based on the existence and number of such files related to a specific flight and filetype.

Inputs

- `filetype` (str): The extension or type of the file to look for, typically indicating the format (e.g., 'nc' for NetCDF).
- `flight` (str): The flight number or identifier used to match files.
- `data_dir` (str): The directory path where the files are located.
- `file_prefix` (str): The prefix used for naming the files, aiding in the creation of a new file if necessary.

Returns

- `tuple`: A tuple containing a boolean and a string.
  - The boolean (`process`) indicates whether the file should be reprocessed (`True`) or shipped as is (`False`).
  - The string (`self.ncfile`) specifies the path to the NetCDF file to be processed or shipped.

Behaviors

1. Single File Found: If exactly one file matching the criteria (`{data_dir}/*{flight}.{filetype}`) is found, it logs the file's path and prompts the user to decide between reprocessing the data (`R`) or shipping the data as is (`S`). The user's choice determines the `process` flag's value.

2. No Files Found: If no files match the search criteria, it logs a message indicating no files were found and sets the `process` flag to `True`, indicating the necessity to process data. It also constructs a new file path using `data_dir` and `file_prefix` with a '.nc' extension for processing.

3. Multiple Files Found: If more than one file is found, it logs a message indicating the situation and calls `self.step_through_files` with the list of found files, `filetype`, and the `process` flag. This method is presumably designed to let the user or the system decide which file to work with, but its behavior is not detailed in the provided excerpt.

4. Error Handling: If, after attempting to identify the correct NetCDF file, `self.ncfile` is empty (`''`), it logs and aborts the operation, indicating that no suitable NetCDF file was identified.

## Usage

This method is useful in workflows where managing LRT NetCDF files is necessary, especially in scenarios involving conditional processing or shipping of data based on the files' existence and user input.

### MyLogger

The MyLogger class sets up the logger to be used throughout the push_data program and defines common functions used throughout

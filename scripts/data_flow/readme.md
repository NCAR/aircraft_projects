# Readme to understand data flow of push_data and sync_field_data

## Table of Contents

- [push_data.py](#push_datapy)
  - [push_data: main()](#push_data-main)
  - [Environment Variables](#environment-variables)
  - [Project Process Setup](#project-process-setup)
  - [Classes](#classes)
    -[Setup](#setup)
    -[Process](#process)
    -[GDrive](#gdrive)
    -[DataShipping](#datashipping)
    -[SetupZip](#setupzip)
    -[TransferFTP](#transferftp)
    - [FindFiles](#findfiles)
- [sync_field_data.py](#sync_field_datapy)
    -[sync_field_data: main()](#sync_field_data-main)
    -[Setup functions](#setup-functions)
    -[Helper functions](#helper-functions)
    -[Main functions](#main-functions)
- [Testing for Developers](#testing-for-developers)
    -[Test environment](#test-environment)
    -[Running tests](#running-tests)
    -[Test Modules](#test-modules)


## push_data.py

push_data.py is the main module to automate pushing and processing raw data from the groundstation.

### push_data: main()

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

### Environment variables

A number of environment variables need to be set for the script to run properly:

- $PROJECT --> name of project
- $AIRCRAFT --> name of aircraft
- $RAW_DATA_DIR --> the raw data directory variable set on the computer running push_data
- $PROJ_DIR  --> the project directory set on the computer running push_data

### Project Process Setup

The project specific setup constants and filepaths are defined in fieldProcSetup.py in the filepath $PROJ_DIR/$PROJECT/$AIRCRAFT/scripts, including:

- ftp_site --> FTP server website;  `'ftp.eol.ucar.edu'`
- ftp_data_dir --> FTP server directory; should be  `'/pub/data/incoming/ + project + 'EOL_data/RAF_data'` with project in lowercase

In addition, the following locations are defined in the Setup class:

- RAW_DIR --> path of raw data directory; should be the combination of environment variables `$RAW_DATA_DIR + $PROJECT`]
- PROJ_DIR --> path of raw data directory; should be the combination of environment variables `$PROJ_DIR + / + $PROJECT + / + $AIRCRAFT`]

the DataShipping class (in _NAS.py):

- zip_dir --> path of the zip directory; should be `'/tmp/'`

and the Process class:

- nc2ascBatch -->  path of n2asc file; should be environment variables `$PROJ_DIR +$PROJECT + / + $AIRCRAFT + /scripts/nc2asc.bat`

### Classes

#### Setup

The Setup class is designed to initialize and prepare the push_data environment for processing and handling within a project. When initialized, it calls upon all the methods to set up the initial variables needed to process and push data. For more details on the individual methods see the documentation in _setup.py

`__init__`

The `__init__` method performs the following steps:

 1. Sets up a logger object for logging. `init__logger` and creates an instance of the MyLogger class for logging the setup
 2. Reads and stores the environment variables: `read_env(variable)` and create the `RAW_DIR` [path of raw data directory; should be the combination of environment variables `$RAW_DATA_DIR + $PROJECT`] and `PROJ_DIR` [path of raw data directory; should be the combination of environment variables `$PROJ_DIR + / + $PROJECT + / + $AIRCRAFT`] variables.
 3. Initializes the constants for file extensions, directories, and tracking progress throughout: `create_status`, `createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)`,`createRate()`,`createConfigExt()`,`createFilePrefix(PROJECT, FLIGHT)`,`createFileType()`
 4. Parses user input for flight number and user email to send results: `readEmail()`, `readFlight()`
 5. Initializes email message for sending results.

`report`

The `report` method is not accessed in the `__init__` method, but once the Setup class is initialized it can be called to send the report to the user's email address.

#### Process

The Process class is designed to automate and streamline the handling of various data files. The class provides a structured approach to executing a series of processing steps, such as converting raw data into netCDF format, reordering netCDF files, and processing 3vCPI data. Additionally, it includes methods for extracting dates from filenames and moving merged files to specified directories. The class is initialized with a comprehensive set of parameters. When initialized in push_data, the Process class is passed these parameters from the Setup class.

`__init__`

The `__init__` method performs the following steps:

 1. Tracks the processing status with the class variable `self.stat` which is passed the current version of the processing status.
 2. Defines nc2ascBatch as the path of the n2asc config file; should be environment variables `$PROJ_DIR +$PROJECT + / + $AIRCRAFT + /scripts/nc2asc.bat`
 3. Determines the LRT netCDF processing modes using the FindFiles Class
 4. Find ADS files and extracts the date from the filename
 5. Processes other file types based on flight number
 6. Process and generate files: if the `process` flag from Step 2 is set to `True` it iterates over the keys in the file extension dictionary and performs the following
    - `process_core_data` for each key to call nimbus and create the netcdf files
    - If threeVCPI is set to TRUE in fieldProc_setup.py then `process_threeVCPI` will process 2d and OAP files.
    - If PMS2D is set to True then `process_pms2d_files` will be called
 7. Once the processing is done, it loops through the file extensions again and finds additional files except for ADS and LRT.
 8. If QATools is set to True, a `generate_QAtools` is run and a QA ipynb is exported as an html.

#### GDrive

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

#### DataShipping

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

#### SetupZip

The SetupZip class (in _zip.py) sets up the zipping functionality if the datafiles needs to be zipped before being transferred.
The `__init__` method of the SetupZip class performs the following steps:

 1. Iterates over each key in the file_ext dictionary:
    - If the key is "ADS", logs a message about finding a raw .ads file but not zipping it. Indicates that if zip_ads is set, it will bzip the .ads file next.
    - If the key is "PMS2D", logs a message about finding a raw .2d file but not zipping it.
    - For all other keys, it performs the following:
 2. Splits the filename into data_dir and file_name using os.path.split.
 3. Logs a message with the key and the file_name.
 4. Logs a message with the data_dir.
 5. Calls the `zip_file` method with file_name and the corresponding directory from inst_dir based on the key to

#### TransferFTP

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

#### FindFiles

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

##### Usage

This method is useful in workflows where managing LRT NetCDF files is necessary, especially in scenarios involving conditional processing or shipping of data based on the files' existence and user input.

#### MyLogger

The MyLogger class (in _logger.py) sets up the logger to be used throughout the push_data program and defines common functions used throughout

## sync_field_data.py

This script is used to synchronize field data between different systems after `push_data.py` has been run. It takes input from a source system and updates the target system with the latest field data. A process dictionary is setup at the start of the file which takes the boolean values from fieldProc_setup.py to establish which datatypes need to be processed based on the project.

This script can be run manually using the command `python sync_field_data.py`, or can be set as a cronjob to be run nightly and keep the data synced between active filesystems.

### sync_field_data: main()

The main function of the script checks the boolean values of NAS, GDRIVE and FTP as set in the fieldProc_setup.py project file to determine the source to sync data to. If none of these variables are set, it logs an error and exits with a status code of 1.

### Setup functions

`create_directory` creates a directory given the path and handle errors.
`dir_check` ensures that a given directory exits.
`unzip unzips` and zip files and moves them to a subfolder before processing.
`parse_args` instantiates the command line parser incase the user wants to save the log output to a file with the --logfile flag.
`setup_logger` sets up the logger to log the status of the data syncing process.

### Helper functions

`_run_and_log(command)` is a helper function to run a system command and log the message alongside it

The `_sync_data` function is a utility designed to synchronize files matching a specific pattern from a source directory to one or more destination directories. It leverages the rsync command for efficient file transfer, supporting both non-recursive and recursive syncing. It accepts parameters for the source directory, file pattern to match, destination directories, a base message for logging purposes, and an optional flag to enable recursive syncing. This makes _sync_data versatile for various data distribution needs, ensuring that files are systematically organized and transferred across different storage locations.

`ingest_to_local` function is designed to facilitate the distribution of data from FTP sites and raw data directories to local directories. This function is particularly useful in scenarios where there is no Network Attached Storage (NAS) available in the field, and data is transferred directly from the Ground Station to an FTP site. It ensures that data is systematically organized and stored locally for easy access and further processing.

`distribute_data` function is designed to automate the process of distributing various types of data to their respective destinations. It currently supports multiple data types, including PI data, MTP data, QAtools, and field data, each with its own predefined destination, file extension, source directory, log message, and recursion flag. This function streamlines the process of moving data from its source location to specific directories or FTP sites.

The `dist_prod` function is responsible for distributing RAF production data from the ingestion point to various destinations, including FTP sites and other specified directories. It handles multiple data types such as LRT, HRT, SRT, KML, ICARTT, and IWG1, each identified by specific file patterns (e.g., *.nc for netCDF files). This function ensures that production data is systematically organized and transferred to the appropriate locations for further use and analysis.

The `dist_raw` function focuses on distributing RAF raw data from the ingestion point to designated directories and FTP sites. It specifically looks for files in the /ADS and PMS2D subdirectories, handling both uncompressed (.ads) and compressed (.bz2) data files. This function ensures that raw data is promptly moved to processing locations.

### Main Functions

`sync_from_gdrive()` syncs data from GDRIVE to the local directory. This function iterates over the `proc_dict` dictionary and calls the `ingest_to_local` function to sync each data type from GDRIVE to the local directory. If the `QA_notebook` flag is set to True, it also calls the `distribute_data` function to distribute the synced data to the 'field_data' directory and 'QAtools' directory if QA_notebook is set to `True`.

`sync_from_ftp()` syncs data from FTP server to local directories. This function calls the `dir_check` function to ensure the required directories exist and iterates over the `proc_dict` dictionary to determine which data types need to be processed. For each data type that needs to be processed, it calls the `ingest_to_local` function to sync the data from the FTP server to the local `field_data` directory. It also calls the `distribute_data` function to distribute the synced data to other locations.

`sync_from_nas()` syncs data from NAS. This function calls the `dir_check` function to check the directory, calls the `dist_raw` function to distribute raw data, calls the `dist_prod` function to distribute production data, and finally calls the `distribute_data` function with the arguments ['field_data', 'MTP'].

## Testing for Developers

How to run tests for push_data.py and sync_field_data.py. When edits are made, you can run tests to ensure everything is still functioning by running `./run_tests.sh`. 

### Test environment

To run the tests for push_data and sync_field_data, you must have a test environment running python 3.12 or greater. You can create one using the testenv.yml file by running the following commands from the dataflow subdirectory:

`conda env create -f test/testenv.yml`

You can install the packages in the yml file manually with pip, or set up your own conda environment. Below is an example of a conda environment setup:
 `conda create -n test_env python=3.12`
 `conda activate test_env`
 `conda install pytest, pytest-mock`
 `pip install pyfakefs`

 Then make sure to activate your environment with `conda activate test_env` or `source activate test_env` before running the tests.

The environment variables for `$PROJECT`, `$PROJ_DIR`, and `$AIRCRAFT` must be configured to an existing project with a folder within the aircraft_projects repository for tests to run.

### Running tests

Run all tests in the aircraft_projects/scripts/data_flow/test/ directory by running `./run_tests.sh` from the data_flow/ directory with the active test environment.

### Test Modules

 1. `test__setup.py` tests the instantiation of the setup class and make sure all of the constants passed to process are properly formatted.
 2. `test_push_data.py` sets up a testing environment using fixtures and mocks to ensure that the push_data module functions correctly under various conditions. It is structured to test the main functionality of the data pushing process, including reading flight and email information, handling environment variables, interacting with the filesystem, and sending emails.
 3. `test__zip.py` tests the SetupZip class and the zipping functiomality of the push_data script on a fake filesystem.
 4. `test_sync_field_data.py` sets up a testing environment using fixtures and mocks to ensure the functionality of the sync_field_data.py script. It makes sure that based on different configurations the correct functions and commands are called to ensure the data is syncing to the correct directories.


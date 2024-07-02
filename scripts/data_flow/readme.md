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

### DataShipping

### SetupZip

### TransferFTP

### FindFiles

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

### MyLogger

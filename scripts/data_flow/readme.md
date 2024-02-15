# PUSH_DATA Readme to understand data flow

## Input variables:

- project --> name of project; should be environment variable $PROJECT
- aircraft --> name of aircraft; should be environment variable $AIRCRAFT

Input Paths:
- raw_dir --> path of raw data directory; should be the combination of environment variables `$RAW_DATA_DIR + $PROJECT`
- proj_dir --> path of raw data directory; should be the combination of environment variables `$PROJ_DIR + / + $PROJECT + / + $AIRCRAFT`
- zip_dir --> path of the zip directory; should be `'/tmp/'`
- qc_ftp_site --> FTP server website;  `'catalog.eol.ucar.edu'`
- qc_ftp_dir --> FTP server directory; should be  `'/pub/incoming/catalog/ + project` with project in lowercase


File Paths:

- nc2ascBatch -->  path of n2asc file; should be environment variables `$PROJ_DIR +$PROJECT + / + $AIRCRAFT+/scripts/nc2asc.bat`

## Classes

### Field Data

`__init__`

The __init__ method performs the following steps:

1. Sets up a logger object for logging.
2. Sets the log level to DEBUG.
3. Creates a file handler for logging to a file.
4. Sets the log message format.
5. Adds the file handler to the logger.
6. Retrieves the project name.
7. Sets the data directory and raw directory paths based on the project name.
8. Retrieves the aircraft name from the project directory.
9. Sets the project directory path, nc2ascBatch path, zip directory path, QC FTP site, and QC FTP directory.
10. Reads the flight designation and email address from user input.
11. Sets the rclone staging directory path.
12. Initializes the FieldData object by calling various setup methods.

`parse_args`
 
 Parses command-line arguments using argparse to define expected arguments and parse the ones passed to the script.

 `createFileExt`

Creates an ordered dictionary containing the file extensions for different file types.

The createFileExt method takes in several boolean parameters that determine which file types should be included. It creates an ordered dictionary where the keys are the file types and the values are the corresponding file extensions. The method checks the boolean parameters and adds the file types with their extensions to the dictionary if the corresponding parameter is True. Finally, it returns the created dictionary.

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
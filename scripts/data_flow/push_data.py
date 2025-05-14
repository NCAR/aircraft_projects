from check_env import check
check()
from _setup import Setup #setup, myLogger
import sys, os,glob
import  _GDrive, _process,_NAS,_FTP,_zip,_syncThing
 ##Check that the environment variables are set correctly    
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import NAS, FTP,  GDRIVE, SYNCTHING,sendzipped


def main():
    """
    Main function that orchestrates the data processing and transfer operations.

    This function performs the following steps:
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
    """

    # Creates instance of Setup class
    setup = Setup()
    
    # Set up message for email
    final_message = setup.final_message
    
    # Assign the initial status to the status variable to track the status of the data processing
    status = setup.STATUS

    # Create an instance of the Process class
    process=_process.Process(setup.FILE_EXT, setup.DATA_DIR, setup.FLIGHT, setup.FILENAME, setup.RAW_DIR, 
                    status, setup.PROJECT,setup.AIRCRAFT, setup.INST_DIR,setup.RATE, setup.CONFIG_EXT,
                    setup.FILE_TYPE,setup.PROJ_DIR,setup.FILE_PREFIX)

    # Get the status of the data processing after the Process class has been called
    status = process.stat

    # Call the zip function if the sendzipped flag is set to True
    if sendzipped:
        _zip.SetupZip(setup.FILE_EXT, setup.DATA_DIR,setup.FILENAME,  setup.INST_DIR)   
    
    if SYNCTHING:
        syncth = _syncThing.StageSyncThing(status, setup.FILE_EXT, setup.INST_DIR, setup.FILENAME,setup.FLIGHT)
        status = syncth.stat
    # Call the FTP class if the FTP flag is set to True
    if FTP:
        ftp= _FTP.TransferFTP(status, setup.FILE_EXT, setup.INST_DIR, setup.FILENAME)
        status = ftp.stat # Get the status of the data processing after the FTP class has been called

    # Call GDrive class if the GDRIVE flag is set to True
    if GDRIVE:
        gdrive= _GDrive.GDrive(status, setup.FILE_EXT, setup.INST_DIR, setup.FILENAME)
        status = gdrive.stat # Get the status of the data processing after the GDrive class has been called 

    # Call NAS class if the NAS flag is set to True
    if NAS:
        _NAS.DataShipping(setup.FILE_EXT, setup.FILENAME,status, setup.process, setup.reprocess, 
                        setup.INST_DIR, setup.FLIGHT, setup.PROJECT, final_message)
        status  = _NAS.stat
        final_message = _NAS.final_message

    # Call the report function from the setup class to append to the final message and send the status email
    setup.report(status, setup.PROJECT, setup.FLIGHT, setup.EMAIL, setup.FILE_EXT,final_message)

if __name__ == "__main__":
    main()


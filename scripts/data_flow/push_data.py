from _setup import Setup #setup, myLogger
import sys, os,glob
import  _GDrive, _process,_NAS,_FTP,_zip
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import NAS, FTP,  GDRIVE,sendzipped


def main():

    # instantiate FieldData class
    setup = Setup()
    final_message = setup.final_message
    # set up the email functionality
    status = setup.STATUS

    process=_process.Process(setup.FILE_EXT, setup.DATA_DIR, setup.FLIGHT, setup.FILENAME, setup.RAW_DIR, 
                    status, setup.PROJECT,setup.AIRCRAFT, setup.INST_DIR,setup.RATE, setup.CONFIG_EXT,
                    setup.FILE_TYPE,setup.PROJ_DIR,setup.FILE_PREFIX)
    status = process.stat
    _zip.SetupZip(setup.FILE_EXT, setup.DATA_DIR,setup.FILENAME,  setup.INST_DIR)   
    
    # Call FTP function if the FTP flag is set to True
    if FTP:
        ftp= _FTP.TransferFTP(status, setup.FILE_EXT, setup.INST_DIR, setup.FILENAME)
        status = ftp.stat

    # Call GDrive function if the GDRIVE flag is set to True
    if GDRIVE:
        gdrive= _GDrive.GDrive(setup.DATA_DIR, status, setup.FILE_EXT, setup.INST_DIR, setup.FILENAME)
        status = gdrive.stat

    # Call NAS functions if the NAS flag is set to True
    if NAS:
        _NAS.DataShipping(setup.FILE_EXT, setup.FILENAME,status, setup.process, setup.reprocess, 
                        setup.INST_DIR, setup.FLIGHT, setup.PROJECT, final_message)
        status  = _NAS.stat
        final_message = _NAS.final_message
        

    # Call the report function which appends the final message for emailing 
    setup.report(status, setup.PROJECT, setup.FLIGHT, setup.EMAIL, setup.FILE_EXT,final_message)


if __name__ == "__main__":
    main()


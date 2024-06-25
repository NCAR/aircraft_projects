from field_data import FieldData #setup, myLogger
import sys, os,glob
import  _GDrive, _process,_NAS,_FTP
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import NAS, FTP,  GDRIVE



def main():

    # instantiate FieldData class
    fielddata = FieldData()
    # set up the email functionality
    
    _process.Process(fielddata.file_ext, fielddata.data_dir, fielddata.flight, fielddata.filename, fielddata.raw_dir, 
                    fielddata.status, fielddata.project,fielddata.aircraft, fielddata.inst_dir,fielddata.rate, fielddata.config_ext,
                    fielddata.file_type,fielddata.proj_dir,fielddata.file_prefix)

    
    

    # Call FTP function if the FTP flag is set to True
    if FTP:
        _FTP.TransferFTP(fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename)

    # Call GDrive function if the GDRIVE flag is set to True
    if GDRIVE:
        _GDrive.GDrive(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename)

    # Call NAS functions if the NAS flag is set to True
    if NAS:
        _NAS.DataShipping(fielddata.file_ext, fielddata.filename, fielddata.status, fielddata.process, fielddata.reprocess, 
                        fielddata.inst_dir, fielddata.flight, fielddata.project, fielddata.final_message)

    # Call the report function which appends the final message for emailing 
    fielddata.report(fielddata.final_message, fielddata.status, fielddata.project, fielddata.flight, fielddata.email, fielddata.file_ext)


if __name__ == "__main__":
    main()


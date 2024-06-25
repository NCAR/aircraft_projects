from field_data import FieldData #setup, myLogger
import sys, os,glob
import _logging, _GDrive, _process, _setup,_NAS,_FTP
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import NAS, FTP, sendzipped,  GDRIVE



def main():

    # instantiate FieldData class
    fielddata = FieldData()
    # set up the email functionality
    fielddata.setup.setup_email(fielddata.data_dir, fielddata.email)
    
    _process.Process(fielddata.file_ext, fielddata.data_dir, fielddata.flight, fielddata.filename, fielddata.raw_dir, 
                    fielddata.status, fielddata.project,fielddata.aircraft, fielddata.inst_dir,fielddata.rate, fielddata.config_ext,
                    fielddata.file_type,fielddata.proj_dir,fielddata.file_prefix)

    

    # Zip files only if set to True
    if sendzipped:
        fielddata.setup.setup_zip(fielddata.file_ext, fielddata.data_dir, fielddata.filename, fielddata.inst_dir)

    # Call FTP function if the FTP flag is set to True
    if FTP:
        _FTP.setup_FTP(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename)

    # Call GDrive function if the GDRIVE flag is set to True
    if GDRIVE:
        _GDrive.GDrive(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename)

    # Call NAS functions if the NAS flag is set to True
    if NAS:
        _NAS.setup_shipping(fielddata.file_ext, fielddata.filename, fielddata.process, fielddata.reprocess, fielddata.status)
        _NAS.setup_NAS(fielddata.process, fielddata.reprocess, fielddata.file_ext, fielddata.inst_dir, fielddata.status, fielddata.flight, fielddata.project, fielddata.email, fielddata.final_message, fielddata.filename, fielddata.nas_sync_dir, fielddata.nas_data_dir)

    # Call the report function which appends the final message for emailing 
    fielddata.myLogger.report(fielddata.final_message, fielddata.status, fielddata.project, fielddata.flight, fielddata.email, fielddata.file_ext)


if __name__ == "__main__":
    main()


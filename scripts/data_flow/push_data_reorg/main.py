from field_data import FieldData
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, datadump, GDRIVE, rclone_staging_dir


def main():

    # instantiate FieldData class
    fielddata = FieldData()

    # process data
    fielddata.process(fielddata.file_ext, fielddata.data_dir, fielddata.flight, fielddata.filename, fielddata.raw_dir, fielddata.status, fielddata.project)

    # set up the email functionality
    fielddata.setup_email(fielddata.data_dir, fielddata.email)

    # Zip files only if set to True
    if sendzipped:
        fielddata.setup_zip(fielddata.file_ext, fielddata.data_dir, fielddata.filename, fielddata.inst_dir)

    # Call FTP function if the FTP flag is set to True
    if FTP:
        fielddata.setup_FTP(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename)

    # Call GDrive function if the GDRIVE flag is set to True
    if GDRIVE:
        fielddata.GDrive(fielddata.data_dir, fielddata.raw_dir, fielddata.status, fielddata.file_ext, fielddata.inst_dir, fielddata.filename, fielddata.rclone_staging_dir)

    # Call NAS functions if the NAS flag is set to True
    if NAS:
        fielddata.setup_shipping(fielddata.file_ext, fielddata.filename, process, reprocess, fielddata.status)
        fielddata.setup_NAS(process, reprocess, fielddata.file_ext, fielddata.inst_dir, fielddata.status, fielddata.flight, fielddata.project, fielddata.email, fielddata.final_message, fielddata.filename, fielddata.nas_sync_dir, fielddata.nas_data_dir)

    # Call the report function which appends the final message for emailing 
    fielddata.report(fielddata.final_message, fielddata.status, fielddata.project, fielddata.flight, fielddata.email, fielddata.file_ext)


if __name__ == "__main__":
    main()


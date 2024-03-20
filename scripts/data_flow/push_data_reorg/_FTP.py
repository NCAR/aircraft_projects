import os
import sys
from scripts.data_flow.push_data_reorg._logging import *
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, datadump, GDRIVE, rclone_staging_dir


def setup_FTP(self, data_dir, raw_dir, status, file_ext, inst_dir, filename):
    '''No NAS this project, so put files to EOL server. Put
    zipped files if they exist.
    '''
    try:
        message = 'Opening FTP connection to: ' + ftp_site
        log_and_print(message)
        ftp = ftplib.FTP(ftp_site)
        ftp.login(user, password)
        print('')

    except ftplib.all_errors as e:
        message = 'Error connecting to FTP site ' + ftp_site
        log_and_print(message +'\n'+e, 'error')

    print('Putting files to FTP site:')
    print('')

    # When ftping, put PMS2D file in PMS2D subdir
    inst_dir['PMS2D'] = inst_dir['PMS2D'] + 'PMS2D/'

    # If set in config file script will FTP all ads in rdat
    # Keep this set to False unless you have time / bandwidth
    if ship_all_ADS is True:
        message = 'Starting ftp process for all available .ads files'
        self.logger.info(message)
        print(message)
        for rawfilename in os.listdir(inst_dir['ADS']):
            if rawfilename.endswith('.ads'):
                try:
                    os.chdir(inst_dir['ADS'])
                    ftp.cwd('/' + ftp_data_dir + '/ADS')
                    ftp.storbinary('STOR ' + rawfilename, open(rawfilename, 'rb'))
                    status["ADS"]["stor"] = 'Yes-FTP'
                    message = rawfilename + ' ftp successful!'
                    log_and_print(message)
                except Exception as e:
                    message = rawfilename + ' not sent'
                    log_and_print(message)
                    log_and_print(e,'error')

    else:
        # Loop through requested file extensions to be copied to ftp area
        for key in file_ext:
            print('\n' + key + '\n')

            if ship_ADS is False and key == 'ADS':
                # Skip ads if requested in fieldProc_setup.py
                continue
            else:
                try:
                    os.chdir(inst_dir[key])
                    print('Attempt to change to local dir ' + inst_dir[key])
                except ftplib.all_errors as e:
                    print('Could not change to local dir ' + inst_dir[key])
                    log_and_print(e,'error')
                    continue

            if filename[key] != '':
                print('Instrument file is ' + filename[key])
                # Get instrument filename; used for error reporting
                data_dir, file_name = os.path.split(filename[key])

                try:
                    print('Attempt to change to ftp dir /' + ftp_data_dir + '/' + key)
                    ftp.cwd('/' + ftp_data_dir + '/' + key)
                except ftplib.all_errors as e:
                    print('Could not change to dir ' + ftp_data_dir + '/' + key)
                    log_and_print(e,'error')
                    # Attempt to create needed dir
                    print('Attempt to create dir /' + ftp_data_dir + '/' + key)
                    try:
                        ftp.mkd('/' + ftp_data_dir + '/' + key)
                    except Exception as e:
                        print('Make dir /' + ftp_data_dir + '/' + key + ' failed')
                        log_and_print(e,'error')
                        continue
                    # Try to change to dir again
                    try:
                        ftp.cwd('/' + ftp_data_dir + '/' + key)
                    except Exception as e:
                        print('Change dir to ' + ftp_data_dir + '/' + key + ' failed')
                        log_and_print(e)
                        continue

            if file_name in ftp.nlst():
                print('File ' + file_name + ' already exists on ftp server.')
                print('File will not be transfered to ftp site')
                print('To force transfer, delete file from ftp site and rerun in Ship mode')
                continue

            # Transfer files to FTP site
            try:
                print('Transferring file...')
                file = open(file_name, 'rb')
                print(ftp.storbinary('STOR ' + file_name, file))
                file.close()
                status[key]["stor"] = 'Yes-FTP'

                print(datetime.datetime.now().time())
                print('Finished putting data file')
                print('')

            except ftplib.all_errors as e:
                print('Error writing ' + file_name + ' to ' + ftp_site + ':/' + ftp_data_dir + '/' + key)
                log_and_print(e)
                continue

    ftp.quit()

    # Revert PMS2D ftp special case
    inst_dir['PMS2D'] = re.sub('PMS2D/', '',inst_dir['PMS2D'])
    print("After FTP: " + inst_dir['PMS2D'])

import os
import sys
import ftplib
from scripts.data_flow.push_data_reorg._logging import *
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password, DATA_DIR, RAW_DATA_DIR, dat_parent_dir, rdat_parent_dir, NAS, NAS_permanent_mount, nas_url, nas_mnt_pt, FTP, ftp_site, password, ftp_parent_dir, ftp_data_dir, ICARTT, IWG1, HRT, SRT, sendzipped, zip_ADS, ship_ADS, ship_all_ADS, PMS2D, threeVCPI, QA_notebook, catalog, rstudio_dir, translate2ds, datadump, GDRIVE, rclone_staging_dir

def setup_ftp(self, status, file_ext, inst_dir, filename):
    """Transfers files to an FTP server.

    Args:
        data_dir (str): Base data directory (not directly used in this function).
        status (dict): Dictionary to track file transfer status.
        file_ext (dict): Dictionary of file extensions and their processing status.
        inst_dir (dict): Dictionary of instrument directories.
        filename (dict): Dictionary containing filenames for each instrument.
    """

    try:
        self._connect_to_ftp()
    except ftplib.all_errors as e:
        log_and_print(f'Error connecting to FTP site {ftp_site}: {e}','error')
        return

    print('Putting files to FTP site:')

    if ship_all_ADS:
        self._transfer_all_ads(status, inst_dir)
    else:
        self._transfer_selected_files(file_ext, inst_dir, filename)

    self.ftp.quit()
    # Revert PMS2D ftp special case
    inst_dir['PMS2D'] = re.sub('PMS2D/', '',inst_dir['PMS2D'])
    print("After FTP: " + inst_dir['PMS2D'])


def _connect_to_ftp(self):
    message = f'Opening FTP connection to: {ftp_site}'
    log_and_print(message)
    self.ftp = ftplib.FTP(ftp_site)
    self.ftp.login(user, password)


def _transfer_all_ads(self, status, inst_dir):
    # ... Implementation for transferring all ADS files ...
    message = 'Starting ftp process for all available .ads files'
    log_and_print(message)
    for rawfilename in os.listdir(inst_dir['ADS']):
        if rawfilename.endswith('.ads'):
            try:
                os.chdir(inst_dir['ADS'])
                ftp.cwd(f'/{ftp_data_dir}/ADS')
                ftp.storbinary(f'STOR {rawfilename}', open(rawfilename, 'rb'))
                status["ADS"]["stor"] = 'Yes-FTP'
                message = f'{rawfilename} ftp successful!'
                log_and_print(message)
            except Exception as e:
                message = f'{rawfilename} not sent'
                log_and_print(f'{message}/n{e}')
                


def _transfer_selected_files(self, file_ext, inst_dir, filename):
    for key in file_ext:
        if key == 'ADS' and not ship_ADS:
            continue

        if filename[key] == '':
            continue

        try:
            self._create_ftp_dir_if_needed(key)
            self._transfer_file(key, inst_dir[key], filename[key], status)
        except (ftplib.all_errors, OSError) as e:
            self.logger.error(f"Error processing {key}: {e}")


def _create_ftp_dir_if_needed(self, instrument):
    remote_dir = f'/{ftp_data_dir}/{instrument}'
    try:
        self.ftp.cwd(remote_dir)  # Check if exists
    except ftplib.all_errors:
        try:
            self.ftp.mkd(remote_dir)  # Create if it doesn't
            self.logger.info(f"Created FTP directory: {remote_dir}")
        except ftplib.all_errors as e:
            self.logger.error(f"Failed to create FTP directory {remote_dir}: {e}")


def _transfer_file(self, instrument, local_dir, file_name, status):
    remote_path = f'/{ftp_data_dir}/{instrument}/{file_name}'
    if remote_path not in self.ftp.nlst():  # Check for existing file 
        try:
            with open(os.path.join(local_dir, file_name), 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_path}', file)
            status[instrument]["stor"] = 'Yes-FTP'
            print(f"Successfully transferred {file_name}")
        except (ftplib.all_errors, OSError) as e:
            self.logger.error(f"Error transferring {file_name}: {e}")
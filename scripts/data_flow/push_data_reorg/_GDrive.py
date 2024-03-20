import os
from scripts.data_flow.push_data_reorg._logging import *
import subprocess  # For more reliable error handling with rsync and rclone
import shutil  # For potential cleanup operations


def _ship_all_ads(self, inst_dir, rclone_staging_dir, status):
    # ... (Implementation for shipping all ADS files) ...
    message = 'Starting rsync process for all available .ads files'
    log_and_print(message)
    for rawfilename in os.listdir(inst_dir['ADS']):
        if rawfilename.endswith('.ads'):
            try:
                os.chdir(inst_dir['ADS'])
                subprocess.run(f'rsync -u *.ads {rclone_staging_dir}ADS', check = True)
                status["ADS"]["stor"] = 'Yes-GDrive-staging'
                log_and_print(f'{rawfilename} rsync successful!')
            except subprocess.CalledProcessError as e:
                log_and_print('{rawfilename} not copied to local staging')
                log_and_print(e,'error')
            try:
                subprocess.run(f'rclone copy {rclone_staging_dir}/ADS gdrive_eolfield:/'+os.environ['PROJECT']+'/EOL_data/RAF_data/ADS --ignore-existing',check=True)
                status["ADS"]["ship"] = 'Yes-GDrive'
                log_and_print(f'{rawfilename} rclone successful!')

            except subprocess.CalledProcessError as e:
                message = f'{rawfilename} not rcloned to Google Drive'
                log_and_print(message)
                log_and_print(e,'error')

def _transfer_instrument_files(self, key, filename, inst_dir, rclone_staging_dir, status):
    print(f'Instrument file is {filename[key]}')
    # Get instrument filename; used for error reporting
    print(f'\nProcessing: {key}\n')
    print(f"GDrive rclone staging dir for instrument is {rclone_staging_dir}{key}")
    staging_dest = os.path.join(rclone_staging_dir, key)
    if not os.path.exists(staging_dest):
        log_and_print(f'Instrument dir {staging_dest} does not exist','error')
        self._ensure_staging_directory(staging_dest)
        
    source_file = os.path.join(inst_dir[key], filename[key])
    gdrive_dest = f"gdrive_eolfield:/{os.environ['PROJECT']}/EOL_data/RAF_data/{key}"

    # Use subprocess for rsync
    try:
        subprocess.run(['rsync', '-u', source_file, staging_dest], check=True)
        status[key]["stor"] = 'Yes-GDrive-staging'
        print(f'Finished rsyncing {key} file to staging location')
    except subprocess.CalledProcessError as e:
        log_and_print(f"rsync error for {source_file}: {e}")

    # Use subprocess for rclone
    try:
        subprocess.run(['rclone', 'copy', staging_dest, gdrive_dest, '--ignore-existing'], check=True)
        status[key]["ship"] = 'Yes-GDrive'
        print(f'Finished rclone to GDrive for {filename[key]}')
    except subprocess.CalledProcessError as e:
        log_and_print(f"rclone error for {source_file}: {e}. File not copied to GDrive",'error')


def _ensure_staging_directory(self, directory):
    try:
        os.makedirs(directory, exist_ok=True)  # Create if doesn't exist
        log_and_print('Created staging directory')
    except OSError as e:
        log_and_print(f'Failed to create staging directory {directory}: {e}','error')
        e = f'{rclone_staging_dir}{key} still does not exist. Cannot stage {key} data'
        log_and_print(e, 'error')

def ship_to_gdrive(self, data_dir, status, file_ext, inst_dir, filename, rclone_staging_dir):
    """Ships files to Google Drive via an rclone staging location.

    Args:
        data_dir (str): Base data directory.
        status (dict): Dictionary to track file transfer status.
        file_ext (dict): Dictionary of file extensions and their processing status.
        inst_dir (dict): Dictionary of instrument directories.
        filename (dict): Dictionary containing filenames for each instrument.
        rclone_staging_dir (str): Directory for staging files before rclone transfer.
    """

    print('\nPutting files to rclone staging location for shipment to Google Drive:\n')

    if ship_all_ADS:  
        self._ship_all_ads(inst_dir, rclone_staging_dir, status)
    else:
        for key in file_ext:
            print('\n' + key + '\n')
            if key == 'ADS' and not ship_ADS:
                # Skip ads if requested in fieldProc_setup.py
                continue
            if not os.path.exists(inst_dir[key]):
                log_and_print(f'Data dir {inst_dir[key]} does not exist', 'error')
                continue
            print(f"Data dir is {inst_dir[key]}")
            if filename[key] != '':
                self._transfer_instrument_files(key, data_dir, filename, inst_dir, rclone_staging_dir, status)

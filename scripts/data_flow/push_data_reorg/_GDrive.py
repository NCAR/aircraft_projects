import os
from _repetition import *

import os
import subprocess  # For better error handling with rsync
from datetime import datetime

def gdrive(self, data_dir, raw_dir, status, file_ext, inst_dir, filename, rclone_staging_dir):
    """Copies files to Google Drive using rclone (staging + upload).

    Args:
        data_dir: Base directory for data files.
        raw_dir: Directory for raw data files.
        status: Dictionary to track shipping status.
        file_ext: File extensions to ship.
        inst_dir: Directory mapping instrument names to data directories.
        filename: Mapping instrument names to specific filenames.
        rclone_staging_dir: Staging directory for rclone.
    """

    log_and_print('\nPutting files to rclone staging location for shipment to Google Drive:\n')

    def ship_ads_files():
        """Handles shipping of all .ads files."""
        message = 'Starting rsync process for all available .ads files'
        log_and_print(message)

        for rawfilename in os.listdir(inst_dir['ADS']):
            if rawfilename.endswith('.ads'):
                self._transfer_file(rawfilename, inst_dir['ADS'], rclone_staging_dir + 'ADS', status['ADS'])

        #  rclone all at once from the staging directory
        rclone_cmd = f'rclone copy {rclone_staging_dir}/ADS gdrive_eolfield:/{os.environ["PROJECT"]}/EOL_data/RAF_data/ADS --ignore-existing'
        self._run_rclone(rclone_cmd, "ADS")

    def _transfer_file(self, file, src_dir, dest_dir, status_entry):
        """Handles rsync and rclone steps for a single file.

        Args:
            file: The filename.
            src_dir: Source directory.
            dest_dir: Destination (rclone staging) directory.
            status_entry: The corresponding entry in the `status` dictionary.
        """
        rsync_cmd = f'rsync -u {os.path.join(src_dir, file)} {dest_dir}'
        if subprocess.run(rsync_cmd, shell=True).returncode == 0:  # Check rsync success
            status_entry["stor"] = 'Yes-GDrive-staging'
            log_and_print(f'{file} rsync successful!')
        else:
            log_and_print(f'{file} not copied to local staging', 'error')

        rclone_cmd = f'rclone copy {dest_dir} gdrive_eolfield:/{os.environ["PROJECT"]}/EOL_data/RAF_data/{os.path.basename(dest_dir)} --ignore-existing'
        self._run_rclone(rclone_cmd, file)

    def _run_rclone(self, cmd, name):
        """Executes rclone command and logs result."""
        if subprocess.run(cmd, shell=True).returncode == 0:
            status_entry["ship"] = 'Yes-GDrive'
            log_and_print(f"{name} rclone successful!")
        else:
            log_and_print(f"{name} not rcloned to Google Drive", 'error')

    def _process_instrument_data(self, key, data_dir, inst_dir, filename, rclone_staging_dir, status):
        # ... Your existing checks for directories and filenames

        try:
            print('rsync -u ' + filename[key] + ' ' + rclone_staging_dir + key)
            os.system('rsync -u ' + filename[key] + ' ' + rclone_staging_dir + key)
            status[key]["stor"] = 'Yes-GDrive-staging'
            # ... (Other rsync, rclone logic as before)
        except Exception as e:

    # Handle ADS files (if enabled)
    if ship_all_ADS:
        ship_ads_files()

    #  Handle other file extensions
    for key in file_ext:
        print(f'\n{key}\n')

        if ship_ADS is False and key == 'ADS':
            continue

        self._process_instrument_data(key, data_dir, inst_dir, filename, rclone_staging_dir, status)

    # ... (rest of your code)

# ... (helper functions like log_and_print remain the same)

def GDrive(self, data_dir, raw_dir, status, file_ext, inst_dir, filename, rclone_staging_dir):
    '''No NAS this project, so put files to Google Drive. Put
    zipped files if they exist.
    '''
    print('\nPutting files to rclone staging location for shipment to Google Drive:\n')

    # Keep this set to False unless you have time / bandwidth to ship all
    # ads files.
    if ship_all_ADS is True:
        message = 'Starting rsync process for all available .ads files'
        log_and_print(message)
        for rawfilename in os.listdir(inst_dir['ADS']):
            if rawfilename.endswith('.ads'):
                try:
                    os.chdir(inst_dir['ADS'])
                    os.system('rsync -u *.ads ' + rclone_staging_dir + 'ADS')
                    status["ADS"]["stor"] = 'Yes-GDrive-staging'
                    message = rawfilename + ' rsync successful!'
                    self.logger.info(message)
                    print(message)
                except Exception as e:
                    message = rawfilename + ' not copied to local staging'
                    log_and_print(message)
                    log_and_print(e,'error')
                try:
                    os.system('rclone copy ' + rclone_staging_dir + '/ADS' + ' gdrive_eolfield:/' + os.environ[
                        'PROJECT'] + '/EOL_data/RAF_data/ADS --ignore-existing')
                    status["ADS"]["ship"] = 'Yes-GDrive'
                    message = rawfilename + ' rclone successful!'
                    log_and_print(message)
                except:
                    message = rawfilename + ' not rcloned to Google Drive'
                    log_and_print(message)
                    self.logger.error(e)
                    log_and_print(e,'error')
            else:
                pass
    else:
        # Loop through requested file extensions to be copied to GDrive
        for key in file_ext:
            print('\n' + key + '\n')

            if ship_ADS is False and key == 'ADS':
                # Skip ads if requested in fieldProc_setup.py
                continue
            else:
                # For all requested extensions, confirm local dir where
                # data file is located exists
                try:
                    print("Data dir is " + inst_dir[key])
                    os.path.exists(inst_dir[key])
                except Exception as e:
                    log_and_print('Data dir ' + inst_dir[key] + ' does not exist')
                    log_and_print(e,'error')
                    continue

            if filename[key] != '':
                print('Instrument file is ' + filename[key])
                # Get instrument filename; used for error reporting
                data_dir, file_name = os.path.split(filename[key])

                # For all requested extensions, confirm there is an
                # instrument-specific dir within the rclone_staging_dir
                print("GDrive rclone staging dir for instrument is " +
                      rclone_staging_dir + key)
                if not os.path.exists(rclone_staging_dir + key):
                    e = 'Instrument dir ' + rclone_staging_dir + key + \
                        ' does not exist'
                    print(e)
                    self.logger.error(e)
                    # Attempt to create needed dir
                    print('Attempt to create dir ' + rclone_staging_dir +
                          key)
                    try:
                        pass
                        os.system('mkdir ' + rclone_staging_dir + key)
                    except Exception as e:
                        print('Make dir ' + rclone_staging_dir + key +
                              ' failed')
                        print(e)
                        self.logger.error(e)
                        continue
                    # Confirm dir exists again
                    if not os.path.exists(rclone_staging_dir + key):
                        e = rclone_staging_dir + '/' + key + \
                            ' still does not exist. Cannot stage ' + \
                            key + ' data'
                        print(e)
                        self.logger.error(e)
                        continue

                # Copy files to staging area and match desired rclone structure
                try:
                    print('rsync -u ' + filename[key] + ' ' + rclone_staging_dir + key)
                    # os.system doesn't throw an error so this try/except
                    # never fails even if rsync fails. Need to use subprocess.Popen()
                    # This is true every place os.system is used in a try/except
                    os.system('rsync -u ' + filename[key] + ' ' + rclone_staging_dir + key)
                    status[key]["stor"] = 'Yes-GDrive-staging'
                    print(datetime.datetime.now().time())
                    print('Finished rsyncing ' + key + ' file to staging location')
                    print('')

                except Exception as e:
                    print('Error rsyncing data file to staging location ' + file_name)
                    print(e)
                    self.logger.error(e)
                    continue

                # Use rclone to sync files to GDrive. Could rclone all at
                # once, but chose to sync a file at a time so can report
                # status.
                try:
                    print('rclone copy ' + rclone_staging_dir + key +
                          ' gdrive_eolfield:' + os.environ['PROJECT'] +
                          '/EOL_data/RAF_data/' + key + ' --ignore-existing')
                    os.system('rclone copy ' + rclone_staging_dir + key +
                              ' gdrive_eolfield:' + os.environ['PROJECT'] +
                              '/EOL_data/RAF_data/' + key +
                              ' --ignore-existing')
                    status[key]["ship"] = 'Yes-GDrive'
                    print(datetime.datetime.now().time())
                    print('Finished rclone to GDrive for ' + file_name)
                    print('')

                except Exception as e:
                    print('Error with rclone process for ' + file_name +
                          '. File not copied to GDrive')
                    print(e)
                    self.logger.error(e)
                    continue
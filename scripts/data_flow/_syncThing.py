import os, sys
import _logging
import subprocess  # For more reliable error handling with rsync and rclone
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import ship_all_ADS, ship_ADS, syncthing_staging_dir

myLogger = _logging.MyLogger()
class StageSyncThing:
    """Ships files to Google Drive via an rclone staging location.

        Args:
            status (dict): Dictionary to track file transfer status.
            file_ext (dict): Dictionary of file extensions and their processing status.
            inst_dir (dict): Dictionary of instrument directories.
            filename (dict): Dictionary containing filenames for each instrument.
    """
    def __init__(self, status, file_ext, inst_dir, filename,flight):
        self.stat = status
        self.flight = flight
        myLogger.log_and_print('\nPutting files to rclone staging location for shipment to Google Drive:\n')
        if ship_all_ADS:
            self._ship_all_ads(inst_dir, syncthing_staging_dir)
        else:
            for key in file_ext:
                print('\n' + key + '\n')
                if key == 'ADS' and not ship_ADS:
                    # Skip ads if requested in fieldProc_setup.py
                    continue
                if not os.path.exists(inst_dir[key]):
                    myLogger.log_and_print(f'Data dir {inst_dir[key]} does not exist', 'error')
                    continue
                print(f"Data dir is {inst_dir[key]}")
                if filename[key] != '':
                    self._transfer_instrument_files(key, filename, inst_dir, syncthing_staging_dir)
            self._sync_raw(syncthing_staging_dir, inst_dir)

    def _ship_all_ads(self, inst_dir, syncthing_staging_dir):
        ''' Ship all ads files to the specificed syncthing_staging_dir '''
        # ... (Implementation for shipping all ADS files) ...
        message = 'Starting rsync process for all available .ads files'
        myLogger.log_and_print(message)
        for rawfilename in os.listdir(inst_dir['ADS']):
            if rawfilename.endswith('.ads'):
                try:
                    os.chdir(inst_dir['ADS'])
                    subprocess.run(f'rsync -u *.ads {syncthing_staging_dir}/ADS', check = True)
                    self.stat["ADS"]["stor"] = 'Yes-syncthing-staging'
                    myLogger.log_and_print(f'{rawfilename} rsync successful!')
                except subprocess.CalledProcessError as e:
                    myLogger.log_and_print('{rawfilename} not copied to local staging')
                    myLogger.log_and_print(e,'error')

    def _transfer_instrument_files(self, key, filename, inst_dir, syncthing_staging_dir):
        ''' Transfer instrument files to the syncthing_staging_dir '''
        print(f'Instrument file is {filename[key]}')
        # Get instrument filename; used for error reporting
        myLogger.log_and_print(f'\nTransferring: {key}\n')
        myLogger.log_and_print(f"syncthing staging dir for instrument is {syncthing_staging_dir}/{key}")
        staging_dest = os.path.join(syncthing_staging_dir, key)
        if not os.path.exists(staging_dest):
            myLogger.log_and_print(f'Instrument dir {staging_dest} does not exist. \n \
                                Attempting to create staging directory.','warning')
            self._ensure_staging_directory(staging_dest,key)
        if key == 'ADS':
            myLogger.log_and_print(f'Looking for all ADS files matching pattern: *{self.flight}.ads')
            import glob
            matching_files = glob.glob(f'{inst_dir[key]}/*{self.flight}.ads')
            # Transfer each matching file
            for ads_file in matching_files:
                source_file = os.path.join(inst_dir[key], ads_file)
                self._rsync_file(source_file, staging_dest, key)

    # Use subprocess for rsync
        else:
            source_file = os.path.join(inst_dir[key], filename[key])
            self._rsync_file(source_file, staging_dest, key)
    def _sync_raw(destination, inst_dir):
        ''' Sync SATCOM data to the specified destination '''
        try:
            subprocess.run(['rsync', '-ur', f'{inst_dir['ads']}/satcom/', f'{syncthing_staging_dir}/satcom/'], check=True)
            myLogger.log_and_print(f'Successfully synced SATCOM data to {syncthing_staging_dir}/satcom/')
        except subprocess.CalledProcessError as e:
            myLogger.log_and_print(f"did not sync SATCOM data: {e}", 'warning')
        #Sync CAMERA images if it exists
        try:
            subprocess.run(['rsync', '-ur', f'{inst_dir['ads']}/CAMERA/', f'{syncthing_staging_dir}/CAMERA/'], check=True)
            myLogger.log_and_print(f'Successfully synced camera imagery to {syncthing_staging_dir}/CAMERA/')
        except subprocess.CalledProcessError as e:
            myLogger.log_and_print(f"did not sync camera imagery: {e}", 'warning')

    def _rsync_file(self, source_file, destination, key):
        ''' Rsync a file to a destination '''
        try:
            # Perform the rsync operation
            subprocess.run(['rsync', '-u', source_file, destination], check=True)
            self.stat[key]["stor"] = 'Yes-syncthing-staging'
            file_name = os.path.basename(source_file)
            myLogger.log_and_print(f'Successfully synced {file_name} to staging location')
        except subprocess.CalledProcessError as e:
            myLogger.log_and_print(f"rsync error for {source_file}: {e}", 'error')
    def _ensure_staging_directory(self, directory, key):
        ''' Check if the staging directory exists. If not, attempt to create it. '''
        try:
            os.makedirs(directory, exist_ok=True)  # Create if doesn't exist
            myLogger.log_and_print('Created syncthing staging directory')
        except OSError as e:
            myLogger.log_and_print(f'Failed to create staging directory {directory}: {e}','error')
            e = f'{syncthing_staging_dir}{key} still does not exist. Cannot stage {key} data'
            myLogger.log_and_print(e, 'error')

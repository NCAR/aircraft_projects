import os
import re
import sys
import ftplib
import _logging 
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import user, password,  ftp_site, password, ftp_data_dir, ship_ADS, ship_all_ADS

myLogger = _logging.MyLogger()
class TransferFTP:
    def __init__(self, status, file_ext, inst_dir, filename):
        """Transfers files to an FTP server.

        Args:
            data_dir (str): Base data directory (not directly used in this function).
            status (dict): Dictionary to track file transfer status.
            file_ext (dict): Dictionary of file extensions and their processing status.
            inst_dir (dict): Dictionary of instrument directories.
            filename (dict): Dictionary containing filenames for each instrument.
        """
        self.stat = status
        try:
            self._connect_to_ftp()
        except ftplib.all_errors as e:
            myLogger.log_and_print(f'Error connecting to FTP site {ftp_site}: {e}','error')
            return

        print('Putting files to FTP site:')

        if ship_all_ADS:
            self._transfer_all_ads(inst_dir)
        else:
            self._transfer_selected_files(file_ext, inst_dir, filename)

        self.ftp.quit()

        # Revert PMS2D ftp special case
        inst_dir['PMS2D'] = re.sub('PMS2D/', '',inst_dir['PMS2D'])
        print("After FTP: " + inst_dir['PMS2D'])


    def _connect_to_ftp(self):
        ''' Attempt to connect to FTP server '''
        message = f'Opening FTP connection to: {ftp_site}'
        myLogger.log_and_print(message)
        self.ftp = ftplib.FTP(ftp_site)
        self.ftp.login(user, password)


    def _transfer_all_ads(self, inst_dir):
        ''' Implementation for transferring all ADS files ... '''
        message = 'Starting ftp process for all available .ads files'
        myLogger.log_and_print(message)
        for rawfilename in os.listdir(inst_dir['ADS']):
            if rawfilename.endswith('.ads'):
                try:
                    os.chdir(inst_dir['ADS'])
                    self.ftp.cwd(f'/{ftp_data_dir}/ADS')
                    self.ftp.storbinary(f'STOR {rawfilename}', open(rawfilename, 'rb'))
                    self.stat["ADS"]["stor"] = 'Yes-FTP'
                    message = f'{rawfilename} ftp successful!'
                    myLogger.log_and_print(message)
                except Exception as e:
                    message = f'{rawfilename} not sent'
                    myLogger.log_and_print(f'{message}/n{e}')


    def _transfer_selected_files(self, file_ext, inst_dir, filename):
        """
        Implementation to only transfer selected files based in file extensions,
        instrument directories and filenames
        """
        for key in file_ext:
            if key == 'ADS' and not ship_ADS:
                continue

            if filename[key] == '':
                continue

            try:
                self._create_ftp_dir_if_needed(key)
                self._transfer_file(key, inst_dir[key], filename[key])
            except (ftplib.all_errors, OSError) as e:
                myLogger.log_and_print(f"Error processing {key}: {e}",'error')


    def _create_ftp_dir_if_needed(self, instrument):
        ''' Create instrument dir on remote ftp site if needed '''
        remote_dir = f'/{ftp_data_dir}/{instrument}'
        try:
            self.ftp.cwd(remote_dir)  # Check if exists
        except ftplib.all_errors:
            try:
                self.ftp.mkd(remote_dir)  # Create if it doesn't
                myLogger.log_and_print(f"Created FTP directory: {remote_dir}")
            except ftplib.all_errors as e:
                myLogger.log_and_print(f"Failed to create FTP directory {remote_dir}: {e}",'error')


    def _transfer_file(self, instrument, local_dir, file_name, ):
        ''' Transfer file to ftp site '''
        remote_path = f'/{ftp_data_dir}/{instrument}/{file_name}'
        if remote_path not in self.ftp.nlst():  # Check for existing file 
            try:
                with open(os.path.join(local_dir, file_name), 'rb') as file:
                    self.ftp.storbinary(f'STOR {remote_path}', file)
                self.stat[instrument]["stor"] = 'Yes-FTP'
                print(f"Successfully transferred {file_name}")
            except (ftplib.all_errors, OSError) as e:
                myLogger.log_and_print(f"Error transferring {file_name}: {e}",'error')

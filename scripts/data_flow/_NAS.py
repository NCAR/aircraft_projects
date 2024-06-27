import os
import sys
import _logging
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import  NAS_permanent_mount, nas_url, nas_mnt_pt, sendzipped, zip_ADS, ship_ADS
myLogger = _logging.MyLogger()

class DataShipping:
    def __init__(self,file_ext, filename,status, process, reprocess, inst_dir, flight, project,final_message):
        """
        Beginning of Shipping
        """
        self.stat = status
        self.zip_dir = '/tmp/'
        if NAS_permanent_mount is False:
            # Mount NAS
            command = f"sudo /bin/mount -t nfs {nas_url} {nas_mnt_pt}"
            message = '\r\nMounting nas: ' + command
            myLogger.log_and_print(message)

            os.system(command)

        # Put copies of files to local store
        # in dirs to sync to ftp site in Boulder...
        self.nas_sync_dir = f'{nas_mnt_pt}/FTP_sync/EOL_data/RAF_data/'
        # and in dirs for local use...
        self.nas_data_dir = f'{nas_mnt_pt}/EOL_data/RAF_data/'
        ##Refactor to only print once with a new line
        message = "\n*************** Copy files to NAS scratch area ***************"
        myLogger.log_and_print(message)
        """
        Refactoring to remove if statements. Added dir_key so that if it is a PMS2D file then it syncs into a directory
        """
        for key in file_ext:
            dir_key = key
            if key == 'PMS2D':
                dir_key = f'{key}/'
            message = f'Copying {filename[key]} to {self.nas_data_dir}/{dir_key}'
            myLogger.log_and_print(message)
            self.stat[key]["stor"] = self.rsync_file(
                filename[key], f'{self.nas_data_dir}/{dir_key}'
            )
            
        self.setup_NAS(process, reprocess, file_ext, inst_dir, flight, project, final_message, filename)

    def _zip_ads(self, filename):
        # Now only zip up the ADS file, if requested
        raw_dir, rawfilename = os.path.split(filename["ADS"])
        print(f"zipping {rawfilename}")
        result = self.zip_dir + rawfilename + '.bz2'
        print(f"rawfilename = {result}")
        os.chdir(raw_dir)
        # if not os.path.exists(zip_raw_file):
        print("Compressing ADS file with command:")
        command = f"bzip2 -kc {rawfilename} > {result}"
        myLogger.log_and_print(command)
        os.system(command)
        print("")
        return result
    
    def rsync_file(self, file, out_dir):
        '''
        Rsync file to output dir and record success status
        '''
        command = 'rsync '+file+" " + out_dir
        if os.system(command) == 0:
            proc_file = 'Yes-NAS'
            return(str(proc_file))
        else:
            rsync_message = '\nERROR!: syncing file: ' + command + '\n'
            self.print_message(rsync_message)

        
    def setup_NAS(self, process, reprocess, file_ext, inst_dir, flight, project, final_message, filename):
        # Put file onto NAS for BTSyncing back home.
        print("")
        print("***** Copy files to NAS sync area for transfer back home *****")

        if reprocess or not process:
            NAS_message = [
                "***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n",
                "Reprocessing, so assume ADS already shipped during first processing\n",
                "If this is not the case, run the following commands when this script is complete:\n\n",
                f"cp /home/data/Raw_Data/{project}/*{flight}.ads {self.nas_sync_dir}/ADS\n",
                f"cp /home/data/Raw_Data/{project}/*{flight}.ads {self.nas_data_dir}/ADS\n\n",
                "***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n"
            ]
            final_message += ''.join(NAS_message)
            self.final_message = final_message
        if zip_ADS:
            zip_raw_file = self._zip_ads(filename)
        else:
            print('.ads file not being zipped due to preference')

        # mount the NAS and put files to it
        if NAS_permanent_mount is False:
            # Mount NAS
            command = f"sudo /bin/mount -t nfs {nas_url} {nas_mnt_pt}"
            print('\r\nMounting nas: '+command)
            os.system(command)

        for key in file_ext:
            os.chdir(inst_dir[key])
            if key == "ADS" and ship_ADS is True:
                if zip_ADS is True:
                    print(f'Copying {zip_raw_file} file to {self.nas_sync_dir}/ADS')
                    self.rsync_file(zip_raw_file, f'{self.nas_sync_dir}/ADS')
                else:
                    print(f'Copying {filename[key]} file to {self.nas_sync_dir}/ADS')
                    self.stat[key]["ship"] = self.rsync_file(filename[key], f'{self.nas_sync_dir}/{key}')
            elif key == "PMS2D":
                print(f'Copying {filename[key]} file to {self.nas_sync_dir}/PMS2D')
                self.stat[key]["ship"] = self.rsync_file(filename[key], f'{self.nas_sync_dir}/PMS2D')
            elif sendzipped is True:
                print(f'Copying {filename[key]}.zip file to {self.nas_sync_dir}/{key}')
                self.stat[key]["ship"] = self.rsync_file(
                    f'{filename[key]}.zip', f'{self.nas_sync_dir}/{key}'
                )
            else:
                print(f'Copying {filename[key]} file to {self.nas_sync_dir}/{key}')
                self.stat[key]["ship"] = self.rsync_file(filename[key], f'{self.nas_sync_dir}/{key}')
            print('Done')
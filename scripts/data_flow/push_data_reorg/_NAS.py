import os
from _repetition import *

def setup_shipping(self, file_ext, filename, process, reprocess, status):
    """
    Beginning of Shipping
    """
    if NAS_permanent_mount is False:
        # Mount NAS
        command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
        message = '\r\nMounting nas: ' + command
        log_and_print(message)

        os.system(command)

    # Put copies of files to local store
    # in dirs to sync to ftp site in Boulder...
    self.nas_sync_dir = nas_mnt_pt + '/FTP_sync/EOL_data/RAF_data/'
    # and in dirs for local use...
    self.nas_data_dir = nas_mnt_pt + '/EOL_data/RAF_data/'
    ##Refactor to only print once with a new line
    message = "\n*************** Copy files to NAS scratch area ***************"
    log_and_print(message)
    """
    Refactoring to remove if statements. Added dir_key so that if it is a PMS2D file then it syncs into a directory
    """
    for key in file_ext:
        dir_key = key
        if key == 'PMS2D':
            dir_key = key +'/'
        message = 'Copying ' + filename[key] + ' to ' + self.nas_data_dir + '/' + dir_key
        log_and_print(message)
        status[key]["stor"] = self.rsync_file(filename[key], self.nas_data_dir + '/' + dir_key)



    return self.nas_data_dir, self.nas_sync_dir

    def setup_NAS(self, process, reprocess, file_ext, inst_dir, status, flight, project, email, final_message, filename, nas_sync_dir, nas_data_dir):
        # Put file onto NAS for BTSyncing back home.
        print("")
        print("***** Copy files to NAS sync area for transfer back home *****")

        if reprocess or (not reprocess and not process):
            final_message = final_message + '\n***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'
            final_message = final_message + 'Reprocessing so assume ADS already shipped during first processing\n'
            final_message = final_message + 'If this is not the case, run\n\n'
            final_message = final_message + '"cp /home/data/Raw_Data/' + project + '/*' + flight + '.ads ' + nas_sync_dir + '/ADS"\n\n'
            final_message = final_message + '"cp /home/data/Raw_Data/' + project + '/*' + flight + '.ads ' + nas_data_dir + '/ADS"\n\n'
            final_message = final_message + 'when this script is complete\n\n'
            final_message = final_message + '***CAUTION*CAUTION*CAUTION*CAUTION*CAUTION*CAUTION***\n\n'

        if zip_ADS:
            # Now only zip up the ADS file, if requested
            raw_dir, rawfilename = os.path.split(filename["ADS"])
            print("zipping " + rawfilename)
            zip_raw_file = zip_dir + rawfilename + '.bz2'
            print("rawfilename = " + zip_raw_file)
            os.chdir(raw_dir)
            # if not os.path.exists(zip_raw_file):
            print("Compressing ADS file with command:")
            command = "bzip2 -kc " + rawfilename + " > " + zip_raw_file
            print(command)
            os.system(command)
            print("")
        else:
            print('.ads file not being zipped due to preference')

        # mount the NAS and put files to it
        if NAS_permanent_mount is False:
            # Mount NAS
            command = "sudo /bin/mount -t nfs " + nas_url + " " + nas_mnt_pt
            print('\r\nMounting nas: '+command)
            os.system(command)

        for key in file_ext:
            os.chdir(inst_dir[key])
            if (key == "ADS"):
                if ship_ADS is True:
                    if zip_ADS is True:
                        print('Copying ' + zip_raw_file + ' file to ' + nas_sync_dir + '/ADS')
                        self.rsync_file(zip_raw_file, nas_sync_dir + '/ADS')
                        print('Done')
                    else:
                        print('Copying ' + filename[key] + ' file to ' + nas_sync_dir + '/ADS')
                        status[key]["ship"] = self.rsync_file(filename[key], nas_sync_dir + '/' + key)
                        print('Done')
                else:
                    pass
            elif (key == "PMS2D"):
                print('Copying ' + filename[key] + ' file to ' + nas_sync_dir + '/PMS2D')
                status[key]["ship"] = self.rsync_file(filename[key], nas_sync_dir + '/PMS2D')
                print('Done')
            else:
                if sendzipped is True:
                    print('Copying ' + filename[key] + '.zip file to ' + nas_sync_dir + '/' + key)
                    status[key]["ship"] = self.rsync_file(filename[key] + '.zip', nas_sync_dir + '/' + key)
                    print('Done')
                else:
                    print('Copying ' + filename[key] + ' file to ' + nas_sync_dir + '/' + key)
                    status[key]["ship"] = self.rsync_file(filename[key], nas_sync_dir + '/' + key)
                    print('Done')
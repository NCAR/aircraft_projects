from _logging import MyLogger
import os
myLogger = MyLogger()

class SetupZip:
    def __init__(self, file_ext, data_dir, filename, inst_dir):
        """
        ZIP up the files as per expectations back home
        this only affects non-ads files
        """
        self.myLogger = myLogger
        myLogger.log_and_print(filename)
        for key in file_ext:
            if key == "ADS":
                myLogger.log_and_print("Raw .ads file found but not zipping, if zip_ads is set, will bzip .ads file next.")
            elif key == "PMS2D":
                myLogger.log_and_print("Raw .2d file found but not zipping.")
            else:
                data_dir, file_name = os.path.split(filename[key])
                message = f"{key} filename = {file_name}"
                myLogger.log_and_print(message)
                message = f"data_dir = {data_dir}"
                myLogger.log_and_print(message)
                self.zip_file(file_name, inst_dir[key])
                
    def zip_file(self, filename, datadir):
        """
        Create Zip file
        """
        myLogger.log_and_print(f"zipping {filename} in {datadir}")
        os.chdir(datadir)
        command = "zip " + filename + ".zip " + filename
        if os.system(command) != 0:
            message = "\nError zipping up " + filename + " with command:\n  "
            message = message + command
            myLogger.log_and_print(message, 'error')
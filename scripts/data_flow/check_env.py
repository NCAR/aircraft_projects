##Script to be used across files to check that the environment variables are set correctly

import os, sys

#Check that the environment variables are set and exit if they are not  
def check_env_vars(*vars):
    missing_vars = [var for var in vars if not os.environ.get(var)]
    if missing_vars:
        message = f"Missing environment variables: {', '.join(missing_vars)}. Please set these variables and try again."
        try:
            sys.exit(message)
        except SystemExit as e:
            print(e.code)
            os._exit(1)
        
#If the environment variables are set, check that they point to an existing directory
def check():
    check_env_vars('PROJ_DIR', 'PROJECT', 'AIRCRAFT')
    full_proj_dir = os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT']
    if not os.path.exists(full_proj_dir):
        message = f"The specified project directory does not exist: {full_proj_dir}\n Please make sure the environment variables PROJ_DIR, PROJECT, and AIRCRAFT are set correctly."
        sys.exit(message)

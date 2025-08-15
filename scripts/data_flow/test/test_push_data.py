import pytest
import sys
import os
from check_env import check
check() ##Check that the environment variables are set correctly
from unittest.mock import patch
from collections import OrderedDict
from const_tests import env_vars
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import main
from unittest.mock import patch, MagicMock

from pyfakefs.fake_filesystem_unittest import Patcher

user_inputs = [
    'tf01',  # for readFlight
    'test@example.com',    # for readEmail
    'S'
]



# Mock os.environ.get to use our env_vars
def mock_getenv(var_name):
    return env_vars.get(var_name)

# Mock input to use our user_inputs
def mock_input(prompt):
    return user_inputs.pop(0) if user_inputs else ""

@pytest.fixture
def push_data():
    env_vars = {  # Define environment variables here
        "PROJECT": "project_name",
        "AIRCRAFT": "C130_N130AR",
        "RAW_DATA_DIR": "raw_data_directory",
        "DATA_DIR": "data_directory",
        "PROJ_DIR": "project_directory",
        "FLIGHT": "tf01",
        "EMAIL": "test@example.com"
    }
    with (patch.dict('os.environ', env_vars), 
          patch('builtins.input', side_effect=mock_input),
          patch('smtplib.SMTP') as mock_smtp,
          patch('_process.Process') as mock_process_class):
        
        # Create a mock Process instance that sets date when extract_takeoff_lrt is called
        mock_process_instance = MagicMock()
        mock_process_instance.date = "20241204"  # Set the date directly
        
        # Make the Process class return our mock instance
        mock_process_class.return_value = mock_process_instance
        
        mock_smtp.return_value = MagicMock()
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.return_value = {} 
        
        with Patcher() as patcher:
    # access the fake_filesystem object via patcher.fs
            patcher.fs.create_dir('raw_data_directory/PROJECT_NAME')
            patcher.fs.create_dir('data_directory/PROJECT_NAME')
            patcher.fs.create_dir('project_directory/project_name/C130_N130AR/Production')
            patcher.fs.create_file('raw_data_directory/PROJECT_NAME/12042024_130000tf01.ads')
            patcher.fs.create_file('data_directory/PROJECT_NAME/PROJECT_NAMEtf01.nc')
            patcher.fs.create_dir('/home/local/aircraft_QAtools_notebook')
        #fs.create_file('data_directory/PROJECT_NAME/email.addr.txt')
            with patch('subprocess.run') as mock_run:
                def mock_subprocess_run(command, **kwargs):
                    if 'flt_time' in command:
                        # Return a proper mock result for flt_time command
                        mock_result = MagicMock()
                        mock_result.returncode = 0
                        mock_result.stdout = (
                            "data_directory/PROJECT_NAME/project_nametf01.nc:project_name:tf01:\n"
                            "Using variable GSPD\n"
                            "Takeoff: Wed Dec 4 01:09:51 2024\n"
                            "Landing: Wed Dec 4 06:51:06 2024\n"
                        )
                        mock_result.stderr = ""
                        return mock_result
                    else:
                        # Return a generic successful result for other commands
                        mock_result = MagicMock()
                        mock_result.returncode = 0
                        mock_result.stdout = ""
                        mock_result.stderr = ""
                        return mock_result
                mock_run.side_effect = mock_subprocess_run
                #mock_run.return_value = MagicMock(returncode=0)
                
                yield main()

def test_setup_constants(push_data):
    # Assertions remain the same
    assert push_data is None
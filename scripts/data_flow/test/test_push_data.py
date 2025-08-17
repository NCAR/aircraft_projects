import pytest
import sys
import os
from check_env import check
check()
from unittest.mock import patch, MagicMock
from collections import OrderedDict
from const_tests import env_vars
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import main
from pyfakefs.fake_filesystem_unittest import Patcher

# Other parts of your code remain the same...
user_inputs = [
    'tf01',  # for readFlight
    'test@example.com',    # for readEmail
    'S'
]

def mock_getenv(var_name):
    return env_vars.get(var_name)

def mock_input(prompt):
    return user_inputs.pop(0) if user_inputs else ""

@pytest.fixture
def push_data():
    env_vars = {
        "PROJECT": "project_name",
        "AIRCRAFT": "C130_N130AR",
        "RAW_DATA_DIR": "raw_data_directory",
        "DATA_DIR": "data_directory",
        "PROJ_DIR": "project_directory",
        "FLIGHT": "tf01",
        "EMAIL": "test@example.com"
    }

    # Patch the _process.Process.extract_takeoff_lrt method directly
    with (patch.dict('os.environ', env_vars), 
          patch('builtins.input', side_effect=mock_input),
          patch('smtplib.SMTP') as mock_smtp,
          patch('_process.Process.extract_takeoff_lrt') as mock_extract_takeoff,
          patch('subprocess.run') as mock_run):  # Keep this mock for other calls
        
        # Define the side effect for the mocked method
        def mock_extract_takeoff_lrt(self, filename, raw_dir):
            self.date = "20241204" # Set the date as a side effect of the mock call
            print("Mocked extract_takeoff_lrt was called. Date set.")

        mock_extract_takeoff.side_effect = mock_extract_takeoff_lrt
        
        # Configure other mocks
        mock_smtp.return_value = MagicMock()
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.return_value = {}

        # Correctly mock subprocess.run for other calls
        mock_run.return_value = MagicMock(returncode=0)

        with Patcher() as patcher:
            patcher.fs.create_dir('raw_data_directory/PROJECT_NAME')
            patcher.fs.create_dir('data_directory/PROJECT_NAME')
            patcher.fs.create_dir('project_directory/project_name/C130_N130AR/Production')
            patcher.fs.create_file('raw_data_directory/PROJECT_NAME/12042024_130000tf01.ads')
            patcher.fs.create_file('data_directory/PROJECT_NAME/PROJECT_NAMEtf01.nc')
            patcher.fs.create_file('data_directory/PROJECT_NAME/PROJECT_NAMEtf01s.nc')
            patcher.fs.create_file('data_directory/PROJECT_NAME/PROJECT_NAMEtf01h.nc')
            patcher.fs.create_dir('/home/local/aircraft_QAtools_notebook')
            
            yield main()

def test_setup_constants(push_data):
    assert push_data is None
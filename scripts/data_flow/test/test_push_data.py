import pytest
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import *
from unittest.mock import patch
from collections import OrderedDict
from const_tests import env_vars
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import main
from unittest.mock import patch, MagicMock

from pyfakefs.fake_filesystem_unittest import Patcher

user_inputs = [
    'tf01',  # for readFlight
    'test@example.com'    # for readEmail
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
    with (patch.dict('os.environ', env_vars), patch('builtins.input', side_effect=mock_input),patch('smtplib.SMTP') as mock_smtp):
        mock_smtp.return_value = MagicMock()
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.return_value = {} 
        with Patcher() as patcher:
    # access the fake_filesystem object via patcher.fs
            patcher.fs.create_dir('raw_data_directory/PROJECT_NAME')
            patcher.fs.create_dir('data_directory/PROJECT_NAME')
            patcher.fs.create_dir('/project_directory/project_name/C130_N130AR/Production')
            patcher.fs.create_file('raw_data_directory/PROJECT_NAME/12042024_130000tf01.ads')
            patcher.fs.create_dir('/data_directory/PROJECT_NAME/data_directory/PROJECT_NAME')
            patcher.fs.create_dir('/home/local/aircraft_QAtools_notebook')
        #fs.create_file('data_directory/PROJECT_NAME/email.addr.txt')
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                yield main()

def test_setup_constants(push_data):
    # Assertions remain the same
    assert push_data is None
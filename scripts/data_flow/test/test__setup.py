import pytest
import sys
import os
from check_env import check
check() ##Check that the environment variables are set correctly
from unittest.mock import MagicMock, patch
from collections import OrderedDict
from const_tests import env_vars, mock_input
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from _setup import Setup, default_emails
from _process import Process
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
    if 'Input flight' in prompt:
        return "tf01"
    elif 'email' in prompt:
        return "test@example.com"
    return input(prompt)

@pytest.fixture
def setup():
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
            patcher.fs.create_dir('/raw_data_directory/PROJECT_NAME')
            patcher.fs.create_dir('/data_directory/PROJECT_NAME')
            patcher.fs.create_dir('/project_directory/project_name/C130_N130AR/Production')
            patcher.fs.create_file('/raw_data_directory/PROJECT_NAME/12042024_130000tf01.ads')
            patcher.fs.create_file('/raw_data_directory/PROJECT_NAME/tf01.nc')
            patcher.fs.create_dir('/home/local/aircraft_QAtools_notebook')
        #fs.create_file('data_directory/PROJECT_NAME/email.addr.txt')
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                yield Setup()

@pytest.fixture
def setup_zip_env(setup):
    # Extend the existing setup fixture for setup_zip requirements
    setup.zip_file = MagicMock()
    yield {
        "setup": setup,  # The setup instance from the previous fixture
    }

def test_setup_constants(setup):
    # Assertions remain the same
    assert setup.PROJECT == "project_name"
    assert setup.AIRCRAFT == "C130_N130AR"
    assert setup.RAW_DIR == "raw_data_directory/PROJECT_NAME/"
    assert setup.DATA_DIR == "data_directory/PROJECT_NAME/"
    #assert isinstance(setup.filename, dict)
    assert setup.FLIGHT == "tf01"
    assert setup.EMAIL == default_emails+['test@example.com']
    assert setup.FILENAME == {}


@pytest.fixture
def setup_process_env(setup):
    # Extend the existing setup fixture for setup_zip requirements
    yield Process(setup.FILE_EXT, setup.DATA_DIR, setup.FLIGHT, setup.FILENAME, setup.RAW_DIR, 
                    setup.STATUS, setup.PROJECT,setup.AIRCRAFT, setup.INST_DIR,setup.RATE, setup.CONFIG_EXT,
                    setup.FILE_TYPE,setup.PROJ_DIR,setup.FILE_PREFIX)

def test_process(setup_process_env):
    result = setup_process_env._reorder_nc(setup_process_env.ncfile)
    assert result == 'Yes'
    assert setup_process_env.date == '12042024'
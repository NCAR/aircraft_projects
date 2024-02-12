import sys
import os
import pytest
from unittest.mock import patch
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import FieldData  # Assuming this is where 'find_file' is
from const_tests import *

@pytest.fixture
def fielddata():
    with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input), patch('os.listdir', return_value=listdir_return_value)):
        return FieldData()

@pytest.mark.parametrize(
    "datalist, fileext, reprocess, expected_datafile, user_inputs", [
        # Test Case 1:
        (['test_file1.nc','/sample/path.nc'], 'nc', False, 'test_file1.nc', None), ##If reprocess is false, then ship is set to true and it should return the first file in the datalist
        (['test_file1.nc','/sample/path.nc'], 'nc', True, '/sample/path.nc', ['N','Y']),  #If reprocess is set to false, then the user selects which file to reprocess
        # ... more test cases with different file paths, flags, etc.
    ]
)
def test_step_through_files(fielddata, datalist, fileext, reprocess, expected_datafile,user_inputs):
    def mock_input(prompt):
        return user_inputs.pop(0) if user_inputs else ""
    # Mocking glob.glob (you can also use monkeypatch if preferred)
    with patch('builtins.input', side_effect=mock_input):

        actual_datafile = fielddata.step_through_files(datalist,fileext,reprocess)
        assert actual_datafile == expected_datafile
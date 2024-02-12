import fnmatch
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
    "test_id, flight, project, filetype, fileext, flag, reprocess,  expected_datafile, expected_flag, user_inputs", [
        # Test Case 1:
        ('test1', 'tf01', 'CAESAR', 'h','nc',True,True,'/Users/srunkel/dev/projects/CAESAR/ttCAESARtf01h.nc', True,['N','Y']),
        ('test2', 'tf01', 'CAESAR', 'h','ict',False,False,'/Users/srunkel/dev/projects/CAESAR/CAESARtf01h.ict',False, None),
        # ... more test cases with different file paths, flags, etc.
    ]
)
def test_find_file(fielddata, test_id, flight, project, filetype, fileext, flag, reprocess, expected_datafile, expected_flag, user_inputs):
    fake_file_list = [
        '/Users/srunkel/dev/projects/CAESAR/CAESARtf01h.nc',
        '/Users/srunkel/dev/projects/CAESAR/ttCAESARtf01h.nc',# Matches pattern in 'else' branch
        '/Users/srunkel/dev/projects/CAESAR/CAESARtf01h.ict',# Matches pattern in 'if' branch
        '/Users/srunkel/dev/projects/CAESAR/atf01h.ict'
        # ... more fake files if needed
    ]
    #pattern = fielddata.data_dir + "*" + flight + filetype + '.' + fileext
    def mock_input(prompt):
        return user_inputs.pop(0) if user_inputs else ""
    def mock_glob_side_effect(pattern):
        return [file for file in fake_file_list if fnmatch.fnmatch(file, pattern)]
    # Mocking glob.glob (you can also use monkeypatch if preferred)
    with patch('glob.glob', side_effect=mock_glob_side_effect), patch('builtins.input', side_effect=mock_input):

        actual_flag, actual_datafile = fielddata.find_file(
            fielddata.data_dir, flight, project, filetype, fileext, flag, reprocess
        )

        assert actual_flag == expected_flag
        assert actual_datafile == expected_datafile
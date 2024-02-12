
import sys
import os

expected_flag = True
expected_datafile = '/Users/srunkel/dev/projects/CAESAR/CAESARtf01h.nc'
fileext = 'nc'
filetype = 'h'
flag = True
reprocess = False

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
    "test_id, FLIGHT, PROJECT, expected_datafile, expected_flag", [
        # Test Case 1:
        ('test1', 'rf01', 'ACCLIPrf01', '/sample/path.nc', True),
        # ... more test cases with different file paths, flags, etc.
    ]
)
def test_find_file(fielddata, test_id, FLIGHT, PROJECT, expected_datafile, expected_flag):
    # Mocking glob.glob (you can also use monkeypatch if preferred)
    with patch('glob.glob') as mock_glob:
        mock_glob.return_value = [expected_datafile]

        actual_flag, actual_datafile = fielddata.find_file(
            fielddata.data_dir, FLIGHT, PROJECT, filetype, fileext, flag, reprocess
        )

        assert actual_flag == expected_flag
        assert actual_datafile == expected_datafile
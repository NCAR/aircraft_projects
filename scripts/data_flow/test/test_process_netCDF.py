import os
import unittest.mock as mock
from unittest.mock import patch
import sys
import pytest
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import FieldData
from const_tests import *

@pytest.fixture
def fielddata():
    with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input)):
        return FieldData()


@pytest.mark.parametrize(
    "test_id, rawfile, ncfile, rate, config_ext, proj_dir, flight, project, flags, expected_result", [
        # Test Case 1:
        ('test1', '/sample/path.raw', '/sample/path.nc', 'h','LRT','/Users/srunkel/dev/projects/CAESAR','tf01','CAESAR','-b', True),
        # ... more test cases with different parameters
    ]
)
def test_process_netCDF(fielddata, test_id, rawfile, ncfile, rate, config_ext, proj_dir, flight, project, flags, expected_result):
    # Mocking, mainly focusing on file & system interactions
    with (mock.patch('os.path.exists', return_value=False), mock.patch('os.system', return_value=0),
          mock.patch('builtins.open', new_callable=mock.mock_open)):  # Mock the logger

        result = fielddata.process_netCDF(rawfile, ncfile, rate, config_ext, proj_dir, flight, project, flags)

        # Assertions: Check file operations, command execution, logging calls, and result
        assert result == expected_result

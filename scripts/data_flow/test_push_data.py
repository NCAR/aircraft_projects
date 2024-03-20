#! /bin/bash/python

import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from const_tests import *

import pytest
from unittest.mock import Mock, patch
from push_data import FieldData


# Test IDs for parametrization
test_ids = [
    "happy_path",
    "mismatch"
    #"edge_case_no_files",
    #"error_case_missing_env_var"
]

# Parametrized test cases
test_cases = [
    # Happy path test with realistic values
    ({"PROJECT": PROJECT, "FLIGHT": FLIGHT, "AIRCRAFT": AIRCRAFT, "DATA_DIR": DATA_DIR, "RAW_DIR": RAW_DIR, "PROJ_DIR": PROJ_DIR, "EMAIL": EMAIL}, True),
    ({"PROJECT": PROJECT, "FLIGHT": 'tf05', "AIRCRAFT": AIRCRAFT, "DATA_DIR": DATA_DIR, "RAW_DIR": RAW_DIR, "PROJ_DIR": PROJ_DIR, "EMAIL": EMAIL}, False),
    # Edge case with no files found
    #({"PROJECT": PROJECT, "FLIGHT": FLIGHT, "AIRCRAFT": AIRCRAFT, "DATA_DIR": "/nonexistent_dir/", "RAW_DIR": "/nonexistent_dir/", "PROJ_DIR": PROJ_DIR, "EMAIL": EMAIL}, False),
    # Error case with missing environment variable
    #({}, False)
]

@pytest.mark.parametrize("env_setup, expected_success", test_cases, ids=test_ids)
def test_FieldData_init(env_setup, expected_success):
    # Arrange
    with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input), patch('os.listdir', return_value=listdir_return_value)):

        # Act

        if expected_success:
            field_data = FieldData()
        else:
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                field_data = FieldData()

        # Assert
        if expected_success:
            assert field_data.project == PROJECT
            assert field_data.aircraft == AIRCRAFT
            assert field_data.flight == FLIGHT
            assert field_data.data_dir == f'{DATA_DIR}/{PROJECT.upper()}/'
            assert field_data.raw_dir == f'{RAW_DIR}/{PROJECT.upper()}/'
            assert field_data.proj_dir == f'{PROJ_DIR}/{PROJECT}/{AIRCRAFT}/'
            assert field_data.nc2ascBatch == f'{PROJ_DIR}/{PROJECT}/{AIRCRAFT}/scripts/nc2asc.bat'
            assert field_data.qc_ftp_dir == f'/pub/incoming/catalog/{PROJECT.lower()}'
            assert field_data.qc_ftp_site == 'catalog.eol.ucar.edu'
            assert field_data.zip_dir =='/tmp/'
        else:
            assert pytest_wrapped_e.value.code == 1
            

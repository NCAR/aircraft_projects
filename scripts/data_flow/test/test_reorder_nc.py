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
    "test_id, ncfile, expected_result", [
        # Test Case 1:
        ('test1', '/sample/path.nc', 'Yes'),
        # ... more test cases with different parameters
    ]
)
def test_reorder_nc(fielddata, test_id, ncfile, expected_result):
    # Mocking, mainly focusing on file & system interactions
    with (mock.patch('os.path.exists', return_value=False), mock.patch('os.system', return_value=0),
          mock.patch('builtins.open', new_callable=mock.mock_open), patch('logging.Logger.info') as mock_logger):  # Mock the logger

        result = fielddata.reorder_nc(ncfile)

        # Assertions: Check file operations, command execution, logging calls, and result
        assert result == expected_result
        expected_messages = [
            f"about to execute : nccopy -u {ncfile} tmp.nc",
            f"about to execute : /bin/mv tmp.nc {ncfile}"
        ]
        for msg in expected_messages:
            mock_logger.assert_any_call(msg)
import os
import unittest.mock as mock
from unittest.mock import patch
import sys
import pytest
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import FieldData
from const_tests import *
import os
import tempfile

# Create a temporary directory


@pytest.fixture
def fielddata():
    with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input)):
        return FieldData()


@pytest.mark.parametrize(
    "test_id, aircraft, project,flight, oapfile_dir", [
        # Test Case 1:
        ('test1', 'C130_N130AR', 'CAESAR','tf01','oapfile_dir'),
        # ... more test cases with different parameters
    ]
)
def test_process_threeVCPI(fielddata, test_id, aircraft, flight, project, oapfile_dir):
    # Mocking, mainly focusing on file & system interactions
    with (mock.patch('os.path.exists', return_value=False), mock.patch('os.system', return_value=0),
          mock.patch('builtins.open', new_callable=mock.mock_open)):  # Mock the logger
        with tempfile.TemporaryDirectory() as twods_raw_dir:
            # Create a file in the temporary directory
            catted_file = os.path.join(twods_raw_dir, "catted_file")
            with open(catted_file, "w") as f:
                f.write("This is a test file")
            fielddata.process_threeVCPI(aircraft, project, flight, twods_raw_dir, oapfile_dir)
            assert not os.path.exists(catted_file)
        # Assertions: Check file operations, command execution, logging calls, and result

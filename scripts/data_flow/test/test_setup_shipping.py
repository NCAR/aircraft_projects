import os
import unittest.mock as mock
from unittest.mock import patch
import pytest

import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')

from const_tests import *

import unittest.mock as mock
import tempfile
from push_data import FieldData
@pytest.fixture
def fielddata():
    with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input)):
        return FieldData()


@pytest.mark.parametrize(
    "test_id, filename, mock_system_return, expected_message", [
        ('test_success', 'test_data', 0, None),  # Success case
        ('test_failure', 'test_data', 1, "\nERROR!: Zipping up test_data with command:\n  zip test_data.zip test_data"),  # Failure case 
    ]
)

def test_setup_shipping(fielddata, mock_ensure_dir, mock_rsync_file, mock_os_system):
    # Mocks setup
    mock_os_system.return_value = 0  # Simulate successful NAS mount
    mock_rsync_file.return_value = 'Yes-NAS'  # Assume successful rsync

    # Test data preparation
    file_ext = {'ADS': True, 'PMS2D': True, 'HRT': True}  # Example
    filename = {'ADS': '/path/to/ads.ads',  # Sample filenames
                'PMS2D': '/path/to/pms2d.nc',
                'HRT': '/path/to/hrt.nc'}
    process = True 
    reprocess = False
    status = {}

    # Call the function
    nas_data_dir, nas_sync_dir = setup_shipping(file_ext, filename, process, reprocess, status)

    # Assertions
    mock_os_system.assert_called_once_with(  # Check NAS mount command (adjust the command string as needed)
        "sudo /bin/mount -t nfs <nas_url> <nas_mnt_pt>" 
    )
    mock_ensure_dir.assert_called()  # At least once for creating directories
    mock_rsync_file.assert_has_calls([
        mock.call('/path/to/ads.ads', nas_data_dir + '/ADS'), 
        # ... add similar assertions for other file_ext entries
    ])
    self.assertEqual(status['ADS']['stor'], 'Yes-NAS')  # Example status check 

    # Add another test with 'NAS_permanent_mount' set to True to exercise that code path.

    # Add a test case with 'catalog' set to True in the input data 


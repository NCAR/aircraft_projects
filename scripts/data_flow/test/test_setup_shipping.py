import os
import unittest.mock as mock
from unittest.mock import patch
import pytest
from unittest.mock import patch, MagicMock

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



# Constants and fixtures for the tests

@pytest.fixture
def mock_os_system():
    with patch('os.system') as mock:
        yield mock

@pytest.fixture
def mock_ensure_dir():
    with patch('push_data.FieldData.ensure_dir') as mock:
        yield mock

@pytest.fixture
def mock_rsync_file():
    with patch('push_data.FieldData.rsync_file') as mock:
        yield mock

# Happy path tests with various realistic test values
@pytest.mark.parametrize("file_ext, filename, process, reprocess, status, expected_nas_data_dir, expected_nas_sync_dir, test_id", [
    ({"ADS": "ads_file.ext"}, {"ADS": "/path/to/ads_file.ext"}, True, False, {"ADS": {}}, "/mnt/Data/EOL_data/RAF_data/", "/mnt/Data/FTP_sync/EOL_data/RAF_data/", "happy_path_ads"),
    ({"PMS2D": "pms2d_file.ext"}, {"PMS2D": "/path/to/pms2d_file.ext"}, True, False, {"PMS2D": {}}, "/mnt/Data/EOL_data/RAF_data/", "/mnt/Data/FTP_sync/EOL_data/RAF_data/", "happy_path_pms2d"),
    # Add more test cases as needed
])
def test_setup_shipping_happy_path(fielddata, mock_os_system, mock_ensure_dir, mock_rsync_file, file_ext, filename, process, reprocess, status, expected_nas_data_dir, expected_nas_sync_dir, test_id):
    # Arrange

    # Act
    nas_data_dir, nas_sync_dir = fielddata.setup_shipping(file_ext, filename, process, reprocess, status)

    # Assert
    mock_os_system.assert_called()
    mock_ensure_dir.assert_called()
    mock_rsync_file.assert_called()
    assert nas_data_dir == expected_nas_data_dir
    assert nas_sync_dir == expected_nas_sync_dir
    for key in file_ext:
        assert status[key]["stor"] == mock_rsync_file.return_value

# Edge cases
# Add tests for edge cases such as empty file_ext, filename, etc.

# Error cases
# Add tests for error cases such as os.system failing, rsync_file failing, etc.

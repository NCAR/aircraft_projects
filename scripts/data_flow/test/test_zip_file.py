import os
import unittest.mock as mock
import pytest
from unittest.mock import patch
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
def test_zip_file(fielddata, test_id, filename, mock_system_return, expected_message):
    with tempfile.TemporaryDirectory() as datadir:
        # Create a test file within the temporary directory
        test_file = os.path.join(datadir, filename)
        with open(test_file, 'w') as f:
            f.write("Sample data for zip test")

        with mock.patch('os.system') as mock_system, \
             mock.patch('push_data.FieldData.print_message') as mock_print:

            mock_system.return_value = mock_system_return

            fielddata.zip_file(filename, datadir) 

            if expected_message:
                mock_print.assert_called_once_with(expected_message) 
            else:
                mock_print.assert_not_called()

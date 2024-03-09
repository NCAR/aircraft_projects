import unittest
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
    "test_id, file, out_dir, expected_result, mock_system_return", [
        ('test1', 'test_file.txt', '/tmp/output', 'Yes-NAS', 0),  # Success case
        ('test2', 'nonexistent_file.txt', '/tmp/output', None, 1)   # Failure case
    ]
)
def test_rsync_file(fielddata,test_id, file, out_dir, expected_result, mock_system_return):
    with (mock.patch('os.path.exists', return_value=False), mock.patch('os.system', return_value=0),
            mock.patch('builtins.open', new_callable=mock.mock_open)):  # Mock the logger
        with mock.patch('os.system') as mock_system:
            mock_system.return_value = mock_system_return 

            with tempfile.TemporaryDirectory() as temp_dir:
                # Optionally create the 'file' within the temp_dir if needed

                result = fielddata.rsync_file(file, out_dir)
                assert result == expected_result

                # Additional assertions on file system state if relevant
                # e.g., assert not os.path.exists(os.path.join(out_dir, file)) in failure case

if __name__ == '__main__':
    unittest.main()

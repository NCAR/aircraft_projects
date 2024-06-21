import pytest
import sys
import os
sys.path.insert(0, os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts')
from fieldProc_setup import *
from unittest.mock import patch
from collections import OrderedDict
from const_tests import *
sys.path.insert(0, os.environ['PROJ_DIR'] + '/scripts/data_flow')
from push_data import FieldData


@pytest.fixture
def fielddata():
    with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input)):
        return FieldData()

def test_fielddata_constants(fielddata):
    # Replace 'expected_project_name' and 'expected_aircraft_name' with the actual expected values
    assert fielddata.project == "CAESAR"
    assert fielddata.aircraft == "C130_N130AR"
    assert fielddata.raw_dir == "/Users/srunkel/dev/projects/CAESAR/"
    assert fielddata.data_dir == "/Users/srunkel/dev/projects/CAESAR/"
    assert isinstance(fielddata.filename, dict)
    assert fielddata.flight == "tf01"
    assert fielddata.email == "test@example.com"
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

ord_dict = OrderedDict([("ADS", "ads"), ("LRT", "nc"), ("KML", "kml")])
caesar_dict=OrderedDict([("ADS", "ads"), ("LRT", "nc"), ("KML", "kml"),('PMS2D','2d')])
@pytest.mark.parametrize(
    "test_id, HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI, expected_output", [
        # Test Case 1:
        ('test1', False, False, False, False, False, False, ord_dict),
        ('test2', HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI, caesar_dict),
        #('test2', 'tf01', 'CAESAR', 'h','ict',False,False,'/Users/srunkel/dev/projects/CAESAR/CAESARtf01h.ict',False, None),
        # ... more test cases with different file paths, flags, etc.
    ]
)
def test_createFileExt(fielddata, test_id, HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI, expected_output):
    result = fielddata.createFileExt(HRT, SRT, ICARTT, IWG1, PMS2D, threeVCPI)
    assert result == expected_output
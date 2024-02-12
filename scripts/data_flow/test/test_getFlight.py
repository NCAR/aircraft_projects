#! /usr/bin/python3

import unittest

import pytest
from push_data import FieldData
from unittest.mock import patch
from const_tests import *
import argparse
import sys
#import imp
import push_data

class TEST_readFlight(unittest.TestCase):
    def setUp(self):
        with (patch('os.environ.get', side_effect=mock_getenv), patch('builtins.input', side_effect=mock_input), patch(
                'os.listdir', return_value=listdir_return_value)):
            self.fielddata = push_data.FieldData()

    def tearDown(self):
        pass

    def test_getFlight(self):
        #@patch('os.environ.get', side_effect=mock_getenv)

        self.assertEqual(self.fielddata.flight,'tf01')

if __name__ == '__main__':
    unittest.main()

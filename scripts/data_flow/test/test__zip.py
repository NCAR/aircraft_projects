from unittest.mock import MagicMock
import pytest
from _zip import SetupZip
import os
from pyfakefs.fake_filesystem_unittest import Patcher

@pytest.fixture
def setup_zip():
    file_ext = {
        "ADS": ".ads",
        "PMS2D": ".2d",
        "OTHER": ".txt"
    }
    data_dir = "/path/to/data"
    filename = {
        "ADS": "/path/to/data/ads_file.ads",
        "PMS2D": "/path/to/data/2d_file.2d",
        "OTHER": "/path/to/data/other_file.txt"
    }
    inst_dir = {
        "ADS": "/path/to/inst/ads",
        "PMS2D": "/path/to/inst/2d",
        "OTHER": "/path/to/inst/other"
    }
    with Patcher() as patcher:
    # access the fake_filesystem object via patcher.fs
            patcher.fs.create_dir('/path/to/inst/other')
            patcher.fs.create_dir('path/to/inst/2d')
            patcher.fs.create_dir('/path/to/inst/ads')
            patcher.fs.create_file('/path/to/data/2d_file.2d')
            patcher.fs.create_file('/path/to/data/ads_file.ads')
            patcher.fs.create_file('/path/to/data/other_file.txt')
        #fs.create_file('data_directory/PROJECT_NAME/email.addr.txt')
            return SetupZip(file_ext, data_dir, filename, inst_dir)

def test_zip_file_called(setup_zip, mocker):
    mocker.patch("os.chdir")
    mocker.patch("os.system")
    setup_zip.zip_file("ads_file.ads", "/path/to/inst/ads")
    os.chdir.assert_called_once_with("/path/to/inst/ads")
    os.system.assert_called_once_with("zip ads_file.ads.zip ads_file.ads")

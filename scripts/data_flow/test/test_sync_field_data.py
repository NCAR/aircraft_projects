import pytest
from unittest.mock import patch, call
import sys
import os
from check_env import check
check() ##Check that the environment variables are set correctly   
from sync_field_data import ingest_to_local, QA_notebook

# Mock os.environ.get to use our env_vars

project = os.environ['PROJECT']
aircraft = os.environ['AIRCRAFT']
PROJ_DIR = os.environ['PROJ_DIR']
DATA_DIR = os.environ['DATA_DIR']
RAW_DATA_DIR = os.environ['RAW_DATA_DIR']
call1 = call('Starting distribution of data from FTP to localdirs/')

@pytest.mark.parametrize("filetype,local_dir,start_dir,expected_command", [
    ('PMS2D', '/path/to/local_dir', '/path/to/start_dir', f'rsync -qu /path/to/start_dir/EOL_data/RAF_data/PMS2D/* {RAW_DATA_DIR}/{project}/PMS2D/.'),
    ('LRT', '/another/local_dir', '/another/start_dir',  f'rsync -qu /another/start_dir/EOL_data/RAF_data/LRT/* /another/local_dir')
    # Add more test cases as needed
])
@patch('logging.info')
@patch('os.system')
def test_ingest_to_local(mock_os_system, mock_logging_info,filetype, local_dir, start_dir, expected_command):
    
    # Arrange

    call2 = call(f'Syncing dir into place: {expected_command}')

    # Act
    ingest_to_local(filetype, local_dir, start_dir)

    # Assert
    
    mock_os_system.assert_called_once_with(expected_command)
    mock_logging_info.assert_has_calls([call1,call2])
    

from sync_field_data import sync_from_gdrive,proc_dict ##imports process dictionary to see what data is being processed

call_dict  ={'LRT':call('LRT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'KML':call('KML', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'HRT':call('HRT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'SRT':call('SRT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'IWG1':call('IWG1', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'PMS2D':call('PMS2D', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'ADS':call('ADS', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync')}

@patch('logging.info')
@patch('sync_field_data.ingest_to_local')
@patch('sync_field_data.distribute_data')
def test_sync_from_gdrive(mock_distribute_data, mock_ingest_to_local, mock_logging_info):
    # Arrange

    # Act
    sync_from_gdrive()

    # Assert
    mock_ingest_to_local.assert_has_calls([call_dict[dtype] for dtype in proc_dict if proc_dict[dtype]])
    if QA_notebook:
        mock_distribute_data.assert_has_calls([call(['field_data', 'QAtools'])])
    mock_logging_info.assert_called_once_with("Syncing from GDRIVE...")
    

from sync_field_data import distribute_data

@patch('logging.info')
@patch('sync_field_data._sync_data')
def test_distribute_data(mock_sync_data, mock_logging_info):
    # Arrange
    data_type = ['QAtools', 'field_data']
    dat_dir = DATA_DIR + '/' + project

    expected_calls = [
        call(f'{DATA_DIR}/{project}/QAtools',  '*', ['/net/www/raf/'], 'Syncing QAtools data into place', True),
        call(f'{DATA_DIR}/{project}/field_data','*.nc', [f'{DATA_DIR}/{project}'], 'Syncing field_data data into place', False)
    ]
    log1 = call('Starting distribution of QAtools.html')
    log2 = call('Continuing distribution of RAF prod data')
    # Act
    distribute_data(data_type)
    
    # Assert
    mock_sync_data.assert_has_calls(expected_calls)
    mock_logging_info.assert_has_calls([log1,log2])
    
from sync_field_data import _sync_data

@patch('logging.info')
@patch('sync_field_data._run_and_log')
def test_sync_data_recursive(mock_run_and_log, mock_logging_info):
    # Arrange
    src_dir = '/path/to/src_dir'
    file_pattern = '*.txt'
    dest_dirs = ['/path/to/dest_dir1', '/path/to/dest_dir2']
    base_message = 'Syncing files'
    recursive = True

    # Act
    _sync_data(src_dir, file_pattern, dest_dirs, base_message, recursive)

    # Assert
    command_base = f'rsync -rqu {src_dir}/{file_pattern} '
    expected_calls = [
        call(command_base + dest_dirs[0], f'{base_message}'),
        call(command_base + dest_dirs[1], f'{base_message}')
    ]
    mock_run_and_log.assert_has_calls(expected_calls)
    mock_logging_info.assert_not_called()

@patch('logging.info')
@patch('sync_field_data._run_and_log')
def test_sync_data_non_recursive(mock_run_and_log, mock_logging_info):
    # Arrange
    src_dir = '/path/to/src_dir'
    file_pattern = '*.txt'
    dest_dirs = ['/path/to/dest_dir1', '/path/to/dest_dir2']
    base_message = 'Syncing files'
    recursive = False

    # Act
    _sync_data(src_dir, file_pattern, dest_dirs, base_message, recursive)

    # Assert
    command_base = f'rsync -qu {src_dir}/{file_pattern} '
    expected_calls = [
        call(command_base + dest_dirs[0], f'{base_message}'),
        call(command_base + dest_dirs[1], f'{base_message}')
    ]
    mock_run_and_log.assert_has_calls(expected_calls)
    mock_logging_info.assert_not_called()
    
import logging
from unittest.mock import patch, call
from sync_field_data import _run_and_log

@patch('os.system')
@patch('logging.info')
def test_run_and_log(mock_logging_info, mock_os_system):
    # Arrange
    command = 'ls -l'
    message = 'Running command'
    output ='Running command: ls -l'
    # Act
    _run_and_log(command, message)
    
    # Assert
    mock_os_system.assert_called_once_with(command)
    mock_logging_info.assert_called_once_with(output)

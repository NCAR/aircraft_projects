import pytest
from unittest.mock import patch, call
import sys
import os
from check_env import check
check() ##Check that the environment variables are set correctly   
from sync_field_data import ingest_to_local, QA_notebook,ftp_dir,rdat_dir

# Mock os.environ.get to use our env_vars

project = os.environ['PROJECT']
aircraft = os.environ['AIRCRAFT']
PROJ_DIR = os.environ['PROJ_DIR']
DATA_DIR = os.environ['DATA_DIR']
RAW_DATA_DIR = os.environ['RAW_DATA_DIR']
call1 = call('Starting distribution of data from FTP to localdirs/')

@pytest.mark.parametrize("filetype,local_dir,start_dir,expected_command", [
    ('PMS2D', f'{RAW_DATA_DIR}{project}', '/path/to/start_dir', f'rsync -qu --exclude="*.shtml" /path/to/start_dir/PMS2D/* {RAW_DATA_DIR}{project}/PMS2D/.'),
    ('LRT', '/another/local_dir', '/another/start_dir',  f'rsync -qu --exclude="*.shtml" /another/start_dir/LRT/* /another/local_dir')
    # Add more test cases as needed
])
# Decorator order is bottom up so start with os.system in call
@patch('logging.info')
@patch('sync_field_data.create_directory')
@patch('os.path.exists', return_value=True)
@patch('os.system')
def test_ingest_to_local(mock_os_system, mock_path_exists, mock_create_directory, mock_logging_info, filetype, local_dir, start_dir, expected_command):
    
    # Arrange

    call2 = call(f'Syncing dir into place: {expected_command}')

    # Act
    ingest_to_local(filetype, local_dir, start_dir)

    # Assert
    
    mock_os_system.assert_called_once_with(expected_command)
    mock_logging_info.assert_has_calls([call1,call2])
    

from sync_field_data import sync_from_gdrive,sync_from_ftp,proc_dict ##imports process dictionary to see what data is being processed

call_dict_gdrive  ={'LRT':call('LRT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'KML':call('KML', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'HRT':call('HRT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'SRT':call('SRT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'IWG1':call('IWG1', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'PMS2D':call('PMS2D', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'ADS':call('ADS', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'ICARTT': call('ICARTT', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync'),
        'QA_Tools': call('QA_Tools', f'{DATA_DIR}/{project}/field_data', RAW_DATA_DIR + '/' + project + '/field_sync')
        }

@patch('logging.info')
@patch('sync_field_data.ingest_to_local')
@patch('sync_field_data.distribute_data')
def test_sync_from_gdrive(mock_distribute_data, mock_ingest_to_local, mock_logging_info):
    # Arrange

    # Act
    sync_from_gdrive()

    # Assert
    mock_ingest_to_local.assert_has_calls([call_dict_gdrive[dtype] for dtype in proc_dict if proc_dict[dtype]])
    if QA_notebook:
        mock_distribute_data.assert_has_calls([call(['QAtools'])])
    mock_logging_info.assert_called_once_with("Syncing from GDRIVE...")



call_dict  ={'LRT':call('LRT', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'KML':call('KML', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'HRT':call('HRT', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'SRT':call('SRT', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'IWG1':call('IWG1', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'PMS2D':call('PMS2D', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'ADS':call('ADS', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'ICARTT': call('ICARTT', f'{DATA_DIR}/{project}/field_data', ftp_dir),
    'QA_Tools': call('QA_Tools', f'{DATA_DIR}/{project}/field_data', ftp_dir)
}


@patch('sync_field_data.dir_check')
@patch('sync_field_data.ingest_to_local')
@patch('logging.info')
@patch('sync_field_data.distribute_data')
def test_sync_from_ftp(mock_distribute_data,mock_logging_info, mock_ingest_to_local, mock_dir_check):
    # Arrange



    # Act
    sync_from_ftp()
    #mock_logging_info.assert_called_once_with(call("Syncing from syncthing transfer directory...")),
    mock_dir_check.assert_called_once()
    # Assert
    mock_logging_info.assert_has_calls([
            call(f'Syncing from syncthing transfer directory...'),
            call(f'Syncing ADS and PMS2D data from {ftp_dir} to {rdat_dir}'),
            call(f'Syncing other data from {ftp_dir} to {DATA_DIR}/{project}/field_data')
        ])
    mock_ingest_to_local.assert_has_calls([call_dict[dtype] for dtype in proc_dict if proc_dict[dtype]])
    

from sync_field_data import distribute_data

@patch('logging.info')
@patch('sync_field_data._sync_data')
def test_distribute_data(mock_sync_data, mock_logging_info):
    # Arrange
    data_type = ['QAtools', 'field_data']
    dat_dir = DATA_DIR + '/' + project

    expected_calls = [
        call(f'{DATA_DIR}/{project}/QAtools',  '*', ['/net/www/raf/'], 'Syncing QAtools data into place', True),
        call(f'{DATA_DIR}/{project}/field_sync','*.nc', [f'{DATA_DIR}/{project}'], 'Syncing field_data data into place', False)
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
    command_base = f'rsync -rqu --exclude="*.shtml" {src_dir}/{file_pattern} '
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
    command_base = f'rsync -qu --exclude="*.shtml" {src_dir}/{file_pattern} '
    expected_calls = [
        call(command_base + dest_dirs[0], f'{base_message}'),
        call(command_base + dest_dirs[1], f'{base_message}')
    ]
    mock_run_and_log.assert_has_calls(expected_calls)
    mock_logging_info.assert_not_called()
    
import logging
import unittest
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

###############################################################################
# Tests for the autofs-race guard added to create_directory:
#   _automount_root, _ensure_visible, and the create_directory branches that
#   depend on them. See sync_field_data.py for the rationale.
###############################################################################

from sync_field_data import _automount_root, _ensure_visible, create_directory


@pytest.mark.parametrize("path,expected", [
    ('/net/ftp/pub/data/incoming/inspyre/EOL_Data/RAF_Data', '/net/ftp'),
    ('/net/jlocal/projects/scripts', '/net/jlocal'),
    ('/net/ftp', '/net/ftp'),            # the mount root itself
    ('/net/ftp/', '/net/ftp'),           # trailing slash
    ('/home/ads/data', None),            # not under /net
    ('/net', None),                      # no host component
    ('/net/', None),                     # empty host component
])
def test_automount_root(path, expected):
    assert _automount_root(path) == expected


@patch('sync_field_data.time.sleep')
@patch('os.listdir')
@patch('os.path.isdir')
def test_ensure_visible_already_present(mock_isdir, mock_listdir, mock_sleep):
    # Visible on the first check: no automount nudge, no sleeping.
    mock_isdir.return_value = True

    assert _ensure_visible('/net/ftp/pub/EOL_Data/RAF_Data') is True
    mock_isdir.assert_called_once_with('/net/ftp/pub/EOL_Data/RAF_Data')
    mock_listdir.assert_not_called()
    mock_sleep.assert_not_called()


@patch('sync_field_data.time.sleep')
@patch('os.listdir')
@patch('os.path.isdir')
def test_ensure_visible_transient_automount_race(mock_isdir, mock_listdir, mock_sleep):
    # Not visible on the first check (mount timed out), visible after a nudge.
    mock_isdir.side_effect = [False, True]

    assert _ensure_visible('/net/ftp/pub/EOL_Data/RAF_Data') is True
    # We nudged the correct automount root exactly once, then succeeded.
    mock_listdir.assert_called_once_with('/net/ftp')
    mock_sleep.assert_called_once()


@patch('sync_field_data.time.sleep')
@patch('os.listdir')
@patch('os.path.isdir')
def test_ensure_visible_genuinely_missing_under_net(mock_isdir, mock_listdir, mock_sleep):
    # Never becomes visible: exhaust retries, nudging each time, then report False.
    mock_isdir.return_value = False

    assert _ensure_visible('/net/ftp/pub/EOL_Data/RAF_Data', retries=3) is False
    assert mock_listdir.call_count == 3      # one nudge per retry
    assert mock_sleep.call_count == 3


@patch('sync_field_data.time.sleep')
@patch('os.listdir')
@patch('os.path.isdir')
def test_ensure_visible_non_net_path_does_not_retry(mock_isdir, mock_listdir, mock_sleep):
    # A missing non-/net path can't be an automount race: bail immediately,
    # no nudging and no sleeping.
    mock_isdir.return_value = False

    assert _ensure_visible('/home/ads/missing', retries=5) is False
    mock_listdir.assert_not_called()
    mock_sleep.assert_not_called()


@patch('sync_field_data.send_mail_and_die')
@patch('os.makedirs')
@patch('sync_field_data._ensure_visible', return_value=True)
def test_create_directory_visible_is_a_noop(mock_ensure, mock_makedirs, mock_die):
    # Directory is (or becomes) visible: never create, never bail.
    create_directory('/net/ftp/pub/EOL_Data/RAF_Data')

    mock_ensure.assert_called_once_with('/net/ftp/pub/EOL_Data/RAF_Data')
    mock_makedirs.assert_not_called()
    mock_die.assert_not_called()


@patch('sync_field_data.send_mail_and_die')
@patch('os.makedirs')
@patch('os.access', return_value=False)
@patch('os.path.isdir', return_value=True)
@patch('sync_field_data._ensure_visible', return_value=False)
def test_create_directory_bails_when_parent_unwritable(
        mock_ensure, mock_parent_isdir, mock_access, mock_makedirs, mock_die):
    # Not visible, parent exists but is not writable => mount/permission issue.
    # Must NOT makedirs (would shadow the real NFS export); must bail instead.
    create_directory('/net/ftp/pub/EOL_Data/RAF_Data')

    mock_makedirs.assert_not_called()
    mock_die.assert_called_once()


@patch('sync_field_data.send_mail_and_die')
@patch('os.makedirs')
@patch('os.access', return_value=True)
@patch('os.path.isdir', return_value=True)
@patch('sync_field_data._ensure_visible', return_value=False)
def test_create_directory_creates_when_genuinely_missing(
        mock_ensure, mock_parent_isdir, mock_access, mock_makedirs, mock_die):
    # Not visible, parent exists and IS writable => genuinely missing, so create.
    create_directory('/tmp/data/INSPYRE/PMS2D')

    mock_makedirs.assert_called_once_with('/tmp/data/INSPYRE/PMS2D', exist_ok=True)
    mock_die.assert_not_called()


@patch('sync_field_data.send_mail_and_die')
@patch('os.makedirs', side_effect=OSError('boom'))
@patch('os.access', return_value=True)
@patch('os.path.isdir', return_value=True)
@patch('sync_field_data._ensure_visible', return_value=False)
def test_create_directory_bails_when_makedirs_fails(
        mock_ensure, mock_parent_isdir, mock_access, mock_makedirs, mock_die):
    # makedirs itself errors => bail with an email.
    create_directory('/tmp/data/INSPYRE/PMS2D')

    mock_makedirs.assert_called_once()
    mock_die.assert_called_once()


@patch('sync_field_data.send_mail_and_die')
@patch('os.makedirs')
@patch('sync_field_data._ensure_visible')
@patch('os.path.isdir')
def test_create_directory_tuple_uses_existing_case(
        mock_isdir, mock_ensure, mock_makedirs, mock_die):
    # Tuple form (upper/lower case candidates): the existing one is selected and
    # assigned to the global dat_dir; no creation or bail. Here the second
    # (lower case) candidate exists.
    import sync_field_data
    mock_isdir.side_effect = lambda p: p == '/tmp/data/inspyre'

    create_directory(('/tmp/data/INSPYRE', '/tmp/data/inspyre'))

    assert sync_field_data.dat_dir == '/tmp/data/inspyre'
    mock_ensure.assert_not_called()
    mock_makedirs.assert_not_called()
    mock_die.assert_not_called()


if __name__ == '__main__':
    unittest.main()

# How to run tests for push_data.py and sync_field_data.py

## Setting up the test environment

To run the tests for push_data and sync_field_data, you must have a test environment running python 3.12 or greater. Below is an example test environment setup:
 `conda create -n test_env python=3.12`
 `conda activate test_env`
 `conda install pytest, pytest-mock`
 `pip install pyfakefs`
The environment variables for `$PROJECT`, `$PROJ_DIR`, and `$AIRCRAFT` must be configured to an existing project with a folder within the aircraft_projects repository for tests to run.

### Running the tests

Run all tests in the aircraft_projects/scripts/data_flow/test/ directory by running `./run_tests.sh` with the active test environment.

### Test Modules

 1. `test__setup.py` tests the instantiation of the setup class and make sure all of the constants passed to process are properly formatted.
 2. `test_push_data.py` sets up a testing environment using fixtures and mocks to ensure that the push_data module functions correctly under various conditions. It is structured to test the main functionality of the data pushing process, including reading flight and email information, handling environment variables, interacting with the filesystem, and sending emails.
 3. `test__zip.py` tests the SetupZip class and the zipping functiomality of the push_data script on a fake filesystem.
 4. `test_sync_field_data.py` ets up a testing environment using fixtures and mocks to ensure the functionality of the sync_field_data.py script. It makes sure that based on different configurations the correct functions and commands are called to ensure the data is syncing to the correct directories.

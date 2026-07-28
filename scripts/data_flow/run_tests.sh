#!/usr/bin/env bash
###############################################################################
# Shell script to call Python units tests. Configure environment (if not
# running on a server/groundstation/etc) and call tests.
#
# Written in Python 3.9
#
# COPYRIGHT:   University Corporation for Atmospheric Research, 2024
###############################################################################
# --- Environment Configuration ---
# The following environment variables must be set before running this script,
# pointing at an existing project with a fieldProc_setup.py file. The tests read
# all five at import time, so a missing one fails before any test runs.
#   PROJECT, AIRCRAFT, PROJ_DIR   -- also validated by check_env.check()
#   DATA_DIR, RAW_DATA_DIR        -- used to build expected paths in the tests
#
# The conda environment must be python 3.9 or later with the required packages.
# The easiest way to get them is the pinned environment file:
#   conda env create -f test/testenv.yml
#   conda activate test_env
# Or set one up manually:
#   conda create -n test_env python=3.9
#   conda activate test_env
#   conda install pytest pytest-mock
#   pip install pyfakefs

# --- Preflight: verify required environment variables are set ---
missing=""
for var in PROJECT AIRCRAFT PROJ_DIR DATA_DIR RAW_DATA_DIR; do
    if [ -z "${!var}" ]; then
        missing="$missing $var"
    fi
done
if [ -n "$missing" ]; then
    echo "*** Cannot run tests: missing environment variable(s):$missing ***"
    echo "Set them to an existing project, e.g.:"
    echo "  export PROJECT=INSPYRE AIRCRAFT=GV_N677F"
    echo "  export PROJ_DIR=/home/local/projects DATA_DIR=/home/data RAW_DATA_DIR=/var/r1"
    exit 1
fi

# --- Test Execution ---
# The following command will run all tests in the test/ directory
# To run a specific test, replace test/ with the path to the test file
python -m pytest -s test/

# --- Exit Status Logic ---

# Capture exit codes to determine overall test result

pytest_result=$?

# Basic check for pass/fail based on non-zero exit codes
if [ $pytest_result -ne 0 ]; then
    echo "*** Some tests failed ***"
    exit 1  # Indicate failure
else
    echo "*** All tests passed ***"
    exit 0  # Indicate success
fi
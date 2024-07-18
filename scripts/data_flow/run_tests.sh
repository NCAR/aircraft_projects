###############################################################################
# Shell script to call Python units tests. Configure environment (if not
# running on a server/groundstation/etc) and call tests.
#
# Written in Python 3.12
#
# COPYRIGHT:   University Corporation for Atmospheric Research, 2024
###############################################################################
# --- Environment Configuration ---
# Set up environment variables, etc. as needed -- The PROJECT, PROJ_DIR, and AIRCRAFT 
# environment variables must be set before running this script to a project with a fieldProcSetup.py file
# The conda environment must be python 3.12 or later and the following packages are required:
# conda create -n test_env python=3.12
# conda activate test_env
# conda install pytest
# pip install pyfakefs

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
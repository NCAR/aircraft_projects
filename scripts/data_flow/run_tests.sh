###############################################################################
# Shell script to call Python units tests. Configure environment (if not
# running on a server/groundstation/etc) and call tests.
#
# Written in Python 3
#
# COPYRIGHT:   University Corporation for Atmospheric Research, 2020
###############################################################################
# If running someplace the standard RPMs aren't installed, such as on a desktop
# MAC, be sure that the standard environment vars are configured through your
# .bashrc setup.
#
# In .bashrc:
#   if [[ -f ~/.Jeffco_only.bashrc ]]; then
#       . ~/.Jeffco_only.bashrc
#   fi
#   source $HOME/ads3_environment.sh
#   source $HOME/.ftpconfig
# and copy .Jeffco_only.bashrc, ads3_environemtn.sh and .ftpconfig from a
# server where the standard RPMs are installed.

# To run a single test use the -p option. To run all tests, omit -p
#python3 -m unittest discover -s test -v -p test_createFileExt.py
#python3 -m unittest discover -s test -v -p test_step_through_files.py #-p test_find_lrt_netcdf.py
#python3 -m unittest discover -s test -v -p test_find_file.py
# --- Unit Tests ---
#python -m pytest -s test_push_data.py
# Specify how to run your unit tests. Replace with your actual command:
# Specify how to run your Pytest tests. Adjust or add command line options:
python -m pytest -s test/t2/

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
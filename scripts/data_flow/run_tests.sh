###############################################################################
# Shell script to call Python units tests. Configure environment (if not
# running on a server/groundstation/etc) and call tests.
#
# Written in Python 3
#
# COPYRIGHT:   University Corporation for Atmospheric Research, 2020
###############################################################################
# If running someplace the standard RPMs aren't installed, such as on a desktop
# MAC, configure a bunch of environment vars. These can also be used to
# override local config.
export PROJ_DIR="/Users/janine/dev/aircraft_projects"
export PROJECT="CAESAR"
export AIRCRAFT="C130_N130AR"
export RAW_DATA_DIR="/Users/janine/dev/projects"
export DATA_DIR="/Users/janine/dev/projects"
export FTPUSER=username  # usually project name, lower case
export FTPPWD=password
export FTPDATADIR=EOL_data/RAF_data
export FTPPARENTDIR=.
# To run a single test use the -p option. To run all tests, omit -p
python3 -m unittest discover -s test -v -p test_createConfigExt.py
#python3 -m unittest discover -s test -v

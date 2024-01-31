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
python3 -m unittest discover -s test -v -p test_createConfigExt.py
#python3 -m unittest discover -s test -v

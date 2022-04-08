#!/usr/bin/python
#
# Generic script to return aircraft, project, and instrument configuration onboard
#
# See ac_config.py for details.
#
#  COPYRIGHT: University Corporation for Atmospheric Research, 2015

import os
import sys
import ac_config

if len(sys.argv) < 2:
  sys.exit(1)

value = ac_config.get_config(sys.argv[1])

if value:
  print value

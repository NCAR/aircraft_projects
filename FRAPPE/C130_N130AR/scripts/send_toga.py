# -*- python -*-

# Run this script from cron something like this:
#
# */2 * * * * python /home/local/projects/FRAPPE/C130_N130AR/scripts/send_toga.py >>& /tmp/send_toga.log
#

import sys
sys.path.append("/home/local/raf/python")

import raf.toga
sys.exit(raf.toga.main(sys.argv))


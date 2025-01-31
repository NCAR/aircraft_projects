"Transfer TOGA data directories to the ground as zip files."


import os
import subprocess as sp
import glob
import time

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import raf.datepattern as datepattern
import raf.config
import raf.ac_config
import iss.time_tools as tt

from optparse import OptionParser

import logging

logger = logging.getLogger(__name__)

# rsync the toga data directory from the toga pc.
# look for the second-to-last .D directory.
# if no zip file yet, zip it and insert into ldm.

# GV_N677F 41% rsync -av rsync://toga-pc/toga/'2014-*' .
# receiving incremental file list
# 2014-01-09-1833.b/
# 2014-01-09-1833.b/2014-01-09-1833_002.D/
# 2014-01-09-1833.b/2014-01-09-1833_002.D/Audit.txt
# 2014-01-09-1833.b/2014-01-09-1833_002.D/CONTRAST_03.RES
# 2014-01-09-1833.b/2014-01-09-1833_002.D/CONTRAST_03.XLS
# 2014-01-09-1833.b/2014-01-09-1833_002.D/DATA.MS
# 2014-01-09-1833.b/2014-01-09-1833_002.D/PRE_POST.INI
# 2014-01-09-1833.b/2014-01-09-1833_002.D/acqmeth.txt
# 2014-01-09-1833.b/2014-01-09-1833_002.D/fileinfo.txt
# 2014-01-09-1833.b/2014-01-09-1833_002.D/fooport2.txt
# 2014-01-09-1833.b/2014-01-09-1833_003.D/
# 2014-01-09-1833.b/2014-01-09-1833_003.D/TEMPBASE
# 2014-01-09-1833.b/2014-01-09-1833_003.D/TEMPDAT
# 2014-01-09-1833.b/2014-01-09-1833_003.D/TEMPDIR
# 2014-01-09-1833.b/2014-01-09-1833_003.D/runstart.txt
# 2014-01-09-1833.b/CONTRAST_03.M/LastData.mac
# 2014-01-09-1833.b/CONTRAST_03.M/QDB.BAK
# 2014-01-09-1833.b/CONTRAST_03.M/tempevt.mac
# 
# sent 1186 bytes  received 425924 bytes  170844.00 bytes/sec
# total size is 114901475  speedup is 269.02

def zipfile_from_folder(path):
    cwd = os.path.abspath(os.path.dirname(path))
    if not cwd:
        raise Exception("path does not exist: " + path)
    base = os.path.basename(path)
    zipfile = os.path.join(cwd, 'TOGA_'+base+'.zip')
    return zipfile

def zip_toga_folder(path):
    # Run in the parent directory of the .D data folder
    cwd = os.path.abspath(os.path.dirname(path))
    base = os.path.basename(path)
    zipfile = zipfile_from_folder(path)
    args = ['zip', '-rv', zipfile, base]
    p = sp.Popen(args, shell=False, cwd=cwd)
    _pid_, _status_ = os.waitpid(p.pid, 0)

def find_latest_dirs(togatop, ndirs=1):
    dirs = glob.glob(togatop+"/*/*.D")
    dirs.sort()
    if len(dirs) > 1:
        dpath = dirs[-2]
        logging.info("latest finished directory: %s" % (dpath))
    return dirs[-ndirs-1:-1]


def main(argv):
    parser = OptionParser()
    serviceurl = "rsync://toga-pc/toga/"
    togatop = raf.ac_config.get_config("toga.path")

    # Add the options specific to send_toga
    parser.add_option("--interval", type="string", help="""\
Look for TOGA directories only within the time interval specified as
<begin>,<end>.  A time can be absolute in the form YYYYMMDD[HH[MM]], or
'now', or it can be relative to now using a minus sign prefix and units.
The end time can be omitted and defaults to now.  The default interval is
the last 8 hours, or '-8h,'.""", default="-8h,")
    parser.add_option("--ldmforce", help="""\
Force the latest zip file to be inserted into the LDM queue.""",
                      action="store_true", default=False)
    parser.add_option("--serviceurl", help="""\
The URL to the rsync service on the TOGA PC.
Defaults to '%s'.""" % (serviceurl), default=serviceurl)
    parser.add_option("--togatop", help="""\
The top directory to into which TOGA data directories will be downloaded.
Defaults to '%s'""" % (togatop), default=togatop)
    parser.add_option("--nzips", help="""\
Zip the NZIPS most recent TOGA directories for insertion into LDM.  The
default is 1.""", type="int", default=1)

    config = raf.config.Config()
    config.addOptions(parser)

    (options, argv) = parser.parse_args(argv)
    config.setOptions(options)
    times = tt.parseTimespan(options.interval)
    serviceurl = options.serviceurl
    togatop = options.togatop
    if not times[1]:
        times[1] = time.time()

    togadirpattern = "%Y-%m-%d-%H*.b/"
    dp = datepattern.DatePattern(togadirpattern)
    logging.debug("generating rsync patterns for interval (%s,%s)" %
                  (tt.formatTime(times[0]), tt.formatTime(times[1])))
    rsyncopts = dp.generateRsyncRules(times[0], times[1])
    rsync = config.Rsync(serviceurl, togatop, rsyncopts)
    rsync.run()
    dpaths = find_latest_dirs(togatop, options.nzips)
    if not dpaths:
        logging.info("No TOGA data directories found in " + togatop)
        return 1

    ldm = config.LDM()
    for dpath in dpaths:
        zipfile = zipfile_from_folder(dpath)
        ldmsend = options.ldmforce
        if os.path.exists(zipfile):
            logging.info("zipfile already exists: %s" % (zipfile))
        else:
            logging.info("zipping toga folder: %s" % (dpath))
            zip_toga_folder(dpath)
            ldmsend = True
        if ldmsend:
            # expire all but the last 15 minutes of TOGA products
            ldm.expire(0.25, r"TOGA_.*\.zip")
            ldm.insert(zipfile)
    return 0


# Run this script from cron something like this:
#
# */2 * * * * python /home/local/projects/FRAPPE/C130_N130AR/scripts/send_toga.py >>& /tmp/send_toga.log
#

if __name__ == "__main__":
    sys.exit(main(sys.argv))


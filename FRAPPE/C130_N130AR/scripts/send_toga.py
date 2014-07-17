
import os
import sys
import subprocess as sp
import glob

# rsync the toga data directory from the toga pc.
# look for the second-to-last .D directory.
# if no zip file yet, zip it and insert into ldm.

"""
GV_N677F 41% rsync -av rsync://toga-pc/toga/'2014-*' .
receiving incremental file list
2014-01-09-1833.b/
2014-01-09-1833.b/2014-01-09-1833_002.D/
2014-01-09-1833.b/2014-01-09-1833_002.D/Audit.txt
2014-01-09-1833.b/2014-01-09-1833_002.D/CONTRAST_03.RES
2014-01-09-1833.b/2014-01-09-1833_002.D/CONTRAST_03.XLS
2014-01-09-1833.b/2014-01-09-1833_002.D/DATA.MS
2014-01-09-1833.b/2014-01-09-1833_002.D/PRE_POST.INI
2014-01-09-1833.b/2014-01-09-1833_002.D/acqmeth.txt
2014-01-09-1833.b/2014-01-09-1833_002.D/fileinfo.txt
2014-01-09-1833.b/2014-01-09-1833_002.D/fooport2.txt
2014-01-09-1833.b/2014-01-09-1833_003.D/
2014-01-09-1833.b/2014-01-09-1833_003.D/TEMPBASE
2014-01-09-1833.b/2014-01-09-1833_003.D/TEMPDAT
2014-01-09-1833.b/2014-01-09-1833_003.D/TEMPDIR
2014-01-09-1833.b/2014-01-09-1833_003.D/runstart.txt
2014-01-09-1833.b/CONTRAST_03.M/LastData.mac
2014-01-09-1833.b/CONTRAST_03.M/QDB.BAK
2014-01-09-1833.b/CONTRAST_03.M/tempevt.mac

sent 1186 bytes  received 425924 bytes  170844.00 bytes/sec
total size is 114901475  speedup is 269.02
"""


def ldminsert(filepath):
    p = sp.Popen(["/home/ldm/bin/pqinsert", "-v", filepath], shell=False)
    pid, sts = os.waitpid(p.pid, 0)

def runrsync(source, dest):
    p = sp.Popen(["rsync", "-av", source, dest], shell=False)
    pid, sts = os.waitpid(p.pid, 0)

def zipfile_from_folder(path):
    cwd = os.path.abspath(os.path.dirname(path))
    base = os.path.basename(path)
    zipfile = os.path.join(cwd, 'TOGA_'+base+'.zip')
    return zipfile

def zip_toga_folder(path):
    # Run in the parent directory of the .D data folder
    cwd = os.path.abspath(os.path.dirname(path))
    base = os.path.basename(path)
    zipfile = zipfile_from_folder(path)
    args = ['zip', '-rv', zipfile, base ]
    p = sp.Popen(args, shell=False, cwd=cwd)
    pid, sts = os.waitpid(p.pid, 0)

def find_latest_dir(togatop):
    dpath = None
    dirs = glob.glob(togatop+"/*/*.D")
    dirs.sort()
    if len(dirs) > 1:
        dpath = dirs[-2]
        print("latest finished directory: %s" % (dpath))
    return dpath

if __name__ == "__main__":
    togatop = "/mnt/r1/toga"
    runrsync("rsync://toga-pc/toga/2014-*", togatop)
    dpath = find_latest_dir(togatop)
    zipfile = zipfile_from_folder(dpath)
    if os.path.exists(zipfile):
        print("zipfile already exists: %s" % (zipfile))
    else:
        print("zipping toga folder: %s" % (dpath))
        zip_toga_folder(dpath)
        ldminsert(zipfile)

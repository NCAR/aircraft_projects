
import os
import subprocess as sp

import logging

logger = logging.getLogger(__name__)

class LDM(object):

    "Encapsulate interaction with the local LDM service."

    def __init__(self):
        self.pqinsert = "/home/ldm/bin/pqinsert"
        self.pqexpire = "/home/ldm/bin/pqexpire"
        self.verbose = True
        self.dryrun = False

    def setDryrun(self, enabled):
        self.dryrun = enabled

    def _run(self, cmd):
        logger.info(" ".join(cmd))
        if self.dryrun:
            logger.info("ldm dryrun: ldm command not executed.")
        else:
            p = sp.Popen(cmd, shell=False)
            _pid_, _status_ = os.waitpid(p.pid, 0)

    def insert(self, filepath):
        cmd = [self.pqinsert]
        if self.verbose:
            cmd += ["-v"]
        cmd += [filepath]
        self._run(cmd)

    def expire(self, hours, pattern):
        "Expire products older than @p hours with @p pattern."
        cmd = [self.pqexpire]
        if self.verbose:
            cmd += ["-v"]
        cmd += ["-i", "0", "-a", str(hours), "-p", pattern]
        self._run(cmd)

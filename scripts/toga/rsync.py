
import subprocess as sp
import os

import logging

logger = logging.getLogger(__name__)


class Rsync(object):
    "Setup Rsync options and then run rsync."

    def __init__(self, source=None, dest=None, options=None):
        self.dryrun = False
        self.verbose = True
        self.options = options
        self.source = source
        self.dest = dest
        self.status = None

    def setDryrun(self, enabled):
        self.dryrun = enabled

    def setup(self, source, dest, options=None):
        self.options = options
        self.source = source
        self.dest = dest

    def _generate_command(self):
        cmd = ["rsync", "-a"]
        if self.dryrun:
            cmd += ["-n"]
        if self.verbose:
            cmd += ["-v"]
        if self.options:
            cmd += self.options
        cmd += [self.source, self.dest]
        return cmd
        
    def exitStatus(self):
        return self.status

    def run(self):
        cmd = self._generate_command()
        logger.info(" ".join(cmd))
        p = sp.Popen(cmd, shell=False)
        _pid_, status = os.waitpid(p.pid, 0)
        self.status = status
        return status


def runrsync(options, source, dest):
    rsync = Rsync(source, dest, options)
    return rsync.run()



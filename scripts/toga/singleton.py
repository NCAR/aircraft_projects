import sys
import os
import fcntl
import subprocess
import logging

logger = logging.getLogger(__name__)


# Taken from ActiveState example:
#
# http://code.activestate.com/recipes/578453-python-single-instance-cross-platform/
#

class SingleProcess(object):

    def __init__(self, name, lockpath=None):
        self.name = name
        self.lockpath = lockpath
        self.fp = None
        self.is_running = False
        if not self.lockpath:
            self.lockpath = "/var/tmp/raf-%s.lock" % (self.name)

    def try_lock(self):
        try:
            self.fp = open(self.lockpath, 'w')
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except EnvironmentError as err__:
            if self.fp is not None:
                self.is_running = True
            else:
                raise
        return self

    def lock_or_fail(self):
        self.try_lock()
        msg = "already locked: " + self.lockpath
        if self.is_running:
            logger.error(msg)
            raise Exception(msg)
        return self

    def clean_up(self):
        # this is not really needed
        try:
            if self.fp is not None:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                self.fp.close() # ???
                os.unlink(self.lockpath)
        except Exception as err__:
            # logger.exception(err)
            # for debugging porpuses, do not raise it on production
            pass 


def fork_check(operation, name):
    retcode = -1
    try:
        retcode = subprocess.call(["python", __file__, operation, name], 
                                  shell=False)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
        else:
            print >>sys.stderr, "Child returned", retcode
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e
    return retcode
    

def test_singleton():
    # Try to create the same singleton lock twice.  The
    # second should fail.
    name = "test_singleton"
    sp = SingleProcess(name).try_lock()
    assert not sp.is_running
    assert os.path.exists(sp.lockpath)
    assert fork_check("try_lock", name) == 1
    assert fork_check("lock_or_fail", name) == 2
    sp.clean_up()
    assert not os.path.exists(sp.lockpath)
    assert fork_check("try_lock", name) == 0


def main(operation, name):
    sp = SingleProcess(name)
    if operation == "try_lock":
        try:
            sp.try_lock()
            sys.exit(int(sp.is_running))
        except Exception as ex:
            print(str(ex))
            sys.exit(2)
    elif operation == "lock_or_fail":
        try:
            sp.lock_or_fail()
            sys.exit(int(sp.is_running))
        except Exception as ex:
            print(str(ex))
            sys.exit(2)


if __name__ == "__main__":

    main(sys.argv[1], sys.argv[2])



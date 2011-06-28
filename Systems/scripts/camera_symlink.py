#!/usr/bin/python

"""
Create a symbolic link to the latest recorded camera image in
/var/www/html/flight_data/images/
"""

# A watched directory will watch for new files and new directories.
# Any new directory detected will, in turn, be watched is the same
# manor as the the initial directory is.

import logging, logging.handlers
import os, sys, commands, pyinotify, re
from pyinotify import WatchManager, Notifier, ProcessEvent #, EventsCodes

mask = pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE

class transferNotifier(pyinotify.ProcessEvent):

#   def process_IN_CREATE(self, event):
#       logging.info("IN_CREATE saw:   %s" % event.pathname)

    def process_IN_CLOSE(self, event):
#       logging.info("IN_CLOSE  saw:   %s" % event.pathname)
        if event.dir: return

        m = reLatest.match(event.pathname)
        if m:
#           logging.info("IN_CLOSE  match: %s" % event.pathname)
            if os.path.islink(sym_link):
                os.remove(sym_link)
            os.symlink(event.pathname, sym_link)


def Monitor(data):

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, transferNotifier())
    wm.add_watch(data, mask, rec=True, auto_add=True)

    try:
        while 1:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        return


if __name__ == '__main__':

    data     = "/mnt/r2/camera_images/"
    logfile  = "/tmp/camera_symlink.log"
    sym_link = "/var/www/html/flight_data/images/latest_forward"

    # This regexp defines a constrained path to prevent falsly linking
    # to any rogue .jpg(s) that are created in the watched directory.
    # regexp hint:       any number of non...   /'s            .'s
    #                                         /----\         /----\
    reLatest = re.compile(data+"flight_number_[^\/]*/forward/[^\.]*\.jpg")

    # setup logging
    logger = logging.getLogger()
    handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=8192, backupCount=10)
    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    if not os.path.isdir(data):
        logging.critical("Folder '%s' does not exist, holding." % data)

    # hang until 'data' folder is created
    while (not os.path.isdir(data)):
        time.sleep(1)

    # watch the data folder for new files being created
    Monitor(data)

#!/usr/bin/python

"""
Create a sym_link of the latest recorded camera image into
/var/www/html/flight_data/images

This script will only send files it 'sees' being
created.
"""

import logging, logging.handlers
import os, sys, commands, pyinotify, threading, time, pg
from pyinotify import WatchManager, Notifier, ProcessEvent #, EventsCodes
from threading import Event, Thread


class PClose(ProcessEvent):

    def process_IN_CLOSE(self, event):
        if event.name.endswith('.jpg'):
            if os.path.isfile(event.path):
                fn = event.path
            else:
                fn = os.path.join(event.path, event.name)

            if os.path.islink(sym_link):
                os.remove(sym_link)
            os.symlink(fn, sym_link)


def check_flight_number():
    print "Checking for flight number"
    global t
    global data
    db = pg.connect('real-time-GV')
    pgq = db.query("SELECT value from global_attributes where key='FlightNumber'")
    if pgq.ntuples() > 0:
        camera_dir = os.path.join(data, "flight_number_")
        flight_num = pgq.getresult()[0]
        camera_dir = camera_dir + ''.join(flight_num)
        if (os.path.isdir(camera_dir)):
            global wm
            wm.rm_watch(data, rec=True)
            wm.add_watch(camera_dir, pyinotify.IN_CLOSE_WRITE)
            print "Monitoring directory: %s" % camera_dir
    db.close()
    t = threading.Timer(15.0, check_flight_number).start()


def Monitor(data):

    global wm
    notifier = Notifier(wm, PClose())
    wm.add_watch(data, pyinotify.IN_CLOSE_WRITE)

    try:
        while 1:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        return


if __name__ == '__main__':

    data    = "/mnt/r1/camera_images/"
    data    = "/tmp/camera_images/"
    logfile = "/tmp/camera_symlink.log"
    sym_link="/var/www/html/flight_data/images/latest_forward"
    sym_link="latest_forward"

    wm = WatchManager()

    # setup logging
    logger = logging.getLogger()
    handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=8192, backupCount=10)
    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    if not os.path.isdir(data):
        print "Folder '%s' does not exist, holding." % data
        logging.critical("Folder '%s' does not exist, holding." % data)

    # Set up periodic timmer to check for new flight number.
    t = threading.Timer(1.0, check_flight_number)
    t.start()

    while (not os.path.isdir(data)):
        time.sleep(1)

    # watch the data folder for new files being created
    wm = Monitor(data)

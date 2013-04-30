#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is a daemon process that listens for the postgres signal 'killiit'.
It is ment to be run on eol-rt-data.fl-ext.ucar.edu.

When this signal is received it kills all postgres process(es) that are
in an '<IDLE> in transaction' state that are accessing the real-time-GV
database.

To signal it simply connect to the exposed postgres database real-time-GV
(on eol-rt-data) and issue a 'NOTIFY killiit;' signal.

To observe the process before and after it is killed use this postgres
command:
SELECT * FROM pg_stat_activity;

Currently it is designed to only deal with hangups on the real-time-GV
database.
"""

from subprocess import *
import select
import psycopg2
import psycopg2.extensions


def nProcesses():
    p0 = Popen(["ps -ef | grep -c 'real-time-GV .* [i]dle in transaction'"],
               stdout=PIPE, shell=True)
    return int(p0.communicate()[0])


def killIIT():
    p0 = Popen(["ps -eo pid,command | grep 'real-time-GV .* [i]dle in transaction'"],
               stdout=PIPE, shell=True)
    p1 = Popen(["awk '{print \"kill \"$1}' | sh"],
               stdin=p0.stdout, stdout=PIPE, shell=True)
    p1.communicate()[0]


conn = psycopg2.connect("host='localhost' dbname='real-time-GV' user='ads'")
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

curs = conn.cursor()
curs.execute("LISTEN killiit;")

#print "conn.fileno() = ", conn.fileno()
#print "Waiting for notifications on channel 'killiit'..."
while 1:
    if select.select([conn.fileno()],[],[]) != ([],[],[]):
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop()
            #print "Got NOTIFY:", notify.pid, notify.channel

            if nProcesses():
                killIIT()

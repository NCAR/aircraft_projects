#!/bin/sh
#
# Start udp2sql to read UDP packets from the aircraft and write
# the data to the database
#

# Kill any running instances of udp2sql
killall udp2sql

# This is where the log will go
logfile="/tmp/udp2sql.log"

# Rotate the previous logfiles, if any
/usr/sbin/logrotate -s /tmp/.udp2sql.log.state /home/local/Systems/eol-rt-data/etc/logrotate.d/udp2sql

# Start the new udp2sql in background, logging to $logfile.
/opt/local/bin/udp2sql < /dev/null > $logfile 2>&1 &

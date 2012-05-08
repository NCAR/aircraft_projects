#!/bin/sh
#
# Start udp2sql to read UDP packets from the aircraft and write
# the data to the database
#

# This is where the log will go
logfile="/tmp/udp2sql.log"

# Rotate the previous logfiles, if any
/usr/sbin/logrotate -s /tmp/.udp2sql.log.state ../logrotate.d/udp2sql

# Kill any running instances of udp2sql
killall udp2sql

# Start the new udp2sql in background, logging to $logfile.  Assume that udp2sql
# lives in the same place as this script.
fullpath=`which $0`
homedir=${fullpath%/*}
$homedir/udp2sql < /dev/null > $logfile 2>&1 &

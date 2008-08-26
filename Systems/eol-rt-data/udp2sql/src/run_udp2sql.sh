#!/bin/sh
#
# Start udp2sql to read UDP packets from the aircraft and write
# the data to the database
#

# This is where the log will go
logfile="/tmp/udp2sql.log"

# Move the previous logfile, if any
if [[ -e $logfile ]]; then
	mv $logfile $logfile.old
fi

# Kill any running instances of udp2sql
killall udp2sql

# Start the new udp2sql in background, logging to $logfile.  Assume that udp2sql
# lives in the same place as this script.
fullpath=`which $0`
homedir=${fullpath%/*}
$homedir/udp2sql < /dev/null > $logfile 2>&1 &

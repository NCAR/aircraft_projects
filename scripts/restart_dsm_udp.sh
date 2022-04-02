#!/bin/bash

set -x

# Restart local dsm process

# Shutdown any existing process
if  test -f "/tmp/run/nidas/dsm.pid" ; then
    pkill -F /tmp/run/nidas/dsm.pid;
    for (( i = 0; i < 10; i++ )); do
        pgrep $(</tmp/run/nidas/dsm.pid) || break;
        sleep 5
        pkill -F /tmp/run/nidas/dsm.pid;
    rm /tmp/run/nidas/dsm.pid
    done
fi
ps ax | grep -w dsm | grep -qv grep
if [ $? -eq 1 ]; then
  rm /tmp/run/nidas/dsm.pid
  nohup dsm > /tmp/dsm.log &
fi

sleep 2

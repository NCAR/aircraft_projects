#!/bin/bash

unset HOST
unset AIRCRAFT

HOST='hyper.raf-guest.ucar.edu'
AIRCRAFT='DC8'

USAGE="usage: $0 [-h] [-s ...] [-a ...]
        -h help
        -s server name (default $HOST)
        -a Aircraft name (default $AIRCRAFT)"

while getopts hs:a: c; do
    case $c in
    h)    echo "$USAGE"; exit ;;
    s)    HOST=$OPTARG ;;
    a)    AIRCRAFT=$OPTARG ;;
    esac
done

echo "HOST:" $HOST
echo "AIRCRAFT:" $AIRCRAFT

cat /home/local/Systems/eol-rt-data/postgres/real-time-DC8_on_GV.sql | psql -h $HOST -U ads -d real-time-$AIRCRAFT

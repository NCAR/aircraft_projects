#!/bin/bash

unset HOST
unset AIRCRAFT

HOST='eol-rt-data.fl-ext.ucar.edu'
#AIRCRAFT='N43RF'

USAGE="usage: $0 [-h] [-s ...] [-a ...]
        -h help
        -s server name (default $HOST)
        -p Project name (default $PROJECT)
        -a Aircraft name (default $AIRCRAFT)
        -n Flight number (default $FLIGHT)"

while getopts hs:a:n:p: c; do
    case $c in
    h)    echo "$USAGE"; exit ;;
    s)    HOST=$OPTARG ;;
    p)    PROJECT=$OPTARG ;;
    a)    AIRCRAFT=$OPTARG ;;
    n)    FLIGHT=$OPTARG ;;
    esac
done

echo "HOST:" $HOST
echo "AIRCRAFT:" $AIRCRAFT
echo "FLIGHTNUM:" $FLIGHT

if [ -z "$AIRCRAFT" ];
    echo "AIRCRAFT must be set."
    exit 1
fi

cat real-time-init.sql | sed s/PROJECT/$PROJECT/ | sed s/FLIGHTNUM/$FLIGHT/ | sed s/PLATFORM/$AIRCRAFT/ | psql -h $HOST -U ads -d real-time-$AIRCRAFT

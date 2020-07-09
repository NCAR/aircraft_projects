#!/bin/sh

# run this script as root to install various scripts in locations
# where system utilities expect them.

sbins=(ddclient run_ddclient.sh)

for s in ${sbins[*]}; do
    [ ! -x $s ] chmod +x $s
    if [ ! -x /usr/sbin/$s ]; then
        rm -f /usr/sbin/$s
        ln -s $s /usr/sbin
    fi
done

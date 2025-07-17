#!/bin/bash

SERVER="192.168.84.2"
MOUNTPOINT="/var/r1/GOTHAAM/"

# Check if the mount point is already mounted
if ! mount | grep "$MOUNTPOINT" > /dev/null; then
    echo "$MOUNTPOINT not mounted" >&2
    # Try to mount the NFS share
    if ! mount -t nfs "$SERVER:$MOUNTPOINT" "$MOUNTPOINT"; then
        echo "Failed to mount $SERVER:$MOUNTPOINT on $MOUNTPOINT" >&2
        exit 1
    else
        echo "$SERVER mounted on $MOUNTPOINT"
    fi
else
    echo "$MOUNTPOINT already mounted"
fi

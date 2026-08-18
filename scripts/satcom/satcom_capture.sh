#!/bin/bash
###############################################################################
# Script to log traffic getting off the plane. Ignores traffic between
# onboard hosts
#  - Needs to run as root
#  - Need to change interface to satcom interface onboard.
# Options:
#  - Excludes onboard traffic between .84 subnets from logging
#  -i Interface
#  -C, -W  Creates up to 10 100MB log files. Rotates logs
#  -s Only snapshots 96 bytes of data, rather than the default 262144,
#     to decrease logsize.
###############################################################################
# During INSPYRE:
# - acserver: interface is eno8303np0
# - MC brix01: enp3s0
# - steam (for testing): enp0s31f6
######################################
# CHANGE ME!!!
interface="enp0s31f6"  # steam

logfile="satcom_capture.log"
output_dir="/var/log/ads/satcom/"

# Create logfile dir if needed
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir" ||
      { echo "could not create $dir" >> "$output_dir/$logfile" 2>&1; exit 1; }
fi

# Stamp logfile with date/time script started
date=$(date -u +%Y%m%d_%H%M%S)

# Some interface sanity checking
if [ ! -d "/sys/class/net/$interface" ]; then
    echo "interface $interface not found" >> "$output_dir/$logfile" 2>&1
    exit 1
fi
[ "$(cat /sys/class/net/$interface/operstate)" = "up" ] ||
  { echo "$interface is down" >> "$output_dir/$logfile" 2>&1; exit 1; }


tcpdump 'not (src net 192.168.84.0/24 and dst net 192.168.84.0/24)' \
    -i ${interface} \
    -w /var/log/satcom-capture/traffic${date}.pcap \
    -C 100 \
    -W 10 \
    -s 96 >> "$output_dir/$logfile" 2>&1

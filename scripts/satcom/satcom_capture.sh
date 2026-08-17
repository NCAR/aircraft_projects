#!/bin/bash
# Needs to run as root
# Need to change interface to satcom interface onboard
# - acserver: interface is eno8303np0
# - MC brix01: enp3s0
# - steam (for testing): enp0s31f6
# Options:
#  - Excludes onboard traffic between .84 subnets from logging
#  -C, -W  Creates up to 10 1GB log files. Rotates logs
#  -s Only snapshots 96 bytes of data, rather than the default 262144,
#     to decrease logsize.
tcpdump 'not (src net 192.168.84.0/24 and dst net 192.168.84.0/24)' \
    -i enp0s31f6 \
    -w /var/log/satcom-capture/traffic.pcap \
    -C 1000 \
    -W 10 \
    -s 96

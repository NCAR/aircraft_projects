#!/bin/bash
# Needs to run as root
# Need to change interface to satcom interface onboard
tcpdump -i enp0s31f6 \
    -w /var/log/satcom-capture/traffic.pcap \
    -C 100 \
    -W 5

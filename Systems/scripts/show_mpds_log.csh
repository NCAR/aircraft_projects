#!/bin/csh
tail -f /var/log/messages | grep -e ppp -e ddclient

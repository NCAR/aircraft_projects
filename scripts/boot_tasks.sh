#!/bin/bash

# Set netowrk MTU to max 9000 bytes.  We haven't figured out how to make this permanent yet.
ifc=`ip -o -4 route show to default | awk '{print $5}'`
ip link set $ifc mtu 9000


# Chat server
# moved into systemctl 
#/home/ads/unrealircd/unrealircd start > /dev/null 2>&1

# nag irc chat bot
CHATSRV="acserver.raf.ucar.edu:6668"
CHATROOM="#daq-c130"

if [ "$AIRCRAFT" = "GV_N677F" ]; then
  CHATROOM="#daq-gv"
fi


/usr/bin/nagircbot -e -C -s $CHATSRV -c \\$CHATROOM -n nagiosBOT -p CHAT_PASSWORD -f /var/log/nagios/status.dat -I 0

# Perform some basic housekeeping / clean up.
rm -f /tmp/nimbus.pid /tmp/run/nidas/*.pid

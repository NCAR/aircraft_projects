# nag irc chat bot
CHATSRV="acserver.raf.ucar.edu:6668"
CHATROOM="#network,#daq-c130,#c130q,#caesar"
CHATNIC="c130bot"

if [ "$AIRCRAFT" = "GV_N677F" ]; then
  CHATROOM="#daq-gv"
  CHATNIC="gvbot"
fi

#/usr/bin/nagircbot -e -C -s acserver.raf.ucar.edu:6668 -c \#daq-c130 -n nagiosBOT -p t@lksci3nc3 -f /var/log/nagios/status.dat -I 0

/usr/bin/nagircbot -e -C -s $CHATSRV -c \\$CHATROOM -n $CHATNIC -p t@lksci3nc3 -f /var/log/nagios/status.dat -I 0

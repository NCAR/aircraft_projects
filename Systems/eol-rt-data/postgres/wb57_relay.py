#!/usr/bin/python

# This script was written for the TCI campaign to ingest WB57 IWG1 real-time
# data and send it UDP to eol-rt-data for use in mission coordinator / catalog
# maps.
# Chris Webster, July 24 2015

import socket
import time
import urllib2

# eol-rt-data
UDP_IP = "128.117.188.122"
UDP_PORT = 31007


# Sample input.
# {"data":["IWG1","2015-06-25T03:28:43Z",29.649188,-95.164604,0,0,0,600,58.111478512406,0,0,0,0,178,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"type":"ASDI","id":"fa_7058"}

prev_content = ""
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while 1:
  time.sleep(5)

  print "reading"
  response = urllib2.urlopen("http://asp2.arc.nasa.gov/dashlite/dash.php?ACTION=FETCH_LAST_POS&CALLSIGN=NASA928", timeout = 10)
  content = response.read()

  if content == prev_content:
    continue

  prev_content = content

  # substring between square brackets and remove all quotes.
  s = content[content.find('[')+1:content.find(']')]
  s = s.replace('"', '')
  values = s.split(',')

  # Extract date/time and clean it up.
  dt = values[1].replace('Z', '')
  dt = dt.replace('-', '')
  dt = dt.replace(':', '')

  # Construct output
  output = "WB57," + dt
  for val in values[2:len(values)]:
    output = output + "," + val

  sock.sendto(output, (UDP_IP, UDP_PORT))

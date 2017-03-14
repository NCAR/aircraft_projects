#!/bin/bash

# RHEL/CentOS 7 no longer use eth# (0-3).  Our first server they were named em# (1-4).
# Wait and see on how more servers get their ethernet interfaces names.

#
# Work zone is hangar / guest net.
# External zone is SATCOM
#
firewall-cmd --permanent --set-default-zone=work
firewall-cmd --permanent --zone=trusted --add-interface=em1
firewall-cmd --permanent --zone=trusted --add-interface=em2
firewall-cmd --permanent --zone=work --add-interface=em3
firewall-cmd --permanent --zone=external --add-interface=em4

#
# NAT and masquerading.
#
firewall-cmd --permanent --direct --add-rule ipv4 nat POSTROUTING 0 -o em3 -j MASQUERADE
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em1 -o em3 -j ACCEPT
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em3 -o em1 -m state --state RELATED,ESTABLISHED -j ACCEPT
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em2 -o em3 -j ACCEPT
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em3 -o em2 -m state --state RELATED,ESTABLISHED -j ACCEPT

#
# For SATCOM NAT and masquerading we should add restrictions back that only computers
# in 192.168.x.[0-64] range can get out.
#
firewall-cmd --permanent --direct --add-rule ipv4 nat POSTROUTING 0 -o em4 -j MASQUERADE
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em1 -o em4 -j ACCEPT
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em4 -o em1 -m state --state RELATED,ESTABLISHED -j ACCEPT
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em2 -o em4 -j ACCEPT
firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i em4 -o em2 -m state --state RELATED,ESTABLISHED -j ACCEPT

#
# Hangar network.
#
# Allow ssh, http, ldm, postgresql, and RIC.
#
firewall-cmd --permanent --zone=work --add-service=ssh
firewall-cmd --permanent --zone=work --add-service=http
firewall-cmd --permanent --zone=work --add-port=388/tcp
firewall-cmd --permanent --zone=work --add-port=5432/tcp
firewall-cmd --permanent --zone=work --add-port=32001/udp
firewall-cmd --permanent --zone=work --add-port=32002/udp

#
# SATCOM
#
# Restrict incoming connections (ssh, http, ldm, and RIC) to UCAR subnets (128.117.0.0).
#
firewall-cmd --permanent --zone=external --add-rich-rule='
  rule family="ipv4"
  source address="128.117.0.0/16"
  port protocol="tcp" port="22" accept'

firewall-cmd --permanent --zone=external --add-rich-rule='
  rule family="ipv4"
  source address="128.117.0.0/16"
  port protocol="tcp" port="80" accept'

firewall-cmd --permanent --zone=external --add-rich-rule='
  rule family="ipv4"
  source address="128.117.0.0/16"
  port protocol="tcp" port="388" accept'

firewall-cmd --permanent --zone=external --add-rich-rule='
  rule family="ipv4"
  source address="128.117.0.0/16"
  port protocol="udp" port="32001" accept'

firewall-cmd --permanent --zone=external --add-rich-rule='
  rule family="ipv4"
  source address="128.117.0.0/16"
  port protocol="udp" port="32002" accept'


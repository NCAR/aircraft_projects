#!/bin/bash

# set -x

modprobe ip_tables
modprobe ip_conntrack
modprobe ip_conntrack_ftp

# 0/0 is anywhere
# ! 0/0 is nowhere
# x.x.x.x/N
#	N is bits in netmask

# Set forwarding, either 0(no) or 1(yes)
forward=1

# Interfaces connected to the big-bad internet
EXT_IFS=(eth2 eth3)

# Internal trusted interfaces
INT_IFS=(lo eth0 eth1)

SSH_OUTGOING=(0/0)

SSH_INCOMING=(0/0)

POSTGRES=(128.117.0.0/16)

# pop
# POP_SVRS=(128.117.80.208)
POP_SVRS=()

# IMAP_SVRS=128.117.80.208
IMAP_SVRS=()

# SMTP_OUT=128.117.80.208
SMTP_OUT=()

# SMTP_IN = 128.117.80.208
SMTP_IN=()

# who is allowed to ping me
# EXT_PING_HOST=128.117.80.208
EXT_PING_HOST=(0/0)

# who is allowed to make requests to our http server
# HTTP_CLNTS=128.117.0.0/16
HTTP_CLNTS=(0/0)

# who is allowed to make outgoing http requests
HTTP_REQUESTERS=(192.168.84.20 192.168.84.21)

# which IRC servers can we connect to
IRC_SERVERS=(0/0)

# RPC_CLIENTS=128.117.80.0/8
RPC_CLIENTS="! 0/0"

# on rh7.3, outgoing traceroute was using a source port of 1050
# TR_SRC_PORTS="32769:65535"
TR_SRC_PORTS="1050:65535"

TR_DEST_PORTS="33434:33523"

LOOPBACK="127.0.0.0/8"
CLASS_A="10.0.0.0/8"
CLASS_B="172.16.0.0/12"
CLASS_C="192.168.0.0/16"
CLASS_D_MULTICAST="224.0.0.0/4"
CLASS_E_RESERVED_NET="240.0.0.0/5"
P_PORTS="0:1023"
UP_PORTS="1024:65535"

# Flush tables
# flush (delete all rules one by one) all chains in the -t filter table
iptables -F
# delete every non-builtin chain in the table
iptables -X
iptables -Z

# iptables -F INPUT
# iptables -F OUTPUT
# iptables -F FORWARD
# iptables -t nat -F POSTROUTING
iptables -t nat -F

# default policy
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

# disable response to ping
# /bin/echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_all
/bin/echo "0" > /proc/sys/net/ipv4/icmp_echo_ignore_all

# disable response to broadcasts
# You don't want yourself becoming a Smurf amplifier.
/bin/echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts

# Don't accept source routed packets. Attackers can use source routing to generate
# traffic pretending to be from inside your network, but which is routed back along
# the path from which it came, namely outside, so attackers can compromise your
# network. Source routing is rarely used for legitimate purposes.
/bin/echo "0" > /proc/sys/net/ipv4/conf/all/accept_source_route

# Disable ICMP redirect acceptance. ICMP redirects can be used to alter your routing
# tables, possibly to a bad end.
for interface in /proc/sys/net/ipv4/conf/*/accept_redirects; do
   /bin/echo "0" > ${interface}
done

# Enable bad error message protection.
/bin/echo "1" > /proc/sys/net/ipv4/icmp_ignore_bogus_error_responses 

# Turn on reverse path filtering. This helps make sure that packets use
# legitimate source addresses, by automatically rejecting incoming packets
# if the routing table entry for their source address doesn't match the network
# interface they're arriving on. This has security advantages because it prevents
# so-called IP spoofing, however it can pose problems if you use asymmetric routing
# (packets from you to a host take a different path than packets from that host to you)
# or if you operate a non-routing host which has several IP addresses on different
# interfaces. (Note - If you turn on IP forwarding, you will also get this).
for interface in /proc/sys/net/ipv4/conf/*/rp_filter; do
   /bin/echo "1" > ${interface}
done

# Log spoofed packets, source routed packets, redirect packets.
/bin/echo "1" > /proc/sys/net/ipv4/conf/all/log_martians

# Set forwarding
/bin/echo $forward > /proc/sys/net/ipv4/ip_forward 

# allow anything on trusted interfaces
for iif in ${INT_IFS[*]}; do
    iptables -A INPUT -i $iif -j ACCEPT
    iptables -A OUTPUT -o $iif -j ACCEPT
    iptables -A FORWARD -i $iif -j ACCEPT
    iptables -A FORWARD -o $iif -j ACCEPT
done

## SYN-FLOODING PROTECTION
# This rule maximises the rate of incoming connections. In order to do this we divert tcp
# packets with the SYN bit set off to a user-defined chain. Up to limit-burst connections
# can arrive in 1/limit seconds ..... in this case 4 connections in one second. After this, one
# of the burst is regained every second and connections are allowed again. The default limit
# is 3/hour. The default limit burst is 5.
#
# taken from http://www.cs.princeton.edu/~jns/security/iptables

iptables -N syn-flood
for eif in ${EXT_IFS[*]}; do
    iptables -A INPUT -i $eif -p tcp --syn -j syn-flood
done

iptables -A syn-flood -m limit --limit 1/s --limit-burst 4 -j RETURN
iptables -A syn-flood -j DROP

# make sure NEW tcp connections are SYN packets
for eif in ${EXT_IFS[*]}; do
    iptables -A INPUT -i $eif -p tcp \! --syn -m state --state NEW -j DROP
done

for eif in ${EXT_IFS[*]}; do
    ## SPOOFING
    # Most of this anti-spoofing stuff is theoretically not really necessary with the flags we
    # have set in the kernel above ........... but you never know there isn't a bug somewhere in
    # your IP stack.
    #
    # Refuse spoofed packets pretending to be from your IP address.
    # iptables -A INPUT  -i $eif -s $IPADDR -j DROP
    # Refuse packets claiming to be from a Class A private network.
    iptables -A INPUT  -i $eif -s $CLASS_A -j DROP
    # Refuse packets claiming to be from a Class B private network.
    iptables -A INPUT  -i $eif -s $CLASS_B -j DROP
    # Refuse packets claiming to be from a Class C private network.
    iptables -A INPUT  -i $eif -s $CLASS_C -j DROP
    # Refuse Class D multicast addresses. Multicast is illegal as a source address.
    iptables -A INPUT -i $eif -s $CLASS_D_MULTICAST -j DROP
    # Refuse Class E reserved IP addresses.
    iptables -A INPUT -i $eif -s $CLASS_E_RESERVED_NET -j DROP
    #
    # Refuse packets claiming to be to the loopback interface.
    # Refusing packets claiming to be to the loopback interface protects against
    # source quench, whereby a machine can be told to slow itself down by an icmp source
    # quench to the loopback.
    iptables -A INPUT  -i $eif -d $LOOPBACK -j DROP
    # Refuse broadcast address packets.
    # iptables -A INPUT -i $eif -d $BROADCAST -j DROP
done

## ===================================================================
## ICMP
# We prefilter icmp by pulling it off to user-dfined chains so that we can restrict which
# types are allowed from the beginning rather than leaving it to the connection tracking.
# For instance, we don't want redirects whatever happens.
# In case you hadn't realised, ICMP scares me ...................
#
#  0: echo reply (pong)
#  3: destination-unreachable (port-unreachable, fragmentation-needed etc).
#  4: source quench
#  5: redirect
#  8: echo request (ping)
#  9: router advertisement
# 10: router solicitation
# 11: time-exceeded
# 12: parameter-problem
# 13: timestamp request
# 14: timestamp reply
# 15: information request
# 16: information reply
# 17: address mask request
# 18: address mask reply


iptables -N icmp-in
iptables -N icmp-out

for eif in ${EXT_IFS[*]}; do
    iptables -A INPUT  -i $eif -p icmp -j icmp-in
    iptables -A OUTPUT -o $eif -p icmp -j icmp-out

    # Accept 0,3,4,11,12,14,16,18 in.
    # These all had "-d $IPADDR" on them. Removed, GDM, Aug 2003
    iptables -A icmp-in -i $eif -p icmp --icmp-type 0  -s 0/0 -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 3  -s 0/0 -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 4  -s 0/0 -j RETURN
    # specify ACCEPT here. If RETURN, then it will be rejected later because we
    # don't have NEW in --state when returning from icmp-in chain to INPUT chain.
    for host in ${EXT_PING_HOST[*]}; do
	iptables -A icmp-in -i $eif -p icmp --icmp-type echo-request -s $host -m limit --limit 6/minute -j ACCEPT
    done
    iptables -A icmp-in -i $eif -p icmp --icmp-type 11 -s 0/0 -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 12 -s 0/0 -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 14 -s 0/0 -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 16 -s 0/0 -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 18 -s 0/0 -j RETURN
    # Allow 4,8,12,13,15,17 out.
    # These had "-s $IPADDR"
    iptables -A icmp-out -o $eif -p icmp --icmp-type echo-reply -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 4 -d 0/0 -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 8 -d 0/0 -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 12 -d 0/0 -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 13 -d 0/0 -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 15 -d 0/0 -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 17 -d 0/0 -j RETURN


    # Any ICMP not already allowed is logged and then dropped.
    iptables -A icmp-in  -i $eif -j LOG --log-prefix "IPTABLES ICMP-BAD-TYPE-IN: "
    iptables -A icmp-in  -i $eif -j DROP
    iptables -A icmp-out -o $eif -j LOG --log-prefix "IPTABLES ICMP-BAD-TYPE-OUT: "
    iptables -A icmp-out -o $eif -j DROP

    # Now we have returned from the icmp-in chain allowing only certain types
    # of icmp inbound, we can accept it if it is related to other connections
    # (e.g a time exceed from a traceroute) or part of an established one
    # (e.g. an echo reply)
    iptables -A INPUT  -i $eif -p icmp -m state --state ESTABLISHED,RELATED -j ACCEPT
    # Now we have returned from the icmp-out chain allowing only certain types
    # of icmp outbound, we can just accept it under all circumstances.
    iptables -A OUTPUT -o $eif -p icmp -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
done
# ============================================================================
  
for eif in ${EXT_IFS[*]}; do

    # tcp and udp established connections
    iptables -A INPUT -i $eif -p tcp -m state --state ESTABLISHED -j ACCEPT
    iptables -A OUTPUT -o $eif -p tcp -m state --state ESTABLISHED -j ACCEPT
    iptables -A INPUT -i $eif -p udp -m state --state ESTABLISHED -j ACCEPT
    iptables -A OUTPUT -o $eif -p udp -m state --state ESTABLISHED -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -i $eif -p tcp -m state --state ESTABLISHED -j ACCEPT
	iptables -A FORWARD -o $eif -p tcp -m state --state ESTABLISHED -j ACCEPT
	iptables -A FORWARD -i $eif -p udp -m state --state ESTABLISHED -j ACCEPT
	iptables -A FORWARD -o $eif -p udp -m state --state ESTABLISHED -j ACCEPT
    fi

    # port 20=ftp-data, 21=ftp

    # good reference:
    #	http://www.sns.ias.edu/~jns/security/iptables/iptables_conntrack.html
    # starting ftp connection
    iptables -A OUTPUT -o $eif -p tcp --dport 21 -m state --state NEW -j ACCEPT 

    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -p tcp --dport 21 -m state --state NEW -j ACCEPT
    fi

    # active ftp
    iptables -A INPUT -i $eif -p tcp --sport 20 -m state --state RELATED -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -i $eif -p tcp --sport 20 -m state --state RELATED -j ACCEPT
    fi

    # passive ftp
    iptables -A OUTPUT -o $eif -p tcp --sport 1024: --dport 1024:  -m state --state RELATED -j ACCEPT

    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -p tcp --sport 1024: --dport 1024:  -m state --state RELATED -j ACCEPT
    fi


    for host in ${SSH_OUTGOING[*]}; do
	# outgoing ssh to sshd on remote systems (ssh originations from here)
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport ssh -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport ssh -m state --state NEW -j ACCEPT
	fi
    done

    for host in ${SSH_INCOMING[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport ssh -m state --state NEW -j ACCEPT
	# don't do forwarding of incoming SSH 
    done

    for host in ${POSTGRES[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport postgres -m state --state NEW -j ACCEPT
	iptables -A INPUT -i $eif -s $host -p udp --dport postgres -m state --state NEW -j ACCEPT
    done

  
    for host in ${IMAP_SVRS[*]}; do
	# outgoing imap
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport imap -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport imap -m state --state NEW -j ACCEPT
	fi

	# outgoing imap3
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport imap3 -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport imap3 -m state --state NEW -j ACCEPT
	fi

	# outgoing imap-ssl
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport imaps -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport imaps -m state --state NEW -j ACCEPT
	fi
    done

    # outgoing pop
    for host in ${POP_SVRS[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport pop2 -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport pop2 -m state --state NEW -j ACCEPT
	fi

	# outgoing pop3
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport pop3 -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport pop3 -m state --state NEW -j ACCEPT
	fi

	# outgoing pop3s
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport pop3s -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport pop3s -m state --state NEW -j ACCEPT
	fi
    done

    # outgoing dns (udp)
    iptables -A OUTPUT -o $eif -p udp --dport domain -m state --state NEW -j ACCEPT

    # forwarding dns (not necessary since we're a caching nameserver)
    # if [ $forward -eq 1 ]; then
	# iptables -A FORWARD -o $eif -p udp --dport domain -m state --state NEW -j ACCEPT
    # fi

    # outgoing http requests to remote servers
    iptables -A OUTPUT -o $eif -p tcp --dport http -m state --state NEW -j ACCEPT
    iptables -A OUTPUT -o $eif -p udp --dport http -m state --state NEW -j ACCEPT
    iptables -A OUTPUT -o $eif -p tcp --dport https -m state --state NEW -j ACCEPT
    iptables -A OUTPUT -o $eif -p udp --dport https -m state --state NEW -j ACCEPT
    for host in ${HTTP_REQUESTERS[*]}; do
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -s $host -p tcp --dport http -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $host -p udp --dport http -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $host -p tcp --dport https -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $host -p udp --dport https -m state --state NEW -j ACCEPT
         fi
    done

    for host in ${HTTP_CLNTS[*]}; do
	# incoming http requests to our server
	iptables -A INPUT -i $eif -s $host -p tcp --dport http -m state --state NEW -j ACCEPT
	iptables -A INPUT -i $eif -s $host -p udp --dport http -m state --state NEW -j ACCEPT

	# incoming https
	iptables -A INPUT -i $eif -s $host -p tcp --dport https -m state --state NEW -j ACCEPT
	iptables -A INPUT -i $eif -s $host -p udp --dport https -m state --state NEW -j ACCEPT
    done

    # outgoing ntp (udp)
    iptables -A OUTPUT -o $eif -p udp --dport ntp -m state --state NEW -j ACCEPT
    # disable forwarding of ntp
    # if [ $forward -eq 1 ]; then
	# iptables -A FORWARD -o $eif -p udp --dport ntp -m state --state NEW -j ACCEPT
    # fi

    # outgoing smtp
    for smtp in ${SMTP_OUT[*]}; do
	iptables -A OUTPUT -o $eif -d $smtp -p tcp --dport smtp -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -p tcp --dport smtp -m state --state NEW -j ACCEPT
	fi
    done

    # incoming smtp
    for smtp in ${SMTP_IN[*]}; do
	iptables -A INPUT -i $eif -s $smtp -p tcp --dport smtp -m state --state NEW -j ACCEPT
    done

    # irc
    for host in ${IRC_SERVERS[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport irc -m state --state NEW -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p udp --dport irc -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport irc -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -d $host -p udp --dport irc -m state --state NEW -j ACCEPT
	fi
    done


    # incoming rpc clients
    # iptables -A INPUT -i $EXT_IF -s $RPC_CLIENTS -p tcp --sport sunrpc -j ACCEPT
    # iptables -A INPUT -i $EXT_IF -s $RPC_CLIENTS -p udp --sport sunrpc -j ACCEPT

    ## TRACEROUTE
    # Outgoing traceroute anywhere.
    # The reply to a traceroute is an icmp time-exceeded which is allowed by icmp-in
    iptables -A OUTPUT -o $eif -p udp \
	--sport $TR_SRC_PORTS --dport $TR_DEST_PORTS \
	-m state --state NEW -j ACCEPT 
    iptables -A INPUT -i $eif -p udp \
	--sport $TR_SRC_PORTS --dport $TR_DEST_PORTS \
	-m state --state NEW -j ACCEPT 

    # accept fragments (do we need this?)
    # iptables -A OUTPUT -f -j ACCEPT
    # iptables -A INPUT -f -j ACCEPT

    # iptables -A FORWARD -m limit -j LOG --log-prefix iptables_FORWARD \
	#	--log-level info

    ## LOGGING
    # You don't have to split up your logging like I do below, but I
    # prefer to do it this way because I can then grep for things in
    # the logs more easily. One thing you probably want to do is rate-limit
    # the logging. I didn't do that here because it is probably best not too
    # when you first set things up. You actually really want to see
    # everything going to the logs to work out what isn't working and why.
    # You can implement logging with "-m limit --limit 6/h --limit-burst 5"
    # (or similar) before the -j LOG in each case.
    #
    # Any udp not already allowed is logged and then dropped.
    iptables -A INPUT  -i $eif -p udp -j LOG --log-prefix "IPTABLES UDP-IN: "
    iptables -A INPUT  -i $eif -p udp -j DROP
    iptables -A OUTPUT -o $eif -p udp -j LOG --log-prefix "IPTABLES UDP-OUT: "
    iptables -A OUTPUT -o $eif -p udp -j DROP
    # Any icmp not already allowed is logged and then dropped.
    iptables -A INPUT  -i $eif -p icmp -j LOG --log-prefix "IPTABLES ICMP-IN: "
    iptables -A INPUT  -i $eif -p icmp -j DROP
    iptables -A OUTPUT -o $eif -p icmp -j LOG --log-prefix "IPTABLES ICMP-OUT: "
    iptables -A OUTPUT -o $eif -p icmp -j DROP
    # Any tcp not already allowed is logged and then dropped.
    iptables -A INPUT  -i $eif -p tcp -j LOG --log-prefix "IPTABLES TCP-IN: "
    iptables -A INPUT  -i $eif -p tcp -j DROP
    iptables -A OUTPUT -o $eif -p tcp -j LOG --log-prefix "IPTABLES TCP-OUT: "
    iptables -A OUTPUT -o $eif -p tcp -j DROP
    # Anything else not already allowed is logged and then dropped.
    # It will be dropped by the default policy anyway, but let's be paranoid.
    iptables -A INPUT  -i $eif -j LOG --log-prefix "IPTABLES PROTOCOL-X-IN: "
    iptables -A INPUT  -i $eif -j DROP
    iptables -A OUTPUT -o $eif -j LOG --log-prefix "IPTABLES PROTOCOL-X-OUT: "
    iptables -A OUTPUT -o $eif -j DROP

    # NAT
    if [ $forward -eq 1 ]; then
	iptables -t nat -A POSTROUTING -o $eif -j MASQUERADE
    fi
done

# THE END
echo "# Generated by NCAR/EOL hackers: `pwd`/`basename $0` on `date`" > /etc/sysconfig/iptables
iptables-save >> /etc/sysconfig/iptables


#!/bin/sh

# This file is part of the raf-ac-firewall package.
# Suggestion: don't edit this file, instead change the RPM source
# and re-install.
#
# iptables firewall settings for the RAF aircraft servers
#
# This script does the following:
# 1. provides forwarding of traffic between internal subnets
# 2. provides firewall security on external interfaces which are
#    listed in $EXT_IFS.
#    Rules for the following tcp/udp services are provided:
#    FTP,SSH,IMAP varieties,POP varieties, DNS, HTTP, HTTPS,
#    NTP, SMTP, IRC, VPN, traceroute.  All other tcp/udp ports
#    are blocked.  icmp packets are also limited. Other
#    protocols are blocked.
# 3. limits the ping rate and connection rate to protect bandwidth.
# 4. provides forwarding and NAT so systems on internal private
#    subnets can have restricted access to the internet.
#    One can control which internal hosts can connect, which
#    services (ports) and where they can connect to.
#    The idea here is to save $$ and control bandwidth on the satcom. 
# 5. it can provide port forwarding (DNAT), to allow outside
#    systems to connect to specific systems on the internal
#    subnets using a special port (an outside user could access
#    an internal web server, or ssh to an internal host).
# 6. logs a limited number of rejected packets on syslog
#    (/var/log/messages), so look there if something isn't working.
#
# Running this script sets the current iptables firewall rules, and
# saves them the /etc/sysconfig/iptables, so they will be
# in effect after the next boot.
#		
# Much of this was taken from
#	http://www.cs.princeton.edu/~jns/security/iptables
# a few years back.
#
# In general we try to log blocked packets before doing a DROP, or REJECT,
# so that we have a change to figure out what is going on.
#
# set -x

modprobe ip_tables
modprobe ip_conntrack
modprobe ip_conntrack_ftp

# x.x.x.x/N
#	N is bits in netmask
# 0/0 is anywhere
ANYHOST=0/0
# ! 0/0 is nowhere (but you have to watch out for shell mangling of !)
# We'll use 0/32, meaning network part must match exactly 0.0.0.0
# NOHOST
NOHOST=0/32

# are we forwarding? Set this in /etc/sysctl.conf
forward=$(</proc/sys/net/ipv4/ip_forward)

# External interfaces connected to the big-bad internet

# External interface connected through UCAR guest network.
# This is already firewalled, we just have to do FORWARDING.
# If VPN is up then cipsec0 is trusted.
SAFE_EXT_IFS=(eth2 cipsec+)

# Unsafe, external interfaces which are not firewalled for us. We
# want to do firewalling, but don't need to limit traffic
CHEAP_EXT_IFS=()

# Slow and expensive external interfaces.
SATCOM_EXT_IFS=(ppp+ eth3)

UNSAFE_EXT_IFS=(${CHEAP_EXT_IFS[*]} ${SATCOM_EXT_IFS[*]})

# Internal trusted interfaces. Forwarding is done between first two
INT_IFS=(eth0 eth1)

# Currently all hosts can do SSH and IRC off the plane.
#
# Privileged hosts can do more: HTTP, IMAP, etc.
# 192.168.84.0/27 = 192.168.84.0-31
# 192.168.84.0/26 = 192.168.84.0-63
# 192.168.84.0/24 = 192.168.84.*
PRIV_HOSTS_DISP=192.168.84.0/24
PRIV_HOSTS_DATA=192.168.184.0/24

# external hosts that we can ssh to
SSH_OUTGOING=($ANYHOST)

# external hosts that can ssh into our systems
# may want to limit this to known systems
# like 128.117.0.0/16 to avoid password guessers.
SSH_INCOMING=($ANYHOST)

# Google Earth SATCOM block.
# April 2008:
#   google earth uses kh.google.com which is 64.233.167.91
#   maps.google.com is 64.233.167.{99,104,147}
#   72.14.203.91 is ro-in-f91.google.com (not sure what that provides)
#   google.com is 64.233.167.99, 64.233.187.99, 72.14.207.99
#   So blocking 64.233.167.0/24 will also block normal google searches
GOOGLE_EARTH=(72.14.203.0/24 64.233.167.0/24)

# external vpn servers
VPN_SVRS=(192.43.244.230 192.143.244.231)

# external hosts that can establish incoming postgres connections
POSTGRES_IN=(128.117.0.0/16)

# LDM
LDM_IN_OUT=(128.117.0.0/16)

# Who is allowed to send us smtp packets
SMTP_IN=()

# who is allowed to ping me
EXT_PING_HOST=(128.117.0.0/16)

# who is allowed to make requests of our http server
# HTTP_CLNTS=(128.117.0.0/16)
HTTP_CLNTS=($ANYHOST)

# who can make requests of outside servers
HTTP_REQUESTERS=($PRIV_HOSTS_DATA $PRIV_HOSTS_DISP)

# which IRC servers can we connect to
IRC_SERVERS=($ANYHOST)

# RPC (ldm also uses RPC)
RPC_CLIENTS=(128.117.0.0/16)
RPC_SERVERS=(128.117.0.0/16)

# ports used by traceroute
TR_DEST_PORTS="33434:33523"

LOOPBACK="127.0.0.0/8"
CLASS_A="10.0.0.0/8"
CLASS_B="172.16.0.0/12"
CLASS_C="192.168.0.0/16"
CLASS_D_MULTICAST="224.0.0.0/4"
CLASS_E_RESERVED_NET="240.0.0.0/5"
PRIV_PORTS="0:1023"
UPRIV_PORTS="1024:65535"

# Look in /etc/services for ldm port
if egrep -q ^unidata-ldm /etc/services; then
    ldmport=unidata-ldm
elif egrep -q ^ldmd /etc/services; then
    ldmport=ldmd
else
    ldmport=388
fi

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
iptables -t mangle -F

# default policy
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

# allow anything on loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# allow anything on trusted interfaces
for iif in ${INT_IFS[*]} ${SAFE_EXT_IFS[*]}; do
    iptables -A INPUT -i $iif -j ACCEPT
    iptables -A OUTPUT -o $iif -j ACCEPT
done

# If two or more trusted internal interfaces, forward between first two
if [ $forward -eq 1 -a ${#INT_IFS[*]} -ge 2 ]; then
    iptables -A FORWARD -i ${INT_IFS[0]} -o ${INT_IFS[1]} -j ACCEPT
    iptables -A FORWARD -i ${INT_IFS[1]} -o ${INT_IFS[0]} -j ACCEPT
    for iif in ${SAFE_EXT_IFS[*]}; do
        iptables -A FORWARD -i ${INT_IFS[0]} -o $iif -j ACCEPT
        iptables -A FORWARD -i $iif -o ${INT_IFS[0]} -j ACCEPT
        iptables -A FORWARD -i ${INT_IFS[1]} -o $iif -j ACCEPT
        iptables -A FORWARD -i $iif -o ${INT_IFS[1]} -j ACCEPT
    done
fi

## SYN-FLOODING PROTECTION
# This rule limits the rate of incoming connections. In order to do
# this we divert tcp packets with the SYN bit set off to a user-defined
# chain. Up to limit-burst connections can arrive in 1/limit seconds,
# in this case 4 connections in one second. After this, one
# of the burst is regained every second and connections are allowed again.
# The default limit is 3/hour. The default limit burst is 5.
#
# taken from http://www.cs.princeton.edu/~jns/security/iptables

iptables -N syn-flood
for eif in ${UNSAFE_EXT_IFS[*]}; do
    iptables -A INPUT -i $eif -p tcp --syn -j syn-flood
done

iptables -A syn-flood -m limit --limit 1/s --limit-burst 4 -j RETURN
iptables -A syn-flood -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES SYN-FLOOD: "
iptables -A syn-flood -j DROP

# make sure NEW tcp connections are SYN packets. Otherwise log, then DROP
iptables -N syn-log
for eif in ${UNSAFE_EXT_IFS[*]}; do
    iptables -A INPUT -i $eif -p tcp \! --syn -m state --state NEW -j syn-log
done
iptables -A syn-log -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES SYN: "
iptables -A syn-log -j DROP

iptables -N spoof-log
for eif in ${UNSAFE_EXT_IFS[*]}; do
    ## SPOOFING
    # Most of this anti-spoofing stuff is theoretically not really
    # necessary with the flags we have set in the kernel, but you
    # never know there isn't a bug somewhere in your IP stack.
    #
    # Refuse spoofed packets pretending to be from your IP address.
    # iptables -A INPUT  -i $eif -s $IPADDR -j DROP
    # Refuse packets claiming to be from a Class A private network.
    iptables -A INPUT  -i $eif -s $CLASS_A -j spoof-log
    # Refuse packets claiming to be from a Class B private network.
    iptables -A INPUT  -i $eif -s $CLASS_B -j spoof-log
    # Refuse packets claiming to be from a Class C private network.
    iptables -A INPUT  -i $eif -s $CLASS_C -j spoof-log
    # Refuse Class D multicast addresses. Multicast is illegal as a
    # source address.
    iptables -A INPUT -i $eif -s $CLASS_D_MULTICAST -j spoof-log
    # Refuse Class E reserved IP addresses.
    iptables -A INPUT -i $eif -s $CLASS_E_RESERVED_NET -j spoof-log
    #
    # Refuse packets claiming to be to the loopback interface.
    # Refusing packets claiming to be to the loopback interface protects
    # against source quench, whereby a machine can be told to slow itself
    # down by an icmp source quench to the loopback.
    iptables -A INPUT  -i $eif -d $LOOPBACK -j spoof-log
    # Refuse broadcast address packets.
    # iptables -A INPUT -i $eif -d $BROADCAST -j DROP
done
iptables -A spoof-log -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES SPOOF: "
iptables -A spoof-log -j DROP

filter_icmp()
{
    ## ===================================================================
    ## ICMP
    # We prefilter icmp by pulling it off to user-dfined chains so that we
    # can restrict which types are allowed from the beginning rather than
    # leaving it to the connection tracking.  For instance, we don't want
    # redirects whatever happens.  In case you hadn't realised, ICMP scares me.
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


    iptables -A INPUT  -i $eif -p icmp -j icmp-in
    iptables -A OUTPUT -o $eif -p icmp -j icmp-out

    # Accept 0,3,4,11,12,14,16,18 in.
    iptables -A icmp-in -i $eif -p icmp --icmp-type 0  -s $ANYHOST -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 3  -s $ANYHOST -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 4  -s $ANYHOST -j RETURN

    # specify ACCEPT here. If RETURN, then it will be rejected later
    # because we don't have NEW in --state when returning from icmp-in
    # chain to INPUT chain.
    for host in ${EXT_PING_HOST[*]}; do
	iptables -A icmp-in -i $eif -p icmp --icmp-type echo-request \
		-s $host -m limit --limit 6/minute -j ACCEPT
    done
    iptables -A icmp-in -i $eif -p icmp --icmp-type 11 -s $ANYHOST -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 12 -s $ANYHOST -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 14 -s $ANYHOST -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 16 -s $ANYHOST -j RETURN
    iptables -A icmp-in -i $eif -p icmp --icmp-type 18 -s $ANYHOST -j RETURN
    # Allow 4,8,12,13,15,17 out.
    iptables -A icmp-out -o $eif -p icmp --icmp-type echo-reply -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 4 -d $ANYHOST -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 8 -d $ANYHOST -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 12 -d $ANYHOST -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 13 -d $ANYHOST -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 15 -d $ANYHOST -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 17 -d $ANYHOST -j RETURN


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
}
# ============================================================================

iptables -N icmp-in
iptables -N icmp-out

for eif in ${UNSAFE_EXT_IFS[*]}; do
    filter_icmp $eif
done

filter_tcp()
{
    local eif=$1        # interface
    local cheap=$2      # true or false

    # tcp and udp established connections
    iptables -A INPUT -i $eif -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A OUTPUT -o $eif -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A INPUT -i $eif -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A OUTPUT -o $eif -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -i $eif -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT
	iptables -A FORWARD -o $eif -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT
	iptables -A FORWARD -i $eif -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
	iptables -A FORWARD -o $eif -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
    fi

    # port 20=ftp-data, 21=ftp
    # Accepting the RELATED connections above then allows both passive
    # and active ftp.

    # good reference:
    #	http://www.sns.ias.edu/~jns/security/iptables/iptables_conntrack.html
    # starting ftp connection
    iptables -A OUTPUT -o $eif -p tcp --dport 21 -m state --state NEW -j ACCEPT 
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport 21 -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport 21 -m state --state NEW -j ACCEPT
    fi

    # outgoing ssh to sshd on remote systems (ssh originations from here)
    for host in ${SSH_OUTGOING[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport ssh -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport ssh -m state --state NEW -j ACCEPT
	fi
    done

    # incoming ssh connections
    for host in ${SSH_INCOMING[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport ssh -m state --state NEW -j ACCEPT
	# don't do forwarding of incoming SSH. See below for an example
	# of port forwarding to allow ssh to an internal host
    done

    for host in ${POSTGRES_IN[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport postgres -m state --state NEW -j ACCEPT
	iptables -A INPUT -i $eif -s $host -p udp --dport postgres -m state --state NEW -j ACCEPT
    done
  
    for host in ${LDM_IN_OUT[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport $ldmport -m state --state NEW -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport $ldmport -m state --state NEW -j ACCEPT
    done
  
    # outgoing imap
    iptables -A OUTPUT -o $eif -p tcp --dport imap -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport imap -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport imap -m state --state NEW -j ACCEPT
    fi

    # outgoing imap3
    iptables -A OUTPUT -o $eif -p tcp --dport imap3 -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport imap3 -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport imap3 -m state --state NEW -j ACCEPT
    fi

    # outgoing imap-ssl
    iptables -A OUTPUT -o $eif -p tcp --dport imaps -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport imaps -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport imaps -m state --state NEW -j ACCEPT
    fi

    # outgoing pop
    iptables -A OUTPUT -o $eif -p tcp --dport pop2 -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport pop2 -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport pop2 -m state --state NEW -j ACCEPT
    fi

    # outgoing pop3
    iptables -A OUTPUT -o $eif -p tcp --dport pop3 -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport pop3 -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport pop3 -m state --state NEW -j ACCEPT
    fi

    # outgoing pop3s
    iptables -A OUTPUT -o $eif -p tcp --dport pop3s -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport pop3s -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport pop3s -m state --state NEW -j ACCEPT
    fi

    # outgoing dns (udp)
    iptables -A OUTPUT -o $eif -p udp --dport domain -m state --state NEW -j ACCEPT

    # forwarding dns (not necessary since we're a caching nameserver)
    # if [ $forward -eq 1 ]; then
	# iptables -A FORWARD -o $eif -p udp --dport domain -m state --state NEW -j ACCEPT
    # fi

    # Log, then block GoogleEarth on expensive links. This will block
    # squid too.
    if ! $cheap; then
      for host in ${GOOGLE_EARTH[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport http -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES OUT GoogleEarth: "
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport http -j DROP
      done
    fi

    # squid's outgoing http requests to remote servers
    iptables -A OUTPUT -o $eif -p tcp --dport http -m state --state NEW -j ACCEPT
    iptables -A OUTPUT -o $eif -p tcp --dport https -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	for host in ${HTTP_REQUESTERS[*]}; do
            # Added by truss 20070511 for transparent squid proxy
            iptables -t nat -A PREROUTING -s $host -p tcp --dport 80 -j REDIRECT --to-port 3128
	    iptables -A FORWARD -o $eif -s $host -p tcp --dport https -m state --state NEW -j ACCEPT
	done
    fi

    for host in ${HTTP_CLNTS[*]}; do
	# incoming http requests to our server
	iptables -A INPUT -i $eif -s $host -p tcp --dport http -m state --state NEW -j ACCEPT

	# incoming https
	iptables -A INPUT -i $eif -s $host -p tcp --dport https -m state --state NEW -j ACCEPT
    done

    # outgoing ntp (udp) is OK on cheap/fast interfaces.
    # Satcom is so slow that no-one should be doing ntp over it.
    if $cheap; then
        iptables -A OUTPUT -o $eif -p udp --dport ntp -m state --state NEW -j ACCEPT
    fi

    # disable forwarding of ntp
    # if [ $forward -eq 1 ]; then
	# iptables -A FORWARD -o $eif -p udp --dport ntp -m state --state NEW -j ACCEPT
    # fi

    # outgoing smtp
    iptables -A OUTPUT -o $eif -p tcp --dport smtp -m state --state NEW -j ACCEPT
    if [ $forward -eq 1 ]; then
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -p tcp --dport smtp -m state --state NEW -j ACCEPT
	iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -p tcp --dport smtp -m state --state NEW -j ACCEPT
    fi

    # incoming smtp
    for host in ${SMTP_IN[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport smtp -m state --state NEW -j ACCEPT
    done

    # irc
    for host in ${IRC_SERVERS[*]}; do
	# iptables -A OUTPUT -o $eif -d $host -p tcp --dport irc -m state --state NEW -j ACCEPT
	# iptables -A OUTPUT -o $eif -d $host -p udp --dport irc -m state --state NEW -j ACCEPT
	# iptables -A OUTPUT -o $eif -d $host -p tcp --dport 6668 -m state --state NEW -j ACCEPT
	# iptables -A OUTPUT -o $eif -d $host -p udp --dport 6668 -m state --state NEW -j ACCEPT
        iptables -A OUTPUT -o $eif -d $host -p tcp --dport 4400 -m state --state NEW -j ACCEPT
        iptables -A OUTPUT -o $eif -d $host -p udp --dport 4400 -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    # iptables -A FORWARD -o $eif -d $host -p tcp --dport irc -m state --state NEW -j ACCEPT
	    # iptables -A FORWARD -o $eif -d $host -p udp --dport irc -m state --state NEW -j ACCEPT
	    # iptables -A FORWARD -o $eif -d $host -p tcp --dport 6668 -m state --state NEW -j ACCEPT
	    # iptables -A FORWARD -o $eif -d $host -p udp --dport 6668 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport 4400 -m state --state NEW -j ACCEPT
            iptables -A FORWARD -o $eif -d $host -p udp --dport 4400 -m state --state NEW -j ACCEPT
        fi
    done
    # incoming rpc
    for host in ${RPC_CLIENTS[*]}; do
	iptables -A INPUT -i $eif -s $host -p tcp --dport sunrpc -j ACCEPT
    done

    # outgoing rpc
    for host in ${RPC_SERVERS[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport sunrpc -j ACCEPT
    done

    # VPN
    # from Cisco VPN Client user guide:
    # If you are running a Linux firewall (for example, ipchains or iptables),
    # be sure that the following types of traffic are allowed to pass through:
    # ¢UDP port 50
    # ¢UDP port 10000 (or any other port number being used for IPSec/UDP)
    # ¢IP protocol 50 (ESP
    # ¢TCP port configured for IPSec/TCP
    # ¢NAT-T port 4500 
    #
    # Protocol 50 is listed as IPv6-Crypt in linux /etc/protocols, but
    #	iana.org says 50 is ESP.
    # VPN also seems to need port 29747 for some reason.
    #
    for host in ${VPN_SVRS[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p udp --dport isakmp -m state --state NEW -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p udp --dport 4500 -m state --state NEW -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p udp --dport 10000 -m state --state NEW -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p udp --dport 29747 -m state --state NEW -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p 50 -j ACCEPT
	iptables -A INPUT -i $eif -d $host -p 50 -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p udp --dport isakmp -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p udp --dport isakmp -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p udp --dport 4500 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p udp --dport 4500 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p udp --dport 10000 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p udp --dport 10000 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p udp --dport 29747 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p udp --dport 29747 -m state --state NEW -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p 50 -j ACCEPT
	    iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p 50 -j ACCEPT
	    iptables -A FORWARD -i $eif -s $PRIV_HOSTS_DISP -d $host -p 50 -j ACCEPT
	    iptables -A FORWARD -i $eif -s $PRIV_HOSTS_DATA -d $host -p 50 -j ACCEPT
	fi
    done

    ## TRACEROUTE
    # Outgoing traceroute anywhere.
    # The reply to a traceroute is an icmp time-exceeded which is
    # allowed by icmp-in
    iptables -A OUTPUT -o $eif -p udp --dport $TR_DEST_PORTS \
	-m state --state NEW -j ACCEPT 
    # Accept incoming traceroutes from anywhere.
    iptables -A INPUT -i $eif -p udp --dport $TR_DEST_PORTS \
	-m state --state NEW -j ACCEPT 

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
    iptables -A INPUT  -i $eif -p udp -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES UDP-IN: "
    iptables -A INPUT  -i $eif -p udp -j DROP
    iptables -A OUTPUT -o $eif -p udp -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES UDP-OUT: "
    iptables -A OUTPUT -o $eif -p udp -j DROP
    # Any icmp not already allowed is logged and then dropped.
    iptables -A INPUT  -i $eif -p icmp -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES ICMP-IN: "
    iptables -A INPUT  -i $eif -p icmp -j DROP
    iptables -A OUTPUT -o $eif -p icmp -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES ICMP-OUT: "
    iptables -A OUTPUT -o $eif -p icmp -j DROP
    # Any tcp not already allowed is logged and then dropped.
    iptables -A INPUT  -i $eif -p tcp -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES TCP-IN: "
    iptables -A INPUT  -i $eif -p tcp -j DROP
    iptables -A OUTPUT -o $eif -p tcp -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES TCP-OUT: "
    iptables -A OUTPUT -o $eif -p tcp -j DROP
    # Anything else not already allowed is logged and then dropped.
    # It will be dropped by the default policy anyway, but let's be paranoid.
    iptables -A INPUT  -i $eif -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES PROTOCOL-X-IN: "
    iptables -A INPUT  -i $eif -j DROP
    iptables -A OUTPUT -o $eif -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES PROTOCOL-X-OUT: "
    iptables -A OUTPUT -o $eif -j DROP

    # MASQUERADE is a form of SNAT (source NAT)
    if [ $forward -eq 1 ]; then
	iptables -t nat -A POSTROUTING -o $eif -j MASQUERADE
    fi
    # port forwarding is a form of DNAT (destination NAT)
    # Example of port forwarding to allow ssh to an internal host
    # iptables -t nat -A PREROUTING -p tcp --dport 50022 -i $eif -j DNAT \
    # 	--to 192.168.84.99:22
}

for eif in ${CHEAP_EXT_IFS[*]}; do
    filter_tcp $eif true
done

for iif in ${SAFE_EXT_IFS[*]}; do
    # MASQUERADE is a form of SNAT (source NAT)
    if [ $forward -eq 1 ]; then
	iptables -t nat -A POSTROUTING -o $iif -j MASQUERADE
    fi
done

for eif in ${SATCOM_EXT_IFS[*]}; do
    filter_tcp $eif false
done

# Over ppp1 (MPDS), clamp MSS. We'll see if we can log it
iptables -t mangle -A FORWARD -o ppp1 -p tcp --tcp-flags SYN,RST SYN \
    -m limit --limit 1/minute --limit-burst 5 -j LOG --log-prefix "IPTABLES CLAMP-MSS: "
iptables -t mangle -A FORWARD -o ppp1 -p tcp --tcp-flags SYN,RST SYN \
    -j TCPMSS --clamp-mss-to-pmtu

# accept fragments on any interface
iptables -A OUTPUT -f -j ACCEPT
iptables -A INPUT -f -j ACCEPT
if [ $forward -eq 1 ]; then
    iptables -A FORWARD -f -j ACCEPT
fi

# THE END
echo "# Generated by $0 from raf-ac-firewall package on `date`"
iptables-save


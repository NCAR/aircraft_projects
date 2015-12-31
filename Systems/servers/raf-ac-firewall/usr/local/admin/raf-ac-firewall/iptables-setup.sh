#!/bin/bash

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

# Uncomment these lines for debugging, and set AIRCRAFT with env:
# set -x
# alias iptables=true
# alias iptables-save=true

# quit immediately on error, otherwise error messages tend to be missed
set -e
# but return firewall to open state on error (in case one is testing from off site)
trap "{ /etc/init.d/iptables stop; }" ERR

# load iptables modules listed in /etc/sysconfig/iptables-config.
# This as stolen from /etc/init.d/iptables
IPTABLES=iptables
IPTABLES_MODULES=""
IPTABLES_CONFIG=/etc/sysconfig/${IPTABLES}-config
# Load firewall configuration.
[ -r "$IPTABLES_CONFIG" ] && . "$IPTABLES_CONFIG"
# Load additional modules (helpers)
if [ -n "$IPTABLES_MODULES" ]; then
    for mod in $IPTABLES_MODULES; do
        modprobe $mod > /dev/null 2>&1
    done
fi

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

# Safe external interfaces which do not need firewalling
# or traffic limits.  VPN is an example. If VPN is brought
# up over satcom, we'll assume the user knows to limit usage.
# This can also be the interfaces which are connected to the ucar guest
# network (eth2). One could instead put eth2 on CHEAP_UNSAFE_EXT_IFS
# and then it will get the filters that are applied to SATCOM_EXT_IFS.
SAFE_EXT_IFS=(cipsec+ tun+ eth2)

# Unsafe, cheap (per byte) external interfaces. These are not
# firewalled for us. We want to do firewalling, but don't need
# to limit traffic.
CHEAP_UNSAFE_EXT_IFS=()

# Slow and expensive external interfaces.
# Add eth3 if one activates Inmarsat ISDN.
#
# The GV still uses pppoe to the ISDN modem, so ppp+ is the satcom
# interface.  The C130 routes Internet traffic through a pppoe router on
# eth3, so eth3 is the actual satcom interface.
#
# IP masquerading should be enabled on all the external interfaces,
# including the ppp+ SATCOM interfaces, except eth3 does not need it when a
# PPPoE router is doing it.  There's no harm enabling masquerading on ppp+
# even when ppp will not be used, so it's always included by default.
#
# The only difference in this script between the planes is the choice of
# SATCOM_EXT_IFS.  It's possible even that difference could be eliminated
# by applying all the same rules to both eth3 and ppp+, since the firewall
# does not specify the actual default route, only the filtering between
# interfaces.  However, since that has not been tested, for now we stick
# with the distinction that's currently in use.
#
# The determination of the plane comes from the ads user's environment
# settings.  This is not exactly secure, so someday the setting should be
# queried in some safer way.

[ -r /home/ads/ads3_environment.sh ] && . /home/ads/ads3_environment.sh
SATCOM_EXT_IFS=(ppp+)
case "$AIRCRAFT" in
    GV_N677F)
	SATCOM_EXT_IFS=(ppp+)
	;;
    C130_N130AR)
	SATCOM_EXT_IFS=(eth3)
	;;
    *)
	echo "# *** AIRCRAFT setting not recognized: $AIRCRAFT ***"
	exit 1
	;;
esac
MASQUERADE_IFS=(${SAFE_EXT_FS[*]} ppp+)

UNSAFE_EXT_IFS=(${CHEAP_UNSAFE_EXT_IFS[*]} ${SATCOM_EXT_IFS[*]})

# All external (WAN) interfaces
EXT_IFS=(${CHEAP_UNSAFE_EXT_IFS[*]} ${SATCOM_EXT_IFS[*]} ${SAFE_EXT_IFS[*]})

# Internal trusted interfaces. Forwarding is done between first two
INT_IFS=(eth0 eth1)

UCAR_128=128.117.0.0/16

# Currently all hosts can do SSH and IRC off the plane.
#
# Privileged hosts can do more: HTTP, IMAP, etc.
# 192.168.84.0/24 = 192.168.84.0-255
# 192.168.84.0/25 = 192.168.84.0-127
# 192.168.84.0/26 = 192.168.84.0-63
# 192.168.84.0/27 = 192.168.84.0-31
PRIV_HOSTS_DISP=192.168.84.0/26
PRIV_HOSTS_DATA=192.168.184.0/26

# Add udp ports to forward from external interfaces
# (both UNSAFE_EXT_IFS and SAFE_EXT_IFS) to machines on
# the internal interfaces (INT_IFS)
# UDP ports are often blocked by firewalls. According to David Mitchell,
# the UCAR firewall allows outbound UDP to ports 33434-33524, since those are
# typically used by traceroute. One should then forward those to ports
# under 32768, so they're not in the dynamic range.
UDP_PORT_FORWARDS=(\
    # from    port  tohost        toport
    $ANYHOST 33500 192.168.84.151 31100 # John Ortega's system \
    $ANYHOST 33501 127.0.0.1      31101 #  acserver \
    $UCAR_128 33502 192.168.84.11  31102 # testing to adslap1 \
    $UCAR_128 5500 192.168.184.178  5500 # VNC from ground to toga-pc\
    $UCAR_128 5800 192.168.184.178  5800 # VNC from ground to toga-pc\
    $UCAR_128 5801 192.168.184.178  5801 # VNC from ground to toga-pc\
    $UCAR_128 5802 192.168.184.178  5802 # VNC from ground to toga-pc\
    $UCAR_128 5803 192.168.184.178  5803 # VNC from ground to toga-pc\
    $UCAR_128 5900 192.168.184.178  5900 # VNC from ground to toga-pc\
    $UCAR_128 5901 192.168.184.178  5901 # VNC from ground to toga-pc\
    $UCAR_128 5902 192.168.184.178  5902 # VNC from ground to toga-pc\
    $UCAR_128 5903 192.168.184.178  5903 # VNC from ground to toga-pc\
)

# external hosts that we can ssh to
SSH_OUTGOING=($ANYHOST)

# external hosts that can ssh into our systems
# may want to limit this to known systems
# like 128.117.0.0/16 to avoid password guessers.
SSH_INCOMING=($UCAR_128)

# Google Earth SATCOM block.
# April 2008:
#   www.earth.google.com is an alias for www.google.com
#   www.google.com is an alias for www.l.google.com
#   www.l.google.com is
#           74.125.47.{99,103,104,147} (5/1/2008 from GV on MPDS)
#           64.233.167.{99,104,147}    (5/1/2008 from EOL)
#   google.com is 64.233.167.99, 64.233.187.99, 72.14.207.99
#   maps.google.com is 64.233.167.{99,103,104,147}
#   google earth appears to use kh.google.com which is 64.233.167.91
#   72.14.203.91 is ro-in-f91.google.com (not sure what that provides)
# GOOGLE_EARTH=(72.14.203.0/24 64.233.167.0/24 74.125.47.0/24)
# Oct 2008:
#   www.google.com is 209.85.173.{104,147,99,103}
#   maps.google.com is the same
#   kh.google.com is 209.85.173.{190,91,93,136)
# GOOGLE_EARTH=(209.85.173.0/24)
#
# This script is only run on RPM install, not on boot
# or when an interface becomes active. The addresses
# for earth.google.com change quite frequently, and are
# likely different depending on what nameserver we're
# forwarding to.  So this attempt to block google earth
# traffic is not working. We're not even sure what server names
# are used by GE. (We'd have to try tcpdump or strace?)
# So, this list of GOOGLE_EARTH IPs is empty.
GOOGLE_EARTH=()

# EOL vpn servers
VPN_SVRS=(192.43.244.230)

# external hosts that can establish incoming postgres connections
POSTGRES_IN=($UCAR_128)

# LDM
LDM_IN_OUT=($UCAR_128)

# Who is allowed to send us smtp packets
SMTP_IN=()

# who is allowed to ping me
EXT_PING_HOST=($UCAR_128)

# who is allowed to make requests of our http server
# HTTP_CLNTS=($UCAR_128)
HTTP_CLNTS=()

# Remote Instrument Control Host.
RIC_HOST=(128.117.188.122)

# who can make requests of outside servers
HTTP_REQUESTERS=($PRIV_HOSTS_DATA $PRIV_HOSTS_DISP)

# which IRC servers can we connect to
IRC_SERVERS=($ANYHOST)

# RPC (ldm also uses RPC)
RPC_CLIENTS=($UCAR_128)
RPC_SERVERS=($UCAR_128)

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
ROUTER_NET="192.168.99.0/24"

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

# allow anything on docker0, for Docker, Field-Catalog apps
iptables -A INPUT -i docker0 -j ACCEPT
iptables -A OUTPUT -o docker0 -j ACCEPT

# allow anything on trusted interfaces
for iif in ${INT_IFS[*]} ${SAFE_EXT_IFS[*]}; do
    iptables -A INPUT -i $iif -j ACCEPT
    iptables -A OUTPUT -o $iif -j ACCEPT
done

# Allow anything between the server and the router network.  I think
# this still prevents other internal hosts from reaching the router (ie,
# the web admin interface), but that should be tested, assuming that's
# desirable.
iptables -A INPUT -s $ROUTER_NET -j ACCEPT
iptables -A OUTPUT -d $ROUTER_NET -j ACCEPT

# If two or more trusted internal interfaces, forward between first two
if [ $forward -eq 1 -a ${#INT_IFS[*]} -ge 2 ]; then
    iptables -A FORWARD -i ${INT_IFS[0]} -o ${INT_IFS[1]} -j ACCEPT
    iptables -A FORWARD -i ${INT_IFS[1]} -o ${INT_IFS[0]} -j ACCEPT
    # forward to internal interfaces from safe external
    for eif in ${SAFE_EXT_IFS[*]}; do
        for iif in ${INT_IFS[*]}; do
            iptables -A FORWARD -i $iif -o $eif -j ACCEPT
            iptables -A FORWARD -i $eif -o $iif -j ACCEPT
        done
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

# IGMP packets are used to manage multicast groups.
filter_igmp()
{
    # Server at other end of iridium ppp connections (Level3)
    # sends out igmp packets right after connection. Reject them, so
    # it knows we don't want to do any multicast over this link.
    iptables -A INPUT -i $1 -d $CLASS_D_MULTICAST -p igmp -j REJECT
}

filter_icmp() #<eif>
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

    local eif=$1        # interface
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
    # Allow 3,4,8,12,13,15,17 out.
    iptables -A icmp-out -o $eif -p icmp --icmp-type echo-reply -j RETURN
    iptables -A icmp-out -o $eif -p icmp --icmp-type 3 -d $ANYHOST -j RETURN
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

filter_igmp ppp+
filter_igmp eth3

for eif in ${UNSAFE_EXT_IFS[*]}; do
    filter_icmp $eif
done

filter_ip()
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
	# Same for outbound to sshd on port 23, although may want to limit this to eol-rt-data.
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport 23 -m state --state NEW -j ACCEPT
	if [ $forward -eq 1 ]; then
	    iptables -A FORWARD -o $eif -d $host -p tcp --dport 23 -m state --state NEW -j ACCEPT
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

    # Outgoing postgres
    iptables -A OUTPUT -o $eif -d $UCAR_128 -p tcp --dport postgres -j ACCEPT

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
	iptables -A OUTPUT -o $eif -d $host -p tcp --dport http -j REJECT
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

    if $cheap; then
        for host in ${HTTP_CLNTS[*]}; do
            # incoming http requests to our server
            iptables -A INPUT -i $eif -s $host -p tcp --dport http -m state --state NEW -j ACCEPT

            # incoming https
            iptables -A INPUT -i $eif -s $host -p tcp --dport https -m state --state NEW -j ACCEPT
        done
    fi

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
    #   allow protocol 50 (ESP), UDP ports 10000 and isakmp(500)
    #   port 4500 is IPsec NAT-Traversal
    for host in ${VPN_SVRS[*]}; do
	iptables -A OUTPUT -o $eif -d $host -p esp -j ACCEPT
	iptables -A OUTPUT -o $eif -d $host -p udp -m multiport --dports isakmp,ipsec-nat-t,10000 -j ACCEPT

	iptables -A INPUT -i $eif -s $host -p esp -j ACCEPT
	iptables -A INPUT -i $eif -s $host -p udp -m multiport --sports isakmp,ipsec-nat-t,10000 -j ACCEPT

	if [ $forward -eq 1 ]; then
            iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p esp -j ACCEPT
            iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DISP -d $host -p udp -m multiport --dports isakmp,ipsec-nat-t,10000 -j ACCEPT
            iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p esp -j ACCEPT
            iptables -A FORWARD -o $eif -s $PRIV_HOSTS_DATA -d $host -p udp -m multiport --dports isakmp,ipsec-nat-t,10000 -j ACCEPT

            iptables -A FORWARD -i $eif -d $PRIV_HOSTS_DISP -s $host -p esp -j ACCEPT
            iptables -A FORWARD -i $eif -d $PRIV_HOSTS_DISP -s $host -p udp -m multiport --sports isakmp,ipsec-nat-t,10000 -j ACCEPT
            iptables -A FORWARD -i $eif -d $PRIV_HOSTS_DATA -s $host -p esp -j ACCEPT
            iptables -A FORWARD -i $eif -d $PRIV_HOSTS_DATA -s $host -p udp -m multiport --sports isakmp,ipsec-nat-t,10000 -j ACCEPT
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

    # Allow UDP data feed to UCAR
    iptables -A OUTPUT -o $eif -p udp --dport 31007 -d $UCAR_128 -j ACCEPT
    iptables -A OUTPUT -o $eif -p udp --dport 30009 -d $UCAR_128 -j ACCEPT
    iptables -A INPUT -i $eif -p udp --dport 30009 -d $UCAR_128 -j ACCEPT
    iptables -A OUTPUT -o $eif -p udp --dport 30010 -d $UCAR_128 -j ACCEPT
    iptables -A INPUT -i $eif -p udp --dport 30010 -d $UCAR_128 -j ACCEPT

    #  3200{1-2} and {4-5} are for Remote Instrument Control (RIC)
    iptables -A OUTPUT -o $eif -p udp --dport 32001 -d $UCAR_128 -j ACCEPT # plane to ground
    iptables -A INPUT -i $eif -p udp --dport 32001 -s $UCAR_128 -j ACCEPT # ground to plane
    iptables -A OUTPUT -o $eif -p udp --dport 32002 -d $UCAR_128 -j ACCEPT # plane to ground
    iptables -A INPUT -i $eif -p udp --dport 32002 -s $UCAR_128 -j ACCEPT # ground to plane
    iptables -A OUTPUT -o $eif -p udp --dport 32004 -d $UCAR_128 -j ACCEPT # plane to ground
    iptables -A INPUT -i $eif -p udp --dport 32004 -s $UCAR_128 -j ACCEPT # ground to plane
    iptables -A OUTPUT -o $eif -p udp --dport 32005 -d $UCAR_128 -j ACCEPT # plane to ground
    iptables -A INPUT -i $eif -p udp --dport 32005 -s $UCAR_128 -j ACCEPT # ground to plane


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

    # port forwarding is a form of DNAT (destination NAT)
    # Example of port forwarding to allow ssh to an internal host
    # iptables -t nat -A PREROUTING -p tcp --dport 50022 -i $eif -j DNAT \
    # 	--to 192.168.84.99:22
}

# port forwarding of all udp packets coming in on external interfaces
# cheap and expensive, unsafe and safe.
for (( i = 0; i < ${#UDP_PORT_FORWARDS[*]}; )); do
    # mystery: incrementing with "let i++" results in an error exit
    from=${UDP_PORT_FORWARDS[$i]}
    i=$(( $i+1 ))
    port=${UDP_PORT_FORWARDS[$i]}
    i=$(( $i+1 ))
    ip=${UDP_PORT_FORWARDS[$i]}
    i=$(( $i+1 ))
    toport=${UDP_PORT_FORWARDS[$i]}
    i=$(( $i+1 ))
    for eif in ${EXT_IFS[*]}; do
        # if dest is localhost, use REDIRECT target, otherwise DNAT
	if [ $ip == 127.0.0.1 ]; then
	    iptables -t nat -A PREROUTING -i $eif -p udp -s $from --dport $port -j REDIRECT --to-ports $toport
	    iptables -A INPUT -i $eif -p udp -s $from --dport $toport -j ACCEPT
	    # iptables -A INPUT -i $eif -p udp --dport $toport -j ACCEPT
        else
	    iptables -t nat -A PREROUTING -i $eif -p udp -s $from --dport $port -j DNAT --to $ip:$toport
            # then must open the forward filter to internal interfaces
            for iif in ${INT_IFS[*]}; do
                    iptables -A FORWARD -i $eif -o $iif -p udp --dport $toport -j ACCEPT
            done
        fi
    done
done

# setup rules for cheap, i.e. non-satcom, but unsafe interfaces
for eif in ${CHEAP_UNSAFE_EXT_IFS[*]}; do
    filter_ip $eif true
done

# setup rules for expensive satcom exposed interfaces
for eif in ${SATCOM_EXT_IFS[*]}; do
    filter_ip $eif false
done

for eif in ${MASQUERADE_IFS[*]}; do
    # MASQUERADE is a form of SNAT (source NAT)
    if [ $forward -eq 1 ]; then
	iptables -t nat -A POSTROUTING -o $eif -j MASQUERADE
    fi
done

# Over the satcom external interfaces, clamp MSS.
for eif in ${SATCOM_EXT_IFS[*]}; do
    iptables -t mangle -A FORWARD -o $eif -p tcp --tcp-flags SYN,RST SYN \
        -j TCPMSS --clamp-mss-to-pmtu
done

# accept fragments on any interface
iptables -A OUTPUT -f -j ACCEPT
iptables -A INPUT -f -j ACCEPT
if [ $forward -eq 1 ]; then
    iptables -A FORWARD -f -j ACCEPT
fi

info() {
    echo "# Generated by $0 from raf-ac-firewall package on `date`"
    echo "# Note running this script changes the firewall temporarily, until the next boot."
    echo "# To make the changes permanent, redirect the output to /etc/sysconfig/iptables"
    echo "# by doing: $0 > /etc/sysconfig/iptables"
}

# Put the info messages at the beginning and end of output
info
iptables-save
info

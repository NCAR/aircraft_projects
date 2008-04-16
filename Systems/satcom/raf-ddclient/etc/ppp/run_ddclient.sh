#!/bin/sh

# Run ddclient until success.

# To test this script, uncomment "set -x" and run it by hand like so:
# ./run_ddclient.sh ppp0 eth3 0 12.42.105.41 12.42.104.9 iridium
#
# set -x

if [ $# -lt 4 ]; then
    echo "$0 if baud local_IP remote_IP if"
    echo "example: $0 ppp0 /dev/ttyS0 38400 12.42.105.41 12.42.104.9 iridium"
    logger -t ddclient "$0 : no arguments"
    exit 1
fi

PATH=/usr/sbin:/sbin:$PATH

SYSNAME=gv
DDFILE=/etc/ddclient/${SYSNAME}.conf
DDHOST=raf${SYSNAME}.dyndns.org

logger -t ddclient $0 $*

if ! which ddclient > /dev/null; then
        logger -t ddclient "Cannot find ddclient. Install it in /usr/sbin or /sbin"
        exit 1
fi

# clean up any running run_ddclient.sh scripts
script=`basename $0`
ddpids=(`pgrep $script`)
if [ ${#ddpids[*]} -gt 1 ]; then
    pkill -x -o $script
fi

# and ddclient processes
pkill -x ddclient

## update the dyndys server unless the IP address is a private address
## that may be used as an internal LAN address (or PPtP tunnel).
IP=$4

case "$IP" in
10.* | 172.1[6-9].* | 172.2[0-9].* | 172.3[0-1].* | 192.168.*)
        logger -t ddclient "$* : IP=$IP is a private address, cannot update"
        exit 1
        ;;
"")
        logger -t ddclient "$* : No local IP given so cannot update"
        exit 1
	;;
*)      
        ;;
esac

[ -d /var/cache/ddclient ] || mkdir /var/cache/ddclient

if [ -z "$DDFILE" ]; then
    logger -t ddclient "DDFILE variable not found"
    exit 1
fi

good_dns=false
for (( ncheck=0; ncheck < 5; ncheck++ )); do

    # use -R N option of host command to retry up to N requests
    if ip=(`host -R 3 $DDHOST`); then
        # 4th word of host output is IP address
        [ ${#ip[*]} -gt 3 -a "${ip[3]}" == "$IP" ] && good_dns=true
    fi

    if $good_dns; then
        if [ $ncheck -eq 0 ]; then
            logger -t ddclient "Lookup of $DDHOST returns $IP. Running ddclient not necessary"
        else
            logger -t ddclient "Lookup of $DDHOST returns $IP. ddclient successful"
        fi
        break
    fi

    # wait again if not first time through
    [ $ncheck -gt 0 ] && sleep 305

    for (( ntry=0; ntry < 10; ntry++ )); do

            # every other time try members.dyndns.org, otherwise a fixed IP.
            server=members.dyndns.org
            if [ $(($ntry % 2)) -eq 0 ]; then
                host -R 2 members.dyndns.org > /dev/null || server=63.208.196.96 
            else
                server=63.208.196.96 
            fi

            cmd="ddclient -daemon=0 -use=if -if=$1 -server $server -file $DDFILE"
            logger -t ddclient "$cmd"
            eval $cmd && break

            # ddclient complains if you try to update more than every
            # 5 minutes. However, I think it keeps track of that in the
            # local cache, rather than on the server, so if we were
            # devious we could delete the cache.
            sleep 305
    done
done


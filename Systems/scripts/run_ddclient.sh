#!/bin/sh

# Run ddclient until success.

# set -x

PATH=/usr/sbin:/sbin:$PATH

# clean up any old run_ddclient.sh scripts
script=`basename $0`
ddpids=(`pgrep $script`)
if [ ${#ddpids[*]} -gt 1 ]; then
    pkill -x -o $script
fi

# and ddclient processes
pkill -x ddclient

## update the dyndys server unless the IP address is a private address
## that may be used as an internal LAN address (or PPtP tunnel).
IP=
IP=${IP:-$PPP_LOCAL}
IP=${IP:-$IPLOCAL}
IP=${IP:-$4}

logger -t $0 $*
case "$IP" in
10.* | 172.1[6-9].* | 172.2[0-9].* | 172.3[0-1].* | 192.168.*)
        logger -t ddclient "$* : IP=$IP is a private address, cannot update"
        logger -t ppp "$* : IP=$IP is a private address, cannot update"
        exit 1
        ;;
"")
        logger -t ddclient "$* : No local IP given so cannot update"
	logger -t ppp "$* : No local IP given so cannot update"
        exit 1
	;;
*)      ;;
esac

[ -d /var/cache/ddclient ] || mkdir /var/cache/ddclient

if ! which ddclient > /dev/null; then
        logger -t ddclient "Cannot find ddclient. Install it in /usr/sbin or /sbin"
        logger -t ppp "Cannot find ddclient. Install it in /usr/sbin or /sbin"
        exit 1
fi

for (( ntry=10; ntry > 0; ntry-- )); do
        # every other time try members.dyndns.org, otherwise a fixed IP.
        server=members.dyndns.org
        if [ $(($ntry % 2)) -eq 0 ]; then
            host members.dyndns.org > /dev/null || server=63.208.196.96 
        else
            server=63.208.196.96 
        fi

        cmd="ddclient -daemon=0 -syslog -use=if -if=$1 -server $server"
        logger -t ddclient "$cmd"
        logger -t ppp "$cmd"
        eval $cmd && break

        # ddclient complains if you try to update more than every 5 minutes.
        # However, I think it keeps track of that in the local cache,
        # rather than on the server, so if we were devious we could
        # delete the cache.
        sleep 305
done


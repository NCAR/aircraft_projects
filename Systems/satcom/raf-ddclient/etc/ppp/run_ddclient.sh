#!/bin/sh

# Run ddclient until success.

# This script is run as follows from pppd:
# ./run_ddclient.sh ppp0 /dev/ttyS1 19200 12.42.105.41 12.42.104.9 iridium
# ./run_ddclient.sh ppp1 eth3 0 12.42.105.41 12.42.104.9 mpds
#
# These are the parameters that are passed by pppd to the ip-up scripts.
# This script does not use the parameters. The IP local address passed by pppd
# may not be the correct one to be used to contact us from the internet.
# With the Inmarsat BGAN on the C130, the local address of the point-to-point
# is a 192.168 address, and is not the one to be used to contact us from the
# internet. To find our internet address, we query checkip.dyndns.org with curl.
#
# So to test this script you don't need to pass any parameters.
#
# set -x

script=`basename $0`
if [ $# -lt 0 ]; then
    echo "$0 if device baud local_IP [ remote_IP [ ipparam ]]"
    echo "example: $0 ppp0 /dev/ttyS0 38400 12.42.105.41 12.42.104.9 iridium"
    echo "     or: $0 ppp1 eth3 0 12.42.105.41 12.42.104.9 mpds"
    echo "note: device, baud, remote_IP and ipparam are not currently used"
    logger -t ddclient "$0 : no arguments"
    exit 1
fi

PATH=/usr/sbin:/sbin:$PATH

# Which system is this for?
SYSNAME=c130
DDFILE=/etc/ddclient/${SYSNAME}.conf
DDHOST=raf${SYSNAME}.dyndns.org

logger -t ddclient $0 $*

if ! which ddclient > /dev/null; then
        logger -t ddclient "Cannot find ddclient. Install it in /usr/sbin or /sbin"
        exit 1
fi

# clean up any running run_ddclient.sh scripts (except ourselves)
ddpids=(`pgrep $script`)
for (( i=1; i < ${#ddpids[*]}; i++ )); do
    pkill -x -o $script
done

# and ddclient processes
pkill -x ddclient

[ -d /var/cache/ddclient ] || mkdir /var/cache/ddclient

if [ -z "$DDFILE" ]; then
    logger -t ddclient "DDFILE variable not found"
    exit 1
fi

good_dns=false
for (( ncheck=0; ncheck < 5; ncheck++ )); do

    if [ $(($ncheck % 2)) -eq 0 ]; then
        IP=`curl -s --connect-timeout 10 checkip.dyndns.org/ |cut -d ":" -f2|cut -d "<" -f1|sed 's/ //g'`
    else
    # every other time try hardcoded IP address for checkip.dyndns.org
        IP=`curl -s --connect-timeout 10 208.78.70.70/ |cut -d ":" -f2|cut -d "<" -f1|sed 's/ //g'`
    fi

    if [ "$IP" ]; then

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
    fi

    # wait again if not first time through
    [ $ncheck -gt 0 ] && sleep 305


    for (( ntry=0; ntry < 10; ntry++ )); do

            # every other time try members.dyndns.org, otherwise a fixed IP.
            server=members.dyndns.org
            checkip=checkip.dyndns.com/

            if [ $(($ntry % 2)) -eq 0 ]; then
                if ! host -R 2 members.dyndns.org > /dev/null; then
                    server=63.208.196.96 
                    checkip=208.78.70.70/
                fi
            else
                server=63.208.196.96 
                checkip=208.78.70.70/
            fi

            cmd="ddclient -daemon=0 -use=web -web=$checkip -server $server -file $DDFILE"
            logger -t ddclient "$cmd"
            eval $cmd && break

            # ddclient complains if you try to update more than every
            # 5 minutes. However, I think it keeps track of that in the
            # local cache, rather than on the server, so if we were
            # devious we could delete the cache.
            sleep 305
    done
done


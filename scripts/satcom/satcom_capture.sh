#!/bin/bash
###############################################################################
# Script to log traffic getting off the plane. Ignores traffic between
# onboard hosts.
#
#  - Needs to run as root.
#  - Started by systemd at boot, so that a capture covers the whole flight.
#    See INSTALL_LINUX.md for the unit and how to enable it. It is not meant to
#    be run interactively, and takes no arguments.
#  - Finds its own interface rather than having one hardcoded: the interface
#    this machine's off-plane traffic leaves by is the device carrying the
#    default route. Known values, for reference: eno8303np0 on acserver,
#    enp3s0 on MC brix01, enp0s31f6 on steam.
#  - Refuses to capture if that interface is not on the onboard network, since
#    a capture of the wrong link looks perfectly valid but answers nothing.
#    The reason is logged.
#
# tcpdump options:
#  - Excludes traffic that is not leaving the aircraft:
#      - onboard to onboard on 192.168.84.0/24
#      - onboard to onboard on 192.168.1.0/24
#      - all multicast, 224.0.0.0/4, in either direction (the NIDAS data
#        streams, mDNS, IGMP, SSDP)
#    Broadcast is not excluded here, so it is still in the captures; the
#    analysis drops it, along with anything else local that gets through.
#  -i Interface
#  -C, -W  Creates up to 10 100MB log files. Rotates logs
#  -s Only snapshots 96 bytes of data, rather than the default 262144,
#     to decrease logsize.
#
# Overrides, for testing on a machine that does not fit the above:
#  INTERFACE=<dev>    skip detection and capture on <dev>
#  EXPECTED_NET=<pfx> address prefix the detected interface must have
#  WAIT_SECS=<n>      how long to wait at boot for a default route
###############################################################################

logfile="satcom_capture.log"
# Overridable so the tests can exercise the startup logic off the aircraft.
output_dir="${SATCOM_LOG_DIR:-/var/log/ads/satcom}"
capture_dir="${SATCOM_CAPTURE_DIR:-/var/log/satcom-capture}"

INTERFACE="${INTERFACE:-}"
EXPECTED_NET="${EXPECTED_NET:-192.168.84.}"
WAIT_SECS="${WAIT_SECS:-60}"

# Any address off the aircraft will do; the kernel is only asked which way it
# would send traffic there. Nothing is transmitted.
PROBE_ADDR="8.8.8.8"

# Messages go to stderr, which systemd records in the journal, and to the
# script log once its directory exists.
log() {
    local msg
    msg="$(date -u '+%Y-%m-%d %H:%M:%S UTC') $*"
    echo "$msg" >&2
    [ -d "$output_dir" ] && echo "$msg" >> "$output_dir/$logfile"
}

mkdir -p "$output_dir" || { log "could not create $output_dir"; exit 1; }

##
# tcpdump drops privileges to the tcpdump user, so the directory it writes the
# captures into has to be owned by that user. Creating it root-owned would
# leave a directory that exists but cannot be written to, which is worse than
# not creating it at all -- step 3 of INSTALL_LINUX.md would then look done.
##
if [ ! -d "$capture_dir" ]; then
    mkdir -p "$capture_dir" || { log "could not create $capture_dir"; exit 1; }
    if id tcpdump >/dev/null 2>&1; then
        chown tcpdump:tcpdump "$capture_dir" ||
          log "WARNING: could not chown $capture_dir to tcpdump:tcpdump; tcpdump will probably not be able to write there"
    else
        log "WARNING: no tcpdump user on this machine, so $capture_dir is left owned by $(id -un); see INSTALL_LINUX.md if the capture cannot write there"
    fi
    log "created $capture_dir"
fi

##
# The device and source address the kernel would use to reach off the aircraft,
# printed as "<dev> <src>".
#
# `ip route get` is used rather than `ip route show default` so that a machine
# with several default routes resolves them by metric exactly as the kernel
# will for the traffic itself.
##
route_info() {
    ip -4 route get "$PROBE_ADDR" 2>/dev/null | awk '
        NR == 1 {
            for (i = 1; i < NF; i++) {
                if ($i == "dev") dev = $(i + 1)
                if ($i == "src") src = $(i + 1)
            }
            print dev, src
            exit
        }'
}

interface=""
src_addr=""

if [ -n "$INTERFACE" ]; then
    interface="$INTERFACE"
    log "using forced interface $interface (INTERFACE is set, no detection)"
else
    # At boot the default route may not be up yet, even with the unit ordered
    # after network-online.target. Wait rather than dying on a race.
    waited=0
    while :; do
        read -r interface src_addr <<< "$(route_info)"
        [ -n "$interface" ] && break
        [ "$waited" -ge "$WAIT_SECS" ] && break
        sleep 5
        waited=$((waited + 5))
    done

    if [ -z "$interface" ]; then
        log "no default route after ${WAIT_SECS}s, so there is no way to tell which interface leaves the aircraft - not capturing"
        exit 1
    fi
    if [ "$waited" -gt 0 ]; then
        log "waited ${waited}s for a default route"
    fi

    # A default route out of some other link - hangar ethernet on the ramp, say -
    # would capture the wrong interface and look entirely normal afterwards.
    case "$src_addr" in
        "$EXPECTED_NET"*) ;;
        *)
            log "refusing to capture: traffic off the aircraft would leave by $interface from ${src_addr:-an unknown address}, which is not on ${EXPECTED_NET}x - that is not the satcom path (is a ground or hangar link up?). Set INTERFACE=$interface to capture it anyway."
            exit 1
            ;;
    esac
    log "detected interface $interface (address $src_addr, via the default route)"
fi

# Stamp logfile with date/time script started
date=$(date -u +%Y%m%d_%H%M%S)

# Some interface sanity checking
if [ ! -d "/sys/class/net/$interface" ]; then
    log "interface $interface not found - not capturing"
    exit 1
fi
[ "$(cat /sys/class/net/$interface/operstate)" = "up" ] ||
  { log "$interface is down - not capturing"; exit 1; }

log "capturing on $interface to $capture_dir/traffic${date}.pcap"

tcpdump 'not (src net 192.168.84.0/24 and dst net 192.168.84.0/24) and not (src net 192.168.1.0/24 and dst net 192.168.1.0/24) and not (src net 224.0.0.0/4 or dst net 224.0.0.0/4)' \
    -i ${interface} \
    -w "$capture_dir/traffic${date}.pcap" \
    -C 100 \
    -W 10 \
    -s 96 >> "$output_dir/$logfile" 2>&1

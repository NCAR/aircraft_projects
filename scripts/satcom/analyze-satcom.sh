#!/bin/bash
##
# Summarize satcom traffic that actually left the aircraft.
#
# Traffic that never got off the plane is excluded even when the capture
# contains it (older captures predate the tcpdump filter in satcom_capture.sh):
#   - multicast     224.0.0.0/4   (NIDAS data streams, mDNS, IGMP, SSDP)
#   - broadcast     255.255.255.255, 0.0.0.0
#   - onboard-only  RFC1918 on both ends
#
# Scope is whatever you name. With no argument it does every rf* flight
# directory under the capture root, which defaults to the current directory --
# so cd to wherever the captures live, or point --root at them.
#
# Usage:
#   analyze-satcom.sh                          # every rf* flight under the root
#   analyze-satcom.sh rf14_20260901            # one flight
#   analyze-satcom.sh rf14_20260901/applanix   # one subdir
#   analyze-satcom.sh <path>/traffic20260901_180236_brix01.pcap0  # one capture
#   analyze-satcom.sh 20260901_180236          # one capture, by date stamp
#
# Options:
#   --root DIR       where the captures live (default: current directory,
#                    or $SATCOM_ROOT if set)
#   --cache FILE     reverse DNS cache (default: $SATCOM_PTR_CACHE, else
#                    ${XDG_CACHE_HOME:-$HOME/.cache}/satcom-ptr.tsv)
#   --allowed LIST   onboard addresses the router permits off the aircraft,
#                    comma separated (default: $SATCOM_ALLOWED, else empty).
#                    Everyone else is addressed off-plane but dropped at the
#                    router, so their bytes never reach WAN2: with this set
#                    they are reported separately instead of inflating the
#                    total that is reconciled against the WAN2 counters.
#   --skip-existing  leave analysis files that are already present
#   --no-dns         skip reverse DNS; public IPs are reported as unknown
#   -h, --help       this message
#
# Writes one satcom-analysis_<stamp>[_<host>].txt per capture, plus a
# satcom-summary_*.txt per scope carrying hostnames alongside the IPs.
##

set -uo pipefail

SATCOM_ROOT="${SATCOM_ROOT:-$PWD}"
# The onboard gateway. Traffic to and from it is onboard-to-onboard and so is
# excluded from the off-plane flow totals, but it is reported on its own -- the
# router is the one host whose LAN conversations say something about the link.
GATEWAY="${SATCOM_GATEWAY:-192.168.84.1}"
# Onboard hosts the router permits off the aircraft, comma separated. Traffic
# from anyone else is addressed off-plane but dropped at the router, so it never
# reaches WAN2 and costs nothing on satcom -- counting it inflates the total
# that gets reconciled against the WAN2 counters and the carrier's bill. Left
# empty the totals include everyone, which is the old behaviour: the policy
# lives in the router, not here, and guessing it would be worse than not
# applying it.
ALLOWED="${SATCOM_ALLOWED:-}"
# Set per scope, and read by the hourly section to mark the partial hours at
# each end of the capture window.
SPAN_FIRST=0
SPAN_LAST=0
# Also set per scope, and read by the summary header: the first and last packet
# that actually crossed the satellite link, which is a narrower window than the
# captures ran for. Empty when a scope saw no off-plane traffic at all.
OFF_FIRST=""
OFF_LAST=""
PTR_CACHE="${SATCOM_PTR_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/satcom-ptr.tsv}"
SKIP_EXISTING=0
USE_DNS=1

# Overridable so the test suite can stub them out and stay off the network.
MERGECAP="${MERGECAP:-mergecap}"
TSHARK="${TSHARK:-tshark}"
DIG="${DIG:-dig}"

die() { echo "$(basename "$0"): $*" >&2; exit 1; }
usage() { sed -n '3,/^##$/p' "$0" | sed 's/^#\{1,2\} \{0,1\}//'; }

##
# How to install tshark and mergecap on this machine.
#
# Both come from one package, but its name differs by platform, and a hint
# naming the wrong package manager is worse than no hint. Probe for the package
# manager that is actually here rather than guessing from the distribution.
##
install_hint() {
    case "$(uname -s)" in
        Darwin) echo "brew install wireshark" ;;
        Linux)
            if   command -v dnf     >/dev/null 2>&1; then echo "sudo dnf install wireshark-cli"
            elif command -v apt-get >/dev/null 2>&1; then echo "sudo apt-get install tshark"
            elif command -v yum     >/dev/null 2>&1; then echo "sudo yum install wireshark"
            elif command -v zypper  >/dev/null 2>&1; then echo "sudo zypper install wireshark"
            elif command -v pacman  >/dev/null 2>&1; then echo "sudo pacman -S wireshark-cli"
            else echo "install the wireshark command-line tools"
            fi
            ;;
        *) echo "install the wireshark command-line tools" ;;
    esac
}

TARGETS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --root)          shift; SATCOM_ROOT="${1:-}"; [ -n "$SATCOM_ROOT" ] || die "--root needs a directory" ;;
        --cache)         shift; PTR_CACHE="${1:-}"; [ -n "$PTR_CACHE" ] || die "--cache needs a file" ;;
        --allowed)       shift; ALLOWED="${1:-}"; [ -n "$ALLOWED" ] || die "--allowed needs a list of onboard addresses" ;;
        --skip-existing) SKIP_EXISTING=1 ;;
        --no-dns)        USE_DNS=0 ;;
        -h|--help)       usage; exit 0 ;;
        -*)              die "unknown option $1 (try --help)" ;;
        *)               TARGETS+=("$1") ;;
    esac
    shift
done

# Checked after the options are parsed, so that --help still works on a machine
# where wireshark has not been installed yet.
for tool in "$TSHARK" "$MERGECAP"; do
    command -v "$tool" >/dev/null 2>&1 || die "$tool not found - try: $(install_hint)"
done

[ -d "$SATCOM_ROOT" ] || die "capture root not found: $SATCOM_ROOT"
shopt -s nullglob

##
# Reverse DNS is optional, and its absence is otherwise invisible: every public
# address just reads "unknown" with no hint why. Work out up front whether
# lookups can happen, and record a line for the summary when they cannot.
#
# A missing resolver also turns off lookups rather than letting several hundred
# doomed queries run -- each would cache "unknown" permanently, so names would
# stay wrong even after the resolver was installed.
##
DNS_NOTE=""
if [ "$USE_DNS" -eq 0 ]; then
    DNS_NOTE="lookups skipped (--no-dns); public addresses show as unknown"
elif ! command -v "$DIG" >/dev/null 2>&1; then
    DNS_NOTE="$DIG not found, so no lookups were made; public addresses show as unknown"
    USE_DNS=0
fi

mkdir -p "$(dirname "$PTR_CACHE")" 2>/dev/null
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Shared by every awk pass that has to tell onboard addresses from the world.
PRIV_FN='
function priv(ip) {
    return (ip ~ /^10\./ || ip ~ /^192\.168\./ || ip ~ /^127\./ ||
            ip ~ /^169\.254\./ || ip ~ /^172\.(1[6-9]|2[0-9]|3[01])\./)
}'

##
# Strip the rotation suffix so the parts of one capture session share a stem.
# tcpdump -C rotates traffic<stamp>_<host>.pcap0, .pcap1, ...; the Windows
# captures under applanix/ are single files named satcom_<stamp>.pcap
##
stem_of() { echo "${1%.pcap*}"; }

# Analysis-file label: the stamp, plus the host when the filename carries one.
label_of() {
    local base
    base="$(basename "$1")"
    base="${base#traffic}"
    base="${base#satcom_}"
    echo "$base"
}

# Capture host name: from the filename when present, else the directory
# (the applanix captures come off a Windows box and have no host token).
host_of() {
    local label
    label="$(label_of "$1")"
    if [[ "$label" =~ ^[0-9]{8}_[0-9]{6}_(.+)$ ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        basename "$(dirname "$1")"
    fi
}

##
# Extract off-plane flows from one capture session as bytes<TAB>src<TAB>dst,
# and write the session's first/last packet time to $TMP/session-span.
#
# The timestamp is taken from every frame, before any filtering, so a capture
# holding only excluded traffic still dates itself. It comes from the tshark
# pass we already make, which avoids a second read of the pcap just to date
# it. The caller pairs the last packet with the filename's start stamp.
#
# tshark comma-joins a field when a packet carries two IP headers (ICMP errors
# quote the packet that failed), so keep the first value -- that is the header
# that was actually on the wire.
#
# Use frame.len, not ip.len. frame.len still excludes the 7-byte preamble, 1-byte
# start frame delimiter (SFD), 4-byte Ethernet FCS, and 12 -byte inter-frame gap.
#  ← not captured →                                                  ← not captured →
#┌──────────┬─────┐┌───────────────────────────────────────────────┐┌─────┬─────────┐
#│ Preamble │ SFD ││  Dst MAC │ Src MAC │ Type │   IP packet   │pad ││ FCS │   IFG   │
#│    7     │  1  ││    6     │    6    │  2   │               │    ││  4  │   12    │
#└──────────┴─────┘└───────────────────────────────────────────────┘└─────┴─────────┘
#                   └────── 14 bytes ──────────┘└─── ip.len ───┘
#                  └───────────────── frame.len ──────────────────┘
#
# DNS also goes to $TMP/session-dns, as bucket<TAB>response<TAB>bytes<TAB>name,
# out of this same pass rather than a second read of the pcap. Lookups sent to
# an onboard resolver never left the aircraft, so they stay out of the flow
# totals -- but each one the resolver cannot answer from cache costs a satcom
# round trip that no onboard capture can see. Captures taken before the filter
# kept host-to-resolver traffic yield nothing here and the section is omitted.
##

extract_flows() {
    : > "$TMP/session-span"; : > "$TMP/session-dns"; : > "$TMP/session-syslog"
    : > "$TMP/session-gw"; : > "$TMP/session-hourly"
    : > "$TMP/session-offspan"
    "$MERGECAP" -w - "$@" 2>/dev/null | \
    "$TSHARK" -r - --disable-protocol drbd -T fields \
        -e ip.src -e ip.dst -e frame.len -e frame.time_epoch \
        -e dns.flags.response -e dns.qry.name -e syslog.msg -e icmp.type 2>/dev/null | \
    awk -F'\t' -v spanfile="$TMP/session-span" -v dnsfile="$TMP/session-dns" \
        -v syslogfile="$TMP/session-syslog" -v gwfile="$TMP/session-gw" \
        -v hourlyfile="$TMP/session-hourly" \
        -v offspanfile="$TMP/session-offspan" \
        -v gw="$GATEWAY" "$PRIV_FN"'
        function mcast(ip) { split(ip, o, "."); return (o[1] + 0 >= 224 && o[1] + 0 <= 239) }
        function bcast(ip) { return (ip == "255.255.255.255" || ip == "0.0.0.0") }
        {
            ts = $4 + 0
            if (ts > 0) {
                if (first == 0 || ts < first) first = ts
                if (ts > last) last = ts
            }

            split($1, a, ","); split($2, b, ",")
            s = a[1]; d = b[1]
            if (s == "" || d == "") next          # no IPv4 layer (ARP, IPv6)
            if (mcast(s) || mcast(d)) next        # never left the plane
            if (bcast(s) || bcast(d)) next

            # mDNS and LLMNR are multicast and already gone by here, so what is
            # left is unicast resolver traffic. Recorded before the onboard-to-
            # onboard filter drops it, since that is exactly the case of interest.
            if ($5 != "") {
                # tshark renders booleans as True/False from 4.x and as 1/0
                # before that, so normalize to 1/0 here and let the summary
                # read one shape whatever version the capture host runs.
                split($5, r, ","); split($6, q, ",")
                printf "%s\t%d\t%s\t%s\n",
                       (priv(s) && priv(d) ? "lan" : "off"),
                       (r[1] == "True" || r[1] == "1"), $3, q[1] > dnsfile
            }

            # The router logs to syslog here. tshark strips the priority,
            # timestamp and tag, leaving the message body.
            #
            # Take the message only when the frame is not ICMP. When nothing is
            # listening on 514 the destination answers with a port unreachable,
            # and that error quotes the datagram that caused it, so tshark
            # dissects the very same message a second time. Counting both
            # doubles every message and invents a second sender.
            if ($7 != "" && $8 == "") print $7 > syslogfile

            if (priv(s) && priv(d)) {             # onboard to onboard
                if (s == gw || d == gw) gwbytes[s "\t" d] += $3
                next
            }
            bytes[s "\t" d] += $3

            # The same bytes again, bucketed into the UTC hour they crossed in,
            # so a flight can be laid beside the carrier'"'"'s hourly figures and
            # read for where the two start to disagree rather than only by how
            # much. The onboard host is kept in the key so the allowlist can be
            # applied later: comparing a carrier bill against a total that
            # includes traffic the router dropped would compare nothing.
            if (ts > 0) {
                hour = int(ts / 3600) * 3600
                if (priv(s)) hourly[hour "\t" s "\ts"] += $3
                else         hourly[hour "\t" d "\tr"] += $3

                # When this onboard host first and last had a packet on the
                # link. Kept per host because the allowlist is applied further
                # down: a host the router blocked put nothing on satcom, so
                # its packets must not be allowed to widen the window.
                host = priv(s) ? s : d
                if (!(host in ofirst) || ts < ofirst[host]) ofirst[host] = ts
                if (ts > olast[host]) olast[host] = ts
            }
        }
        END {
            for (f in bytes) printf "%d\t%s\n", bytes[f], f
            for (f in gwbytes) printf "%d\t%s\n", gwbytes[f], f > gwfile
            for (f in hourly) printf "%s\t%d\n", f, hourly[f] > hourlyfile
            for (h in ofirst)
                printf "%s\t%.6f\t%.6f\n", h, ofirst[h], olast[h] > offspanfile
            if (last > 0) printf "%.6f\t%.6f\n", first, last > spanfile
        }'
}

# Epoch seconds to a readable UTC stamp, on both BSD and GNU date.
fmt_epoch() {
    local secs="${1%.*}"
    date -u -r "$secs" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || \
    date -u -d "@$secs" '+%Y-%m-%d %H:%M:%S' 2>/dev/null
}

##
# The YYYYMMDD_HHMMSS in a capture filename to epoch seconds.
#
# satcom_capture.sh stamps the name with `date -u` when tcpdump starts, so
# this is the capture's true start -- unlike the first packet, which only
# shows when traffic happened to appear. Measured against the captures on
# hand, the first packet lands 0-63 s after the stamp for both the Linux
# traffic<stamp>_<host> names and the Windows applanix satcom_<stamp> ones.
##
stamp_epoch() {
    local s
    s="$(expr "$1" : '\([0-9]\{8\}_[0-9]\{6\}\)')" || return 1
    [ -n "$s" ] || return 1
    date -u -j -f "%Y%m%d_%H%M%S" "$s" "+%s" 2>/dev/null && return 0
    date -u -d "${s:0:4}-${s:4:2}-${s:6:2} ${s:9:2}:${s:11:2}:${s:13:2}" "+%s" 2>/dev/null
}

# Aggregate a flows TSV by src/dst pair, largest first.
aggregate() {
    awk -F'\t' '{ bytes[$2 "\t" $3] += $1 }
                END { for (f in bytes) printf "%d\t%s\n", bytes[f], f }' "$1" \
        | sort -k1,1rn
}

# Analysis files keep the original "src => dst: N MB" shape. Reads stdin.
write_analysis() {
    awk -F'\t' '{ printf "%s => %s: %.2f MB\n", $2, $3, $1 / 1000000 }'
}

##
# Resolve the public IPs in a flows file, appending ip<TAB>name to the name map.
# Answers are cached across runs; delete $PTR_CACHE to force fresh lookups.
##
resolve_public() {
    local flows="$1" namemap="$2"

    awk -F'\t' "$PRIV_FN"'
        { if (!priv($2)) print $2; if (!priv($3)) print $3 }' "$flows" \
        | sort -u > "$TMP/public"
    [ -s "$TMP/public" ] || return 0
    [ -f "$PTR_CACHE" ] || : > "$PTR_CACHE"

    if [ "$USE_DNS" -eq 1 ]; then
        # Look up only what the cache does not already cover. Keyed on FILENAME
        # rather than NR==FNR, which breaks when the cache file is empty.
        awk -F'\t' -v cache="$PTR_CACHE" '
            FILENAME == cache { seen[$1]; next }
            !($1 in seen)' "$PTR_CACHE" "$TMP/public" > "$TMP/pending"
        if [ -s "$TMP/pending" ]; then
            echo "  resolving $(wc -l < "$TMP/pending" | tr -d ' ') public IP(s)..." >&2
            # DIG is exported so the xargs children pick it up from the
            # environment; it cannot be interpolated alongside the {} token.
            DIG="$DIG" xargs -P 12 -I{} sh -c \
                'n=$("$DIG" +short +time=2 +tries=1 -x {} 2>/dev/null | head -1)
                 n=${n%.}
                 printf "%s\t%s\n" "{}" "${n:-unknown}"' \
                < "$TMP/pending" >> "$PTR_CACHE"
        fi
    fi

    awk -F'\t' -v cache="$PTR_CACHE" '
        FILENAME == cache { if ($2 != "") name[$1] = $2; next }
        { print $1 "\t" ($1 in name ? name[$1] : "unknown") }' \
        "$PTR_CACHE" "$TMP/public" >> "$namemap"
}

##
# The DNS section, from bucket<TAB>response<TAB>bytes<TAB>name records.
#
# Queries counted alone, not queries plus responses: a response echoes the
# question it answers, so counting both double-counts every name.
#
# Unanswered queries are worth watching. A resolver timeout costs the lookup
# again on retry, and with a search domain configured glibc then tries the name
# with that domain appended, so one failure can become three lookups.
##
write_dns_summary() {
    local dnsfile="$1"
    [ -s "$dnsfile" ] || return 0

    echo
    echo "DNS"
    awk -F'\t' '
        $1 == "lan" { n[$2]++; b[$2] += $3 }
        $1 == "off" { offn++; offb += $3 }
        END {
            printf "  %-24s %8d   avg %6.1f B\n", "queries to resolver",
                   n["0"], (n["0"] ? b["0"] / n["0"] : 0)
            printf "  %-24s %8d   avg %6.1f B\n", "responses",
                   n["1"], (n["1"] ? b["1"] / n["1"] : 0)
            miss = n["0"] - n["1"]
            if (miss < 0) miss = 0
            printf "  %-24s %8d   %s\n", "unanswered", miss,
                   (n["0"] ? sprintf("(%.1f%%)", miss * 100 / n["0"]) : "")
            printf "  %-24s %8.2f MB\n", "onboard DNS traffic",
                   (b["0"] + b["1"]) / 1000000
            if (offn)
                printf "  %-24s %8d   %.2f MB\n", "DNS sent off-plane", offn, offb / 1000000
        }' "$dnsfile"

    echo
    printf "  %10s  %s\n" "QUERIES" "NAME"
    awk -F'\t' '$1 == "lan" && $2 == "0" && $4 != "" { c[$4]++ }
                END { for (q in c) printf "  %10d  %s\n", c[q], q }' "$dnsfile" \
        | sort -k1,1rn | head -20
}

##
# Off-plane traffic by UTC hour, from hour<TAB>host<TAB>dir<TAB>bytes records.
#
# The carrier reports hourly, and a whole-flight total can only say whether the
# two figures differ. By hour they can be read for *when* they start to differ,
# which is a far stronger test: a fault that begins partway through a flight --
# the router'"'"'s conntrack table filling, say -- shows as two columns that track
# each other and then separate at a particular hour. A discrepancy present from
# the first hour is a different fault entirely.
#
# Honours the allowlist, for the same reason the total does. Hours are UTC and
# aligned to the wall clock; whether the carrier aligns theirs the same way is
# worth confirming before reading much into a one-hour offset.
#
# The first and last hours are marked when the capture window starts or ends
# inside them. The mark says only that: the capture covered part of the clock
# hour. It does not mean the figure is low.
#
# The carrier bills what crossed the link, and nothing else is on the link, so
# their hour covers the same traffic ours does however much of the clock hour
# that took. A marked hour is therefore still directly comparable. What the
# mark is really for is the one case where the two genuinely differ: the
# satellite terminal comes up with aircraft power, while a capture cannot start
# until its machine has booted, so the first hour can miss traffic that was
# already flowing. The mark says "check when this capture started" -- not
# "discount this row".
##
write_hourly_summary() {
    local hourlyfile="$1"
    [ -s "$hourlyfile" ] || return 0

    echo
    echo "By hour (UTC)"
    printf "  %-17s %9s %9s %10s %12s\n" \
        "HOUR" "SENT MB" "RECV MB" "TOTAL MB" "CUMULATIVE"
    # awk sorts and totals; the shell formats the timestamps, because strftime
    # is a gawk extension and the awk on a Mac does not have it.
    awk -F'\t' -v list="$ALLOWED" '
        BEGIN {
            n = split(list, a, /[, ]+/)
            for (i = 1; i <= n; i++) if (a[i] != "") ok[a[i]] = 1
            any = (list != "")
        }
        { if (any && !($2 in ok)) next
          if ($3 == "s") sent[$1] += $4; else recv[$1] += $4
          seen[$1] = 1 }
        END { for (h in seen)
                  printf "%d\t%d\t%d\n", h, sent[h] + 0, recv[h] + 0 }' \
        "$hourlyfile" \
        | sort -k1,1n \
        | awk -F'\t' '{ cum += $2 + $3
              printf "%d\t%.2f\t%.2f\t%.2f\t%.2f\n", $1,
                     $2 / 1000000, $3 / 1000000,
                     ($2 + $3) / 1000000, cum / 1000000 }' \
        | while IFS=$'\t' read -r hour sent recv total cum; do
              mark=""
              if [ "${SPAN_FIRST:-0}" != "0" ] && \
                 awk -v a="$SPAN_FIRST" -v h="$hour" 'BEGIN { exit !(a > h) }'; then
                  mark="   (partial)"
              elif [ "${SPAN_LAST:-0}" != "0" ] && \
                   awk -v b="$SPAN_LAST" -v h="$hour" \
                       'BEGIN { exit !(b < h + 3600) }'; then
                  mark="   (partial)"
              fi
              printf "  %-17s %9s %9s %10s %12s%s\n" \
                  "$(fmt_epoch "$hour" | cut -c1-16)" \
                  "$sent" "$recv" "$total" "$cum" "$mark"
          done
}

##
# Traffic from onboard hosts the router does not let out, as bytes<TAB>src<TAB>dst.
#
# It was addressed off-plane, so the capture sees it and the old totals counted
# it, but the router drops it and it never reaches WAN2. Reporting it here
# rather than silently discarding it keeps both facts available: how much a
# blocked host is still trying to send, and the fact that none of it was paid
# for. A host appearing here with a large figure is worth chasing at the host,
# since it is retrying something that cannot succeed.
##
write_blocked_summary() {
    local blockedfile="$1" namemap="$2"
    [ -s "$blockedfile" ] || return 0

    echo
    echo "Blocked at the router (never reached WAN2, not in the total)"
    printf "  %10s  %s\n" "MB" "ONBOARD HOST"
    awk -F'\t' -v map="$namemap" "$PRIV_FN"'
        FILENAME == map { if ($2 != "") name[$1] = $2; next }
        { host = priv($2) ? $2 : $3; b[host] += $1 }
        END { for (h in b)
                  printf "%.2f\t%s (%s)\n", b[h] / 1000000, h,
                         (h in name ? name[h] : "unknown") }' "$namemap" "$blockedfile" \
        | sort -k1,1rn \
        | awk -F'\t' '{ printf "  %10s  %s\n", $1, $2 }'
}

##
# Traffic to and from the gateway, as bytes<TAB>src<TAB>dst.
#
# None of this crosses satcom -- it is onboard-to-onboard and is deliberately
# absent from the Flows totals, which exist to be reconciled against the WAN2
# port counters. It is reported separately because the router is where the link
# is managed: its DNS service, its syslog, its DHCP and any ICMP it returns all
# show up here, and a capture that keeps `host <gateway>` is the only view of
# them there is. Folding these bytes into Flows would corrupt the one number
# the summary exists to produce.
##
write_gateway_summary() {
    local gwfile="$1"
    [ -s "$gwfile" ] || return 0

    echo
    echo "Gateway ($GATEWAY, onboard only -- not counted in Flows)"
    printf "  %10s  %-24s %s\n" "MB" "SOURCE" "DESTINATION"
    awk -F'\t' '{ b[$2 "\t" $3] += $1 }
        END { for (f in b) { split(f, p, "\t")
                   printf "%.2f\t%s\t%s\n", b[f] / 1000000, p[1], p[2] } }' "$gwfile" \
        | sort -k1,1rn \
        | awk -F'\t' '{ printf "  %10s  %-24s %s\n", $1, $2, $3 }'
    awk -F'\t' '{ t += $1 }
        END { printf "  %10.2f  %s\n", t / 1000000, "total" }' "$gwfile"
}

##
# The router's own syslog, present once the capture keeps traffic to and from
# the gateway. Nothing here parses the message text: the format is the router's,
# and a parser written against a guess would report confident nonsense. Only the
# count and the onboard addresses mentioned are summarized -- the messages go to
# a companion file to be read directly, and parsing can follow once the real
# format is in hand.
##
write_syslog_summary() {
    local sysfile="$1"
    [ -s "$sysfile" ] || return 0

    echo
    echo "Router syslog"
    printf "  %-24s %8d\n" "messages" "$(wc -l < "$sysfile" | tr -d ' ')"

    local hosts
    hosts="$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$sysfile" 2>/dev/null \
             | awk "$PRIV_FN"'priv($0)' | sort | uniq -c | sort -k1,1rn | head -20)"
    [ -n "$hosts" ] || return 0
    echo
    printf "  %10s  %s\n" "MENTIONS" "ONBOARD ADDRESS"
    echo "$hosts" | awk '{ printf "  %10d  %s\n", $1, $2 }'
}

##
# Build the summary on stdout.
#
# Onboard names come from the capture filenames: a capture taken on a machine's
# own interface only ever shows that machine's own off-plane unicast, so the
# private IP in its flows identifies the machine. Nothing is inferred from a
# static hosts table -- an IP we cannot place is reported as unknown.
##
write_summary() {
    local flows="$1" namemap="$2" scope="$3" captures="$4" collected="$5"
    local dnsfile="${6:-}" sysfile="${7:-}" gwfile="${8:-}" blockedfile="${9:-}"
    local hourlyfile="${10:-}"

    echo "Satcom off-plane traffic summary: $scope"
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Captures:  $captures"
    echo "Collected: $collected"
    # Read from the globals rather than an eleventh positional argument.
    if [ -n "$OFF_FIRST" ]; then
        printf 'Off-plane: %s to %s UTC (%.2f h)\n' \
            "$(fmt_epoch "$OFF_FIRST")" "$(fmt_epoch "$OFF_LAST")" \
            "$(awk -v a="$OFF_FIRST" -v b="$OFF_LAST" \
                   'BEGIN { print (b - a) / 3600 }')"
        echo "           first to last packet that crossed the satellite link."
        echo "           Collected above is wider: it opens when the earliest"
        echo "           tcpdump started and closes on the last frame of any"
        echo "           kind, onboard-only traffic included."
    fi
    echo "Excluded:  multicast (224.0.0.0/4), broadcast, and onboard-only traffic"
    echo "Protocols: all of them. Traffic is selected by address, never by protocol,"
    echo "           so TCP, UDP (DNS, NTP, QUIC, DTLS), ICMP and the rest are all"
    echo "           counted here. Nothing is filtered by port or protocol anywhere."
    [ -n "$DNS_NOTE" ] && echo "Hostnames: $DNS_NOTE"
    echo
    awk -F'\t' '{ t += $1 } END { printf "Total off-plane: %.2f MB\n", t / 1000000 }' "$flows"
    if [ -n "$blockedfile" ] && [ -s "$blockedfile" ]; then
        awk -F'\t' '{ t += $1 }
            END { printf "Blocked at router: %.2f MB (addressed off-plane, dropped before WAN2, not counted above)\n",
                         t / 1000000 }' "$blockedfile"
    fi

    echo
    echo "Onboard hosts"
    printf "  %-34s %10s %10s\n" "HOST" "SENT MB" "RECV MB"
    awk -F'\t' -v map="$namemap" "$PRIV_FN"'
        FILENAME == map { if ($2 != "") name[$1] = $2; next }
        {
            if (priv($2)) { sent[$2] += $1; seen[$2] }
            if (priv($3)) { recv[$3] += $1; seen[$3] }
        }
        END {
            for (ip in seen)
                printf "%d\t%s (%s)\t%.2f\t%.2f\n", sent[ip] + recv[ip],
                       ip, (ip in name ? name[ip] : "unknown"),
                       sent[ip] / 1000000, recv[ip] / 1000000
        }' "$namemap" "$flows" \
        | sort -k1,1rn \
        | awk -F'\t' '{ printf "  %-34s %10s %10s\n", $2, $3, $4 }'

    # A host that sent off-plane traffic and received none did not have a quiet
    # flight. TCP and QUIC both answer, so either nothing came back or the
    # capture is not seeing its own inbound traffic. The two are told apart by
    # the sender's own packets: a capture that is merely half-blind still shows
    # the host's ACKs and data once a connection is up, so outbound consisting
    # of nothing but bare SYNs means the connections never formed at all.
    #
    # The usual reason is the firewall: only some onboard hosts are permitted
    # past the router, and a blocked host's SYNs are dropped there. Those bytes
    # are counted above as off-plane because that is where they were addressed,
    # but they never reached WAN2 and cost nothing on satcom. The total is
    # overstated by exactly that much, which is why this says so here.
    awk -F'\t' -v map="$namemap" "$PRIV_FN"'
        FILENAME == map { if ($2 != "") name[$1] = $2; next }
        {
            if (priv($2)) { sent[$2] += $1; seen[$2] }
            if (priv($3)) { recv[$3] += $1; seen[$3] }
        }
        END {
            for (ip in seen)
                if (sent[ip] > 0 && recv[ip] + 0 == 0)
                    printf "  %s (%s) sent %.2f MB and received nothing. If its outbound is\n  all SYNs the router blocked it, so those MB never crossed satcom and the\n  total above is overstated by them; otherwise its capture is missing inbound.\n",
                           ip, (ip in name ? name[ip] : "unknown"),
                           sent[ip] / 1000000
        }' "$namemap" "$flows"

    [ -n "$blockedfile" ] && write_blocked_summary "$blockedfile" "$namemap"
    [ -n "$gwfile" ] && write_gateway_summary "$gwfile"
    [ -n "$hourlyfile" ] && write_hourly_summary "$hourlyfile"
    [ -n "$dnsfile" ] && write_dns_summary "$dnsfile"
    [ -n "$sysfile" ] && write_syslog_summary "$sysfile"

    echo
    echo "Flows"
    printf "  %10s  %-48s %s\n" "MB" "SOURCE" "DESTINATION"
    awk -F'\t' -v map="$namemap" '
        function label(ip) { return ip " (" (ip in name ? name[ip] : "unknown") ")" }
        FILENAME == map { if ($2 != "") name[$1] = $2; next }
        { printf "  %10.2f  %-48s %s\n", $1 / 1000000, label($2), label($3) }' \
        "$namemap" "$flows"

    awk -F'\t' -v map="$namemap" '
        FILENAME == map { if ($2 != "") name[$1] = $2; next }
        {
            for (i = 2; i <= 3; i++)
                if (!($i in name) || name[$i] == "unknown") u[$i]
        }
        END {
            n = 0
            for (ip in u) n++
            if (n > 0) {
                printf "\nNo hostname found for %d IP(s):\n", n
                for (ip in u) printf "  %s\n", ip
            }
        }' "$namemap" "$flows"
}

##
# Analyze every capture session under a directory, then summarize.
# Pass only_stem to restrict the scope to a single capture.
##
process_scope() {
    local scope_dir="$1" scope_name="$2" only_stem="${3:-}"
    local flows="$TMP/flows" namemap="$TMP/namemap" dns="$TMP/dns" sys="$TMP/syslog"
    local gw="$TMP/gw" hourly="$TMP/hourly"
    # Every one of these accumulates across the captures in a scope, so every
    # one has to be emptied when a new scope starts -- a run over several
    # flights reuses the same $TMP.
    : > "$flows"; : > "$namemap"; : > "$TMP/spans"; : > "$dns"; : > "$sys"
    : > "$gw"; : > "$hourly"; : > "$TMP/offspan"

    local stems
    stems="$(find "$scope_dir" -name '*.pcap*' -type f 2>/dev/null \
             | while read -r f; do stem_of "$f"; done | sort -u)"
    [ -n "$stems" ] || { echo "no captures under $scope_dir" >&2; return 1; }

    local count=0 names="" stem label host out_file
    local parts pkt_first pkt_last sess_start
    while IFS= read -r stem; do
        [ -n "$stem" ] || continue
        [ -z "$only_stem" ] || [ "$stem" = "$only_stem" ] || continue

        parts=("$stem".pcap*)
        [ "${#parts[@]}" -gt 0 ] || continue

        label="$(label_of "$stem")"
        host="$(host_of "$stem")"
        out_file="$(dirname "$stem")/satcom-analysis_${label}.txt"

        extract_flows "${parts[@]}" > "$TMP/session"
        if [ "$SKIP_EXISTING" -eq 1 ] && [ -s "$out_file" ]; then
            echo "  skip (exists) $(basename "$out_file")"
        else
            echo "  $label [${#parts[@]} file(s), host=$host]"
            aggregate "$TMP/session" | write_analysis > "$out_file"
        fi

        # The private IP in this capture's off-plane flows is the capture host.
        awk -F'\t' -v h="$host" "$PRIV_FN"'
            { if (priv($2)) c[$2] += $1; if (priv($3)) c[$3] += $1 }
            END {
                best = ""; max = -1
                for (ip in c) if (c[ip] > max) { max = c[ip]; best = ip }
                if (best != "") print best "\t" h
            }' "$TMP/session" >> "$namemap"

        cat "$TMP/session" >> "$flows"
        [ -s "$TMP/session-dns" ] && cat "$TMP/session-dns" >> "$dns"
        [ -s "$TMP/session-syslog" ] && cat "$TMP/session-syslog" >> "$sys"
        [ -s "$TMP/session-gw" ] && cat "$TMP/session-gw" >> "$gw"
        [ -s "$TMP/session-hourly" ] && cat "$TMP/session-hourly" >> "$hourly"
        [ -s "$TMP/session-offspan" ] &&
            cat "$TMP/session-offspan" >> "$TMP/offspan"

        # Start from the filename, which is when tcpdump started. The end can
        # only be the last packet, a lower bound on when it stopped. A capture
        # holding nothing but excluded traffic still reports its start, so a
        # quiet host stays distinguishable from a capture that died.
        pkt_first=""; pkt_last=0
        if [ -s "$TMP/session-span" ]; then
            pkt_first="$(cut -f1 "$TMP/session-span")"
            pkt_last="$(cut -f2 "$TMP/session-span")"
        fi
        sess_start="$(stamp_epoch "$label" 2>/dev/null)" || sess_start=""
        if [ -z "$sess_start" ]; then
            sess_start="$pkt_first"
        elif [ -n "$pkt_first" ]; then
            # Never claim a start after the first packet, whatever the clocks say.
            sess_start="$(awk -v a="$sess_start" -v b="$pkt_first" \
                'BEGIN { print (b < a ? b : a) }')"
        fi
        [ -n "$sess_start" ] && printf '%s\t%s\n' "$sess_start" "$pkt_last" >> "$TMP/spans"

        count=$((count + 1))
        # One host can contribute several sessions (applanix rotates hourly).
        case ",$names," in
            *",$host,"*) ;;
            *) names="${names:+$names,}$host" ;;
        esac
    done <<< "$stems"

    [ "$count" -gt 0 ] || { echo "nothing to do in $scope_dir" >&2; return 1; }

    # With an allowlist, the flows split in two before anything is totalled:
    # what the router let out, and what it dropped. Both are real observations
    # and both are reported -- only the first is satcom traffic.
    : > "$TMP/blocked-agg"
    if [ -n "$ALLOWED" ]; then
        : > "$TMP/flows-allowed"; : > "$TMP/flows-blocked"
        awk -F'\t' -v list="$ALLOWED" -v af="$TMP/flows-allowed" \
            -v bf="$TMP/flows-blocked" "$PRIV_FN"'
            BEGIN { n = split(list, a, /[, ]+/)
                    for (i = 1; i <= n; i++) if (a[i] != "") ok[a[i]] = 1 }
            { host = priv($2) ? $2 : $3
              print > (host in ok ? af : bf) }' "$flows"
        aggregate "$TMP/flows-allowed" > "$TMP/agg"
        aggregate "$TMP/flows-blocked" > "$TMP/blocked-agg"
    else
        aggregate "$flows" > "$TMP/agg"
    fi
    resolve_public "$TMP/agg" "$namemap"
    [ -s "$TMP/blocked-agg" ] && resolve_public "$TMP/blocked-agg" "$namemap"

    # Collection window: earliest start to latest packet across the scope.
    # Captures within a flight are staggered, so this is the union of their
    # windows, not any single capture's runtime. The duration is a minimum --
    # tcpdump's stop time is not recorded anywhere.
    local collected="unknown (no captures)"
    if [ -s "$TMP/spans" ]; then
        local span_first span_last span_hours
        span_first="$(awk -F'\t' 'NR == 1 || $1 < m { m = $1 } END { printf "%.6f", m }' "$TMP/spans")"
        span_last="$(awk -F'\t' '$2 > m { m = $2 } END { printf "%.6f", m + 0 }' "$TMP/spans")"
        # The hourly section needs these to mark the partial hours at each end.
        SPAN_FIRST="$span_first"; SPAN_LAST="$span_last"
        if awk -v l="$span_last" 'BEGIN { exit !(l > 0) }'; then
            span_hours="$(awk -v a="$span_first" -v b="$span_last" \
                'BEGIN { printf "%.2f", (b - a) / 3600 }')"
            collected="$(fmt_epoch "$span_first") to $(fmt_epoch "$span_last") UTC (>= ${span_hours} h)"
        else
            collected="from $(fmt_epoch "$span_first") UTC (no packets captured; end unknown)"
        fi
        [ "$count" -gt 1 ] && collected="$collected spanning $count captures"
    fi

    # The window in which traffic was actually on the satellite link. It is
    # narrower than the collection window above at both ends, for different
    # reasons. At the start, a capture cannot see traffic that flowed before
    # tcpdump was running, so this is an upper bound on when the link came up
    # -- it is not power-on. At the end it is a real observation: collection
    # runs on to the last frame of any kind, onboard-only chatter included,
    # which can be a long time after the link goes quiet. So unlike the
    # collection window, whose end is only a lower bound, both ends here are
    # observed packets and the duration is exact.
    #
    # Hosts the router blocked are left out, since their packets never reached
    # WAN2, so this honours --allowed exactly as the totals do.
    OFF_FIRST=""; OFF_LAST=""
    if [ -s "$TMP/offspan" ]; then
        awk -F'\t' -v list="$ALLOWED" '
            BEGIN { nok = 0; n = split(list, a, /[, ]+/)
                    for (i = 1; i <= n; i++)
                        if (a[i] != "") { ok[a[i]] = 1; nok++ } }
            nok == 0 || ($1 in ok) {
                if (f == "" || $2 < f) f = $2
                if ($3 > l) l = $3
            }
            END { if (f != "") printf "%.6f\t%.6f\n", f, l }' \
            "$TMP/offspan" > "$TMP/offwin"
        if [ -s "$TMP/offwin" ]; then
            OFF_FIRST="$(cut -f1 "$TMP/offwin")"
            OFF_LAST="$(cut -f2 "$TMP/offwin")"
        fi
    fi

    local summary_file
    if [ -n "$only_stem" ]; then
        summary_file="$(dirname "$only_stem")/satcom-summary_${scope_name}.txt"
    else
        summary_file="$scope_dir/satcom-summary_${scope_name}.txt"
    fi
    write_summary "$TMP/agg" "$namemap" "$scope_name" \
        "$count session(s) from ${names//,/, }" "$collected" "$dns" "$sys" "$gw" \
        "$TMP/blocked-agg" "$hourly" > "$summary_file"
    echo "  summary: $summary_file"

    # The router's log is kept verbatim beside the summary, not folded into it.
    if [ -s "$sys" ]; then
        local syslog_file="${summary_file%/*}/satcom-syslog_${scope_name}.txt"
        cp "$sys" "$syslog_file"
        echo "  syslog:  $syslog_file"
    fi
}

##
# Resolve one user-supplied target into a scope and run it.
##
run_target() {
    local t="$1" stem dir matches

    # A capture file.
    if [ -f "$t" ]; then
        stem="$(stem_of "$t")"
        echo "== $(basename "$stem")"
        process_scope "$(dirname "$t")" "$(label_of "$stem")" "$stem"
        return
    fi

    # A directory, given as a path or as a name under the root.
    dir=""
    if [ -d "$t" ]; then dir="${t%/}"
    elif [ -d "$SATCOM_ROOT/$t" ]; then dir="$SATCOM_ROOT/${t%/}"
    fi
    if [ -n "$dir" ]; then
        echo "== $(basename "$dir")"
        process_scope "$dir" "$(basename "$dir")"
        return
    fi

    # A bare date stamp: find the capture session it belongs to.
    if [[ "$t" =~ ^[0-9]{8}(_[0-9]{6})?$ ]]; then
        matches="$(find "$SATCOM_ROOT" -name "*${t}*.pcap*" -type f 2>/dev/null \
                   | while read -r f; do stem_of "$f"; done | sort -u)"
        [ -n "$matches" ] || die "no captures matching $t under $SATCOM_ROOT"
        while IFS= read -r stem; do
            echo "== $(basename "$stem")"
            process_scope "$(dirname "$stem")" "$(label_of "$stem")" "$stem"
        done <<< "$matches"
        return
    fi

    die "don't know how to handle target: $t"
}

if [ "${#TARGETS[@]}" -eq 0 ]; then
    # Every research flight. rf* deliberately leaves out maint_days.
    flights=("$SATCOM_ROOT"/rf*/)
    [ "${#flights[@]}" -gt 0 ] || die "no rf* directories in $SATCOM_ROOT
(run from the directory holding the flight dirs, or pass --root)"
    for d in "${flights[@]}"; do
        d="${d%/}"
        echo "== $(basename "$d")"
        process_scope "$d" "$(basename "$d")"
    done
else
    for t in "${TARGETS[@]}"; do run_target "$t"; done
fi

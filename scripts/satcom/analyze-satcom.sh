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
#   --skip-existing  leave analysis files that are already present
#   --no-dns         skip reverse DNS; public IPs are reported as unknown
#   -h, --help       this message
#
# Writes one satcom-analysis_<stamp>[_<host>].txt per capture, plus a
# satcom-summary_*.txt per scope carrying hostnames alongside the IPs.
##

set -uo pipefail

SATCOM_ROOT="${SATCOM_ROOT:-$PWD}"
PTR_CACHE="${SATCOM_PTR_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/satcom-ptr.tsv}"
SKIP_EXISTING=0
USE_DNS=1

# Overridable so the test suite can stub them out and stay off the network.
MERGECAP="${MERGECAP:-mergecap}"
TSHARK="${TSHARK:-tshark}"
DIG="${DIG:-dig}"

die() { echo "$(basename "$0"): $*" >&2; exit 1; }
usage() { sed -n '3,/^##$/p' "$0" | sed 's/^#\{1,2\} \{0,1\}//'; }

for tool in "$TSHARK" "$MERGECAP"; do
    command -v "$tool" >/dev/null 2>&1 || die "$tool not found (brew install wireshark)"
done

TARGETS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --root)          shift; SATCOM_ROOT="${1:-}"; [ -n "$SATCOM_ROOT" ] || die "--root needs a directory" ;;
        --cache)         shift; PTR_CACHE="${1:-}"; [ -n "$PTR_CACHE" ] || die "--cache needs a file" ;;
        --skip-existing) SKIP_EXISTING=1 ;;
        --no-dns)        USE_DNS=0 ;;
        -h|--help)       usage; exit 0 ;;
        -*)              die "unknown option $1 (try --help)" ;;
        *)               TARGETS+=("$1") ;;
    esac
    shift
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
##
extract_flows() {
    : > "$TMP/session-span"
    "$MERGECAP" -w - "$@" 2>/dev/null | \
    "$TSHARK" -r - --disable-protocol drbd -T fields \
        -e ip.src -e ip.dst -e ip.len -e frame.time_epoch 2>/dev/null | \
    awk -F'\t' -v spanfile="$TMP/session-span" "$PRIV_FN"'
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
            if (priv(s) && priv(d)) next          # onboard to onboard
            bytes[s "\t" d] += $3
        }
        END {
            for (f in bytes) printf "%d\t%s\n", bytes[f], f
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
    awk -F'\t' '{ printf "%s => %s: %.2f MB\n", $2, $3, $1 / 1048576 }'
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
# Build the summary on stdout.
#
# Onboard names come from the capture filenames: a capture taken on a machine's
# own interface only ever shows that machine's own off-plane unicast, so the
# private IP in its flows identifies the machine. Nothing is inferred from a
# static hosts table -- an IP we cannot place is reported as unknown.
##
write_summary() {
    local flows="$1" namemap="$2" scope="$3" captures="$4" collected="$5"

    echo "Satcom off-plane traffic summary: $scope"
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Captures:  $captures"
    echo "Collected: $collected"
    echo "Excluded:  multicast (224.0.0.0/4), broadcast, and onboard-only traffic"
    [ -n "$DNS_NOTE" ] && echo "Hostnames: $DNS_NOTE"
    echo
    awk -F'\t' '{ t += $1 } END { printf "Total off-plane: %.2f MB\n", t / 1048576 }' "$flows"

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
                       sent[ip] / 1048576, recv[ip] / 1048576
        }' "$namemap" "$flows" \
        | sort -k1,1rn \
        | awk -F'\t' '{ printf "  %-34s %10s %10s\n", $2, $3, $4 }'

    echo
    echo "Flows"
    printf "  %10s  %-48s %s\n" "MB" "SOURCE" "DESTINATION"
    awk -F'\t' -v map="$namemap" '
        function label(ip) { return ip " (" (ip in name ? name[ip] : "unknown") ")" }
        FILENAME == map { if ($2 != "") name[$1] = $2; next }
        { printf "  %10.2f  %-48s %s\n", $1 / 1048576, label($2), label($3) }' \
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
    local flows="$TMP/flows" namemap="$TMP/namemap"
    : > "$flows"; : > "$namemap"; : > "$TMP/spans"

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

    aggregate "$flows" > "$TMP/agg"
    resolve_public "$TMP/agg" "$namemap"

    # Collection window: earliest start to latest packet across the scope.
    # Captures within a flight are staggered, so this is the union of their
    # windows, not any single capture's runtime. The duration is a minimum --
    # tcpdump's stop time is not recorded anywhere.
    local collected="unknown (no captures)"
    if [ -s "$TMP/spans" ]; then
        local span_first span_last span_hours
        span_first="$(awk -F'\t' 'NR == 1 || $1 < m { m = $1 } END { printf "%.6f", m }' "$TMP/spans")"
        span_last="$(awk -F'\t' '$2 > m { m = $2 } END { printf "%.6f", m + 0 }' "$TMP/spans")"
        if awk -v l="$span_last" 'BEGIN { exit !(l > 0) }'; then
            span_hours="$(awk -v a="$span_first" -v b="$span_last" \
                'BEGIN { printf "%.2f", (b - a) / 3600 }')"
            collected="$(fmt_epoch "$span_first") to $(fmt_epoch "$span_last") UTC (>= ${span_hours} h)"
        else
            collected="from $(fmt_epoch "$span_first") UTC (no packets captured; end unknown)"
        fi
        [ "$count" -gt 1 ] && collected="$collected spanning $count captures"
    fi

    local summary_file
    if [ -n "$only_stem" ]; then
        summary_file="$(dirname "$only_stem")/satcom-summary_${scope_name}.txt"
    else
        summary_file="$scope_dir/satcom-summary_${scope_name}.txt"
    fi
    write_summary "$TMP/agg" "$namemap" "$scope_name" \
        "$count session(s) from ${names//,/, }" "$collected" > "$summary_file"
    echo "  summary: $summary_file"
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

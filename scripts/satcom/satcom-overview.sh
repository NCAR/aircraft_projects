#!/bin/bash
##
# Where the off-plane traffic goes, across flights.
#
# Reads the satcom-summary_*.txt files analyze-satcom.sh already wrote -- it
# never opens a pcap, so it is quick and needs no regeneration pass. Rerun it
# whenever you want a different grouping; rerun analyze-satcom.sh only when
# the captures themselves change.
#
# Columns:
#   OFF-PLANE DESTINATION   the far end of the traffic, named where possible
#   MB                      sent plus received
#   COLLECTION (HR)         hours of capture in the flights where it appeared
#   MB/HR                   MB divided by those hours
#
# Every 128.117.* address (UCAR/NCAR) gets its own row. Everything else is
# grouped: by the registrable domain of its reverse-DNS name, or -- when an
# address has no name -- by what its neighbours in the same /16 resolved to,
# falling back to the /16 itself. See vendor() and known_block() to adjust.
#
# Usage:
#   satcom-overview.sh                    # every rf* flight under the root
#   satcom-overview.sh rf14_20260901      # one flight (or several)
#   satcom-overview.sh <summary file>...  # specific summary files
#
# Options:
#   --root DIR   where the flight directories live (default: current directory,
#                or $SATCOM_ROOT if set)
#   --min MB     hide rows below this many MB (default 0.1; use 0 to show all)
#   -h, --help   this message
#
# Writes satcom-overview[_<scope>].txt to the root and prints the same report.
##

set -uo pipefail

SATCOM_ROOT="${SATCOM_ROOT:-$PWD}"
MIN_MB="0.1"

die() { echo "$(basename "$0"): $*" >&2; exit 1; }
usage() { sed -n '3,/^##$/p' "$0" | sed 's/^#\{1,2\} \{0,1\}//'; }

TARGETS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --root)    shift; SATCOM_ROOT="${1:-}"; [ -n "$SATCOM_ROOT" ] || die "--root needs a directory" ;;
        --min)     shift; MIN_MB="${1:-}"; [ -n "$MIN_MB" ] || die "--min needs a number" ;;
        -h|--help) usage; exit 0 ;;
        -*)        die "unknown option $1 (try --help)" ;;
        *)         TARGETS+=("$1") ;;
    esac
    shift
done

[ -d "$SATCOM_ROOT" ] || die "capture root not found: $SATCOM_ROOT"
shopt -s nullglob

summaries=()

##
# Collect the summary files under a directory, without counting anything twice.
#
# A directory-level summary already covers every capture beneath it -- rf14's
# covers its applanix/ subdirectory, and any single-capture summary sitting
# beside it -- so taking one prunes the rest of that subtree. A directory with
# no summary of its own is descended into, so a partly analyzed tree still
# reports what it has.
##
walk_dir() {
    local dir="$1" canon f sub
    canon="$dir/satcom-summary_$(basename "$dir").txt"
    if [ -f "$canon" ]; then
        summaries+=("$canon")
        return
    fi
    for f in "$dir"/satcom-summary_*.txt; do
        summaries+=("$f")
    done
    for sub in "$dir"/*/; do
        walk_dir "${sub%/}"
    done
}

scope="all"
if [ "${#TARGETS[@]}" -eq 0 ]; then
    # Research flights only. rf* deliberately leaves out maint_days, matching
    # what analyze-satcom.sh does with no argument.
    flights=("$SATCOM_ROOT"/rf*/)
    [ "${#flights[@]}" -gt 0 ] || die "no rf* directories in $SATCOM_ROOT
(run from the directory holding the flight dirs, or pass --root)"
    for d in "${flights[@]}"; do walk_dir "${d%/}"; done
else
    scope=""
    for t in "${TARGETS[@]}"; do
        if [ -f "$t" ]; then
            summaries+=("$t")
            scope="${scope:+$scope+}$(basename "$t" .txt)"
        else
            d=""
            [ -d "$t" ] && d="${t%/}"
            [ -z "$d" ] && [ -d "$SATCOM_ROOT/$t" ] && d="$SATCOM_ROOT/${t%/}"
            [ -n "$d" ] || die "no such flight or summary file: $t"
            walk_dir "$d"
            scope="${scope:+$scope+}$(basename "$d")"
        fi
    done
fi

[ "${#summaries[@]}" -gt 0 ] || die "no satcom-summary files found
(run analyze-satcom.sh first)"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

awk -v min_mb="$MIN_MB" -v root="${SATCOM_ROOT%/}" '
function priv(ip) {
    return (ip ~ /^10\./ || ip ~ /^192\.168\./ || ip ~ /^127\./ ||
            ip ~ /^169\.254\./ || ip ~ /^172\.(1[6-9]|2[0-9]|3[01])\./)
}
function slash16(ip,   o) { split(ip, o, "."); return o[1] "." o[2] }

# The registrable domain of a reverse-DNS name, mapped to the operator that
# several domains belong to. Extend the aliases as new ones show up.
function vendor(nm,   n, p, d) {
    n = split(nm, p, ".")
    d = (n >= 2) ? p[n - 1] "." p[n] : nm
    if (d == "1e100.net" || d == "googleusercontent.com" ||
        d == "google.com" || d == "gstatic.com")            return "Google"
    if (d == "akamaitechnologies.com" || d == "akamai.net") return "Akamai"
    if (d == "linodeusercontent.com" || d == "linode.com")  return "Linode"
    if (d == "vultrusercontent.com")                        return "Vultr"
    if (d == "amazonaws.com")                               return "Amazon AWS"
    if (d == "cloudflare.com")                              return "Cloudflare"
    if (d == "ucar.edu")                                    return "UCAR (other)"
    return d
}

# Addresses with no reverse-DNS name and no resolved neighbour in their /16.
function known_block(b) {
    if (b == "151.101") return "Fastly CDN"
    return ""
}

##
# Name each summary by its directory relative to the root, so a nested one
# reads as rf02_20260102/applanix. Using the bare directory name would let the
# applanix subdirectory of two different flights collide onto one key, merging
# hours that belong to separate flights.
##
FNR == 1 {
    flight = FILENAME
    if (root != "" && index(flight, root "/") == 1)
        flight = substr(flight, length(root) + 2)
    sub(/\/?satcom-summary_[^\/]*\.txt$/, "", flight)
    if (flight == "") { flight = FILENAME; sub(/.*\//, "", flight); sub(/\.txt$/, "", flight) }
    flights[flight] = 1; nflights++; inflow = 0
}

# Collection hours for this flight, from the header analyze-satcom.sh wrote.
/^Collected:/ {
    if (match($0, /\(>= [0-9.]+ h\)/)) {
        hours[flight] = substr($0, RSTART + 4, RLENGTH - 7) + 0
    } else {
        hours[flight] = 0            # a capture with no packets: end unknown
        undated++
    }
    next
}

##
# Carry forward the note analyze-satcom.sh leaves when it could not resolve
# names. Without it a summary built on a host with no resolver turns into a
# page of "unresolved <block>.x.x" rows here, with the cause a file away.
##
/^Hostnames:/ {
    reason = substr($0, index($0, ":") + 2)
    if (!(reason in dns_reason)) { dns_reason[reason] = 1; dns_nreason++ }
    dns_flights++
    next
}

/^Flows$/      { inflow = 1; next }
/^No hostname/ { inflow = 0 }

inflow && $1 ~ /^[0-9]+\.[0-9]+$/ {
    val = $1 + 0
    if (!priv($2))      { ip = $2; nm = $3 }
    else if (!priv($4)) { ip = $4; nm = $5 }
    else next
    gsub(/[()]/, "", nm)

    # Hold the rows; grouping needs the whole picture (see END).
    r++; r_ip[r] = ip; r_nm[r] = nm; r_mb[r] = val; r_fl[r] = flight
    if (nm != "unknown")
        block_vote[slash16(ip) "\t" vendor(nm)] += val    # what this /16 mostly is
    total_mb += val
}

END {
    # For each /16, the operator its named addresses mostly belong to. An
    # unnamed address is attributed to that rather than stranded on its own,
    # which is what keeps the Google ranges from splitting in two.
    for (k in block_vote) {
        split(k, p, "\t")
        if (block_vote[k] > best_vote[p[1]]) { best_vote[p[1]] = block_vote[k]; block_of[p[1]] = p[2] }
    }

    for (i = 1; i <= r; i++) {
        ip = r_ip[i]; nm = r_nm[i]; b = slash16(ip)
        if (b == "128.117")            key = (nm != "unknown") ? nm : ip
        else if (nm != "unknown")      key = vendor(nm)
        else if (b in block_of)        key = block_of[b]
        else if (known_block(b) != "") key = known_block(b)
        else                           key = "unresolved " b ".x.x"

        mb[key] += r_mb[i]
        seen[key "\t" r_fl[i]] = 1
        addrs[key "\t" ip] = 1
    }

    # Hours are only counted for the flights a destination actually appeared
    # in, so a host captured on some flights and not others is not judged
    # against time it was never observed.
    for (k in seen)  { split(k, p, "\t"); dest_h[p[1]] += hours[p[2]] }
    for (k in addrs) { split(k, p, "\t"); naddr[p[1]]++ }

    for (k in mb) {
        if (mb[k] + 0 < min_mb + 0) { hidden++; hidden_mb += mb[k]; continue }
        label = (naddr[k] > 1) ? k " (" naddr[k] " addrs)" : k
        printf "%.6f\t%s\t%.2f\t%.2f\t%.3f\n", mb[k], label, mb[k],
               dest_h[k], (dest_h[k] > 0 ? mb[k] / dest_h[k] : 0)
        ndest++
    }

    # Trailer, picked apart by the shell below. Collection hours are the sum
    # over flights -- never the sum of the column above, whose rows overlap.
    for (f in flights) { fl = fl (fl ? ", " : "") f; th += hours[f] }
    for (n in dns_reason) reasons = reasons (reasons ? "; " : "") n
    printf "@@\t%d\t%.2f\t%.2f\t%d\t%.2f\t%d\t%d\t%s\t%d\t%s\n",
           nflights, th, total_mb, hidden + 0, hidden_mb + 0, ndest + 0,
           undated + 0, fl, dns_flights + 0, reasons
}' "${summaries[@]}" | sort -t"$(printf '\t')" -k1,1rn > "$TMP/rows"

trailer="$(grep '^@@' "$TMP/rows")"
[ -n "$trailer" ] || die "could not read any flows from the summary files"
nflights=$(printf '%s' "$trailer"  | cut -f2)
total_h=$(printf '%s' "$trailer"   | cut -f3)
total_mb=$(printf '%s' "$trailer"  | cut -f4)
hidden=$(printf '%s' "$trailer"    | cut -f5)
hidden_mb=$(printf '%s' "$trailer" | cut -f6)
ndest=$(printf '%s' "$trailer"     | cut -f7)
undated=$(printf '%s' "$trailer"   | cut -f8)
flight_list=$(printf '%s' "$trailer" | cut -f9)
dns_flights=$(printf '%s' "$trailer" | cut -f10)
dns_reasons=$(printf '%s' "$trailer" | cut -f11)

overall_rate=$(awk -v m="$total_mb" -v h="$total_h" \
    'BEGIN { printf "%.3f", (h > 0 ? m / h : 0) }')

if [ "$scope" = "all" ]; then
    out="$SATCOM_ROOT/satcom-overview.txt"
else
    out="$SATCOM_ROOT/satcom-overview_${scope}.txt"
fi

{
    echo "Satcom off-plane traffic overview"
    echo "Generated:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Flights:    $nflights ($flight_list)"
    printf "Collection: %s hr\n" "$total_h"
    printf "Off-plane:  %s MB\n" "$total_mb"
    printf "Overall:    %s MB/HR   (off-plane / collection)\n" "$overall_rate"
    if [ "${dns_flights:-0}" -gt 0 ]; then
        printf "Hostnames:  %s of %s summaries had no reverse DNS, so some destinations\n" \
            "$dns_flights" "$nflights"
        printf '            show as "unresolved <block>.x.x" -- %s\n' "$dns_reasons"
    fi
    echo
    printf "  %-44s %10s %15s %10s\n" "OFF-PLANE DESTINATION" "MB" "COLLECTION (HR)" "MB/HR"
    grep -v '^@@' "$TMP/rows" \
        | awk -F'\t' '{ printf "  %-44s %10s %15s %10s\n", $2, $3, $4, $5 }'
    printf "  %-44s %10s %15s %10s\n" \
        "$(printf '%.44s' '--------------------------------------------------')" \
        "----------" "---------------" "----------"
    # The total row's hours are the whole collection window, not a column sum:
    # destinations overlap in time, so adding their hours would be meaningless.
    printf "  %-44s %10s %15s %10s\n" "TOTAL (all destinations)" \
        "$total_mb" "$total_h" "$overall_rate"

    if [ "${hidden:-0}" -gt 0 ]; then
        printf "\n  %s of %s destinations shown; %s below %s MB omitted, %s MB between them.\n" \
            "$ndest" "$((ndest + hidden))" "$hidden" "$MIN_MB" "$hidden_mb"
    fi
    if [ "${undated:-0}" -gt 0 ]; then
        printf "  %s flight(s) had no packet timestamps, so contribute 0 hr.\n" "$undated"
    fi
    echo
    echo "  MB comes from the per-flow figures in the summary files, which are"
    echo "  rounded to 0.01 MB each; the flight summaries hold the exact totals."
} > "$out"

cat "$out"
echo
echo "Overview: $out"

#!/bin/bash
#
# Tests for analyze-satcom.sh: which traffic counts as having left the
# aircraft, how capture filenames map to hostnames, and how scopes are
# selected.
#
# Most tests stub mergecap/tshark/dig through the MERGECAP/TSHARK/DIG
# environment variables, so a fixture "capture" is just the src/dst/len TSV
# that tshark would have produced. That keeps them fast and off the network.
# The last test is end to end: it builds a real pcap with text2pcap and runs
# the real mergecap and tshark over it.
#
# Everything happens in a scratch directory - no capture data is touched and
# no DNS query is ever made. Run from anywhere:
#
#     ./testAnalyzeSatcom.sh
#
# Exits 0 if all tests pass, 1 otherwise.

test_dir=$(cd "$(dirname "$0")" && pwd)
satcom_src=$(dirname "$test_dir")	# .../scripts/satcom
script="${satcom_src}/analyze-satcom.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

# assert_eq <description> <actual> <expected>
assert_eq() {
    if [ "$2" = "$3" ]; then pass "$1"; else fail "$1 (got '$2', expected '$3')"; fi
}

# assert_contains <description> <haystack> <needle>
assert_contains() {
    case "$2" in
        *"$3"*) pass "$1" ;;
        *) fail "$1 (expected to find: $3)" ;;
    esac
}

# assert_not_contains <description> <haystack> <needle>
assert_not_contains() {
    case "$2" in
        *"$3"*) fail "$1 (did not expect to find: $3)" ;;
        *) pass "$1" ;;
    esac
}

assert_file() {
    if [ -f "$2" ]; then pass "$1"; else fail "$1 (no such file: $2)"; fi
}

assert_no_file() {
    if [ -f "$2" ]; then fail "$1 (file should not exist: $2)"; else pass "$1"; fi
}

# ------------------------------- Fixtures --------------------------------

tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/testAnalyzeSatcom.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT

stub_bin="${tmp_dir}/bin"
mkdir -p "$stub_bin"

# The real mergecap concatenates pcaps onto stdout. Our fixture captures are
# already the TSV that tshark would emit, so drop the "-w -" flags and cat.
cat > "${stub_bin}/mergecap" <<'STUB'
#!/bin/sh
while [ "$1" = "-w" ] || [ "$1" = "-" ]; do shift; done
cat "$@"
STUB

# The real tshark turns packets into src/dst/len TSV; the fixtures are already
# in that form, so pass stdin through unchanged.
cat > "${stub_bin}/tshark" <<'STUB'
#!/bin/sh
cat
STUB

# Deterministic reverse DNS. Every lookup is logged so a test can prove the
# cache was used instead of the resolver.
cat > "${stub_bin}/dig" <<'STUB'
#!/bin/sh
for a in "$@"; do ip="$a"; done
[ -n "$DIG_LOG" ] && echo "$ip" >> "$DIG_LOG"
case "$ip" in
    8.8.8.8)        echo "dns.google." ;;
    128.117.43.128) echo "eol-hurricane.eol.ucar.edu." ;;
    1.2.3.4)        echo "icmp-peer.example.net." ;;
    223.255.255.255) echo "just-under-multicast.example." ;;
    240.0.0.1)      echo "just-over-multicast.example." ;;
    172.15.0.1)     echo "just-under-rfc1918.example." ;;
    172.32.0.1)     echo "just-over-rfc1918.example." ;;
    128.117.43.224) echo "last-octet-224.ucar.edu." ;;
    *)              ;;                          # no PTR record
esac
STUB

chmod +x "${stub_bin}"/*

export DIG_LOG="${tmp_dir}/dig.log"
: > "$DIG_LOG"

# run_stubbed <args...> - analyze-satcom.sh with the stubs and a private cache.
cache="${tmp_dir}/ptr-cache.tsv"
run_stubbed() {
    MERGECAP="${stub_bin}/mergecap" TSHARK="${stub_bin}/tshark" \
    DIG="${stub_bin}/dig" "$script" --cache "$cache" "$@" 2>&1
}

# make_capture <path> - flow rows arrive on stdin as "src dst bytes [epoch]",
# written out as the TSV the tshark stub replays. A "-" in either address
# field means an empty field, which is what tshark emits for a packet with no
# IPv4 layer. The epoch column is optional; without it rows are stamped one
# second apart from a fixed base, so spans stay deterministic.
# The default base is the filename's own stamp, so a fixture's packets and its
# capture-start time agree without every test having to say so twice.
make_capture() {
    local stamp base
    mkdir -p "$(dirname "$1")"
    stamp=$(basename "$1" | sed -E 's/^(traffic|satcom_)([0-9]{8}_[0-9]{6}).*/\2/')
    base=$(date -u -j -f "%Y%m%d_%H%M%S" "$stamp" "+%s" 2>/dev/null || \
           date -u -d "${stamp:0:4}-${stamp:4:2}-${stamp:6:2} ${stamp:9:2}:${stamp:11:2}:${stamp:13:2}" "+%s" 2>/dev/null)
    awk -v base="${base:-1787000000}" \
        '{ s = ($1 == "-" ? "" : $1); d = ($2 == "-" ? "" : $2)
           t = ($4 == "" ? base + NR - 1 : $4)
           printf "%s\t%s\t%s\t%s\n", s, d, $3, t }' > "$1"
}

# collected <summary> - the Collected: header line.
collected() { awk -F': ' '/^Collected/ { print $2 }' "$1"; }

# flow_mb <summary> <src> <dst> - MB reported for one flow, or "none".
flow_mb() {
    awk -v s="$2" -v d="$3" '
        /^Flows$/      { f = 1; next }
        /^No hostname/ { f = 0 }
        f && $2 == s && $4 == d { print $1; found = 1 }
        END { if (!found) print "none" }' "$1"
}

# total_mb <summary> - the reported off-plane total.
total_mb() { awk '/^Total off-plane/ { print $3 }' "$1"; }

# The count column of a labelled line, e.g. count_col "$sum" responses.
count_col() { grep -E "^  $2 " "$1" | grep -oE '[0-9]+' | head -1; }

# How many queries the DNS section attributes to one name.
dns_name_count() { awk -v n="$2" '$2 == n { print $1 }' "$1"; }

# gateway_mb <summary> <src> <dst> - the Gateway row for one pair, or "none".
# Pass "total" as <src> for the section total. Scoped to the section, so a
# pair that also appears under Flows cannot be mistaken for a gateway row.
gateway_mb() {
    awk -v s="$2" -v d="$3" '
        /^Gateway \(/                            { g = 1; next }
        /^DNS$/ || /^Router syslog$/ || /^Flows$/ { g = 0 }
        g && s == "total" && $2 == "total" { print $1; found = 1; next }
        g && s != "total" && $2 == s && $3 == d { print $1; found = 1 }
        END { if (!found) print "none" }' "$1"
}

# hour_row <summary> "<YYYY-MM-DD HH:00>" -> "SENT RECV TOTAL CUM", or "none".
hour_row() {
    awk -v want="$2" '
        /^By hour/ { h = 1; next }
        /^$/       { if (h) h = 0 }
        h && $1 " " $2 == want { print $3, $4, $5, $6; found = 1; exit }
        END { if (!found) print "none" }' "$1"
}

# hour_mark <summary> "<YYYY-MM-DD HH:00>" -> "partial", "full", or "none".
hour_mark() {
    awk -v want="$2" '
        /^By hour/ { h = 1; next }
        /^$/       { if (h) h = 0 }
        h && $1 " " $2 == want {
            print ($0 ~ /partial/ ? "partial" : "full"); found = 1; exit }
        END { if (!found) print "none" }' "$1"
}

# host_row <summary> <ip> - the Onboard hosts row for one address, or "none".
host_row() {
    awk -v ip="$2" '
        /^Onboard hosts$/ { h = 1; next }
        /^Flows$/         { h = 0 }
        h && $1 == ip { print; found = 1 }
        END { if (!found) print "none" }' "$1"
}

# ------------------------------ The tests --------------------------------

echo "Test 1: only traffic that left the aircraft is counted"
root="${tmp_dir}/t1"
make_capture "${root}/rf01_20260101/traffic20260101_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8         1000000
8.8.8.8         192.168.84.7     500000
192.168.84.2    239.0.0.10      2000000
192.168.84.2    224.0.0.251      100000
192.168.84.7    192.168.84.2    1000000
10.0.0.5        192.168.84.7    1000000
192.168.84.7    255.255.255.255  500000
0.0.0.0         255.255.255.255   10000
-               -                 60000
ROWS
out=$(run_stubbed --root "$root" rf01_20260101)
sum="${root}/rf01_20260101/satcom-summary_rf01_20260101.txt"
assert_eq "off-plane total excludes everything local" "$(total_mb "$sum")" "1.50"
assert_eq "public to onboard is kept" "$(flow_mb "$sum" 8.8.8.8 192.168.84.7)" "0.50"
assert_eq "onboard to public is kept" "$(flow_mb "$sum" 192.168.84.7 8.8.8.8)" "1.00"
assert_eq "multicast 239.x is dropped" "$(flow_mb "$sum" 192.168.84.2 239.0.0.10)" "none"
assert_eq "multicast 224.x is dropped" "$(flow_mb "$sum" 192.168.84.2 224.0.0.251)" "none"
assert_eq "onboard to onboard is dropped" "$(flow_mb "$sum" 192.168.84.7 192.168.84.2)" "none"
assert_eq "other RFC1918 to onboard is dropped" "$(flow_mb "$sum" 10.0.0.5 192.168.84.7)" "none"
assert_eq "broadcast is dropped" "$(flow_mb "$sum" 192.168.84.7 255.255.255.255)" "none"
assert_eq "0.0.0.0 is dropped" "$(flow_mb "$sum" 0.0.0.0 255.255.255.255)" "none"
assert_not_contains "rows with no IPv4 layer are dropped" "$(cat "$sum")" "  60000"

echo "Test 2: classification looks at the first octet only, and at the right boundaries"
root="${tmp_dir}/t2"
make_capture "${root}/rf02_20260102/traffic20260102_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    128.117.43.224  1000000
192.168.84.7    223.255.255.255  500000
192.168.84.7    224.0.0.0        500000
192.168.84.7    239.255.255.255  500000
192.168.84.7    240.0.0.1        500000
192.168.84.7    172.15.0.1       500000
192.168.84.7    172.16.0.1       500000
192.168.84.7    172.31.255.255   500000
192.168.84.7    172.32.0.1       500000
ROWS
out=$(run_stubbed --root "$root" rf02_20260102)
sum="${root}/rf02_20260102/satcom-summary_rf02_20260102.txt"
assert_eq "224 in the last octet is not multicast" \
    "$(flow_mb "$sum" 192.168.84.7 128.117.43.224)" "1.00"
assert_eq "223.255.255.255 is below the multicast range" \
    "$(flow_mb "$sum" 192.168.84.7 223.255.255.255)" "0.50"
assert_eq "224.0.0.0 is the bottom of the multicast range" \
    "$(flow_mb "$sum" 192.168.84.7 224.0.0.0)" "none"
assert_eq "239.255.255.255 is the top of the multicast range" \
    "$(flow_mb "$sum" 192.168.84.7 239.255.255.255)" "none"
assert_eq "240.0.0.1 is above the multicast range" \
    "$(flow_mb "$sum" 192.168.84.7 240.0.0.1)" "0.50"
assert_eq "172.15 is public" "$(flow_mb "$sum" 192.168.84.7 172.15.0.1)" "0.50"
assert_eq "172.16 is private" "$(flow_mb "$sum" 192.168.84.7 172.16.0.1)" "none"
assert_eq "172.31 is private" "$(flow_mb "$sum" 192.168.84.7 172.31.255.255)" "none"
assert_eq "172.32 is public" "$(flow_mb "$sum" 192.168.84.7 172.32.0.1)" "0.50"

echo "Test 3: a packet carrying two IP headers is counted by its outer one"
# tshark comma-joins the field when an ICMP error quotes the packet that
# failed; the first value is the header that was actually on the wire.
root="${tmp_dir}/t3"
make_capture "${root}/rf03_20260103/traffic20260103_120000_brix01.pcap0" <<'ROWS'
192.168.84.7,1.2.3.4    1.2.3.4,192.168.84.7    1000000
ROWS
out=$(run_stubbed --root "$root" rf03_20260103)
sum="${root}/rf03_20260103/satcom-summary_rf03_20260103.txt"
assert_eq "outer header is used" "$(flow_mb "$sum" 192.168.84.7 1.2.3.4)" "1.00"
assert_not_contains "the comma-joined pair is not reported verbatim" \
    "$(cat "$sum")" "192.168.84.7,1.2.3.4"

echo "Test 4: hostnames come from the capture filenames, both conventions"
root="${tmp_dir}/t4"
make_capture "${root}/rf04_20260104/traffic20260104_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
# The Windows captures under applanix/ have no host token in the name.
make_capture "${root}/rf04_20260104/applanix/satcom_20260104_130000.pcap" <<'ROWS'
192.168.84.183  8.8.8.8     500000
ROWS
out=$(run_stubbed --root "$root" rf04_20260104)
sum="${root}/rf04_20260104/satcom-summary_rf04_20260104.txt"
assert_file "linux capture gets an analysis file named for stamp and host" \
    "${root}/rf04_20260104/satcom-analysis_20260104_120000_brix01.txt"
assert_file "windows capture gets an analysis file named for its stamp" \
    "${root}/rf04_20260104/applanix/satcom-analysis_20260104_130000.txt"
assert_contains "host comes from the linux filename" \
    "$(host_row "$sum" 192.168.84.7)" "(brix01)"
assert_contains "host comes from the directory when the name has no host" \
    "$(host_row "$sum" 192.168.84.183)" "(applanix)"
assert_contains "nested captures are included in the flight summary" \
    "$(cat "$sum")" "192.168.84.183 (applanix)"

echo "Test 5: rotation parts are one capture, and totals sum across captures"
root="${tmp_dir}/t5"
# tcpdump -C rotates a single session into .pcap0, .pcap1, ... Both parts
# share the one filename stamp; the later part's packets are an hour after it,
# so the session's collection time has to span both files.
make_capture "${root}/rf05_20260105/traffic20260817_205320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    500000    1787000000
ROWS
make_capture "${root}/rf05_20260105/traffic20260817_205320_brix01.pcap1" <<'ROWS'
192.168.84.7    8.8.8.8    500000    1787003600
ROWS
make_capture "${root}/rf05_20260105/traffic20260817_212320_brix05.pcap0" <<'ROWS'
192.168.84.164  8.8.8.8    1000000   1787001800
ROWS
out=$(run_stubbed --root "$root" rf05_20260105)
sum="${root}/rf05_20260105/satcom-summary_rf05_20260105.txt"
assert_contains "the two rotation parts are one session" "$out" "[2 file(s), host=brix01]"
assert_eq "one analysis file per session, not per part" \
    "$(find "${root}/rf05_20260105" -name 'satcom-analysis*' | wc -l | tr -d ' ')" "2"
assert_eq "rotation parts are summed" "$(flow_mb "$sum" 192.168.84.7 8.8.8.8)" "1.00"
assert_eq "flight total spans both captures" "$(total_mb "$sum")" "2.00"
assert_contains "collection time spans the rotation parts" \
    "$(collected "$sum")" "(>= 1.00 h)"
assert_contains "and reports the window start in UTC" \
    "$(collected "$sum")" "2026-08-17 20:53:20 to 2026-08-17 21:53:20 UTC"
assert_contains "and notes how many captures it covers" \
    "$(collected "$sum")" "spanning 2 captures"

echo "Test 5b: the start comes from the filename, not the first packet"
root="${tmp_dir}/t5b"
# The link was silent for the first hour: tcpdump started at 20:53:20 but the
# first off-plane packet is not until 21:53:20. The filename must win.
make_capture "${root}/rf05_20260105/traffic20260817_205320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    500000    1787003600
192.168.84.7    8.8.8.8    500000    1787007200
ROWS
out=$(run_stubbed --root "$root" rf05_20260105)
sum="${root}/rf05_20260105/satcom-summary_rf05_20260105.txt"
assert_contains "the quiet hour before the first packet is counted" \
    "$(collected "$sum")" "(>= 2.00 h)"
assert_contains "so the window starts at the capture's filename stamp" \
    "$(collected "$sum")" "2026-08-17 20:53:20 to 2026-08-17 22:53:20 UTC"
assert_not_contains "and a single capture needs no caption" \
    "$(collected "$sum")" "spanning"

echo "Test 5c: a first packet earlier than the filename stamp still wins"
root="${tmp_dir}/t5c"
# Clock skew: never claim a start after traffic was already flowing.
make_capture "${root}/rf05_20260105/traffic20260817_205320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    500000    1786996400
192.168.84.7    8.8.8.8    500000    1787000000
ROWS
out=$(run_stubbed --root "$root" rf05_20260105)
sum="${root}/rf05_20260105/satcom-summary_rf05_20260105.txt"
assert_contains "the earlier packet time is used as the start" \
    "$(collected "$sum")" "2026-08-17 19:53:20 to 2026-08-17 20:53:20 UTC"

echo "Test 6: megabytes are rounded once at the end, not per capture"
root="${tmp_dir}/t6"
# 4000 bytes rounds to 0.00 MB on its own; the two together are 0.01 MB.
make_capture "${root}/rf06_20260106/traffic20260106_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    4000
ROWS
make_capture "${root}/rf06_20260106/traffic20260106_140000_brix05.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    4000
ROWS
out=$(run_stubbed --root "$root" rf06_20260106)
sum="${root}/rf06_20260106/satcom-summary_rf06_20260106.txt"
assert_eq "raw bytes are summed before rounding" \
    "$(flow_mb "$sum" 192.168.84.7 8.8.8.8)" "0.01"

echo "Test 7: names resolve on a first run, when the cache file is empty"
# Regression: the two-file awk idiom silently inverted on an empty cache and
# reported every public address as unknown.
root="${tmp_dir}/t7"
cache="${tmp_dir}/empty-cache.tsv"
: > "$cache"					# exists, zero length
make_capture "${root}/rf07_20260107/traffic20260107_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
out=$(run_stubbed --root "$root" rf07_20260107)
sum="${root}/rf07_20260107/satcom-summary_rf07_20260107.txt"
assert_contains "public address resolves against an empty cache" \
    "$(cat "$sum")" "8.8.8.8 (dns.google)"
assert_not_contains "and is not reported as unknown" "$(cat "$sum")" "8.8.8.8 (unknown)"
assert_contains "the answer is written to the cache" "$(cat "$cache")" "dns.google"

echo "Test 8: a cached answer is reused instead of re-queried"
: > "$DIG_LOG"
out=$(run_stubbed --root "$root" rf07_20260107)
assert_eq "the resolver was not called again" "$(wc -l < "$DIG_LOG" | tr -d ' ')" "0"
assert_contains "the cached name is still reported" \
    "$(cat "$sum")" "8.8.8.8 (dns.google)"

echo "Test 9: --no-dns reports addresses without querying"
root="${tmp_dir}/t9"
cache="${tmp_dir}/nodns-cache.tsv"
: > "$DIG_LOG"
make_capture "${root}/rf09_20260109/traffic20260109_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
out=$(run_stubbed --root "$root" rf09_20260109 --no-dns)
sum="${root}/rf09_20260109/satcom-summary_rf09_20260109.txt"
assert_eq "the resolver was never called" "$(wc -l < "$DIG_LOG" | tr -d ' ')" "0"
assert_contains "the address is reported as unknown" "$(cat "$sum")" "8.8.8.8 (unknown)"
assert_contains "onboard hostnames still work without DNS" \
    "$(cat "$sum")" "192.168.84.7 (brix01)"

echo "Test 9b: a missing resolver is explained rather than left a mystery"
root="${tmp_dir}/t9b"
cache="${tmp_dir}/t9b-cache.tsv"
: > "$DIG_LOG"
make_capture "${root}/rf09_20260109/traffic20260817_205320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
# DIG points at something that does not exist, as on a host without bind-utils.
out=$(MERGECAP="${stub_bin}/mergecap" TSHARK="${stub_bin}/tshark" \
      DIG="${tmp_dir}/nonexistent-dig" "$script" --cache "$cache" \
      --root "$root" rf09_20260109 2>&1)
sum="${root}/rf09_20260109/satcom-summary_rf09_20260109.txt"
assert_contains "the summary says why the names are missing" "$(cat "$sum")" \
    "Hostnames: ${tmp_dir}/nonexistent-dig not found, so no lookups were made"
assert_contains "the addresses are still reported as unknown" \
    "$(cat "$sum")" "8.8.8.8 (unknown)"
# Caching "unknown" here would outlive the missing resolver and keep the names
# wrong even once it was installed.
assert_eq "and nothing is written to the cache" \
    "$([ -s "$cache" ] && echo nonempty || echo empty)" "empty"

echo "Test 9c: --no-dns says so too, and a working resolver says nothing"
root="${tmp_dir}/t9c"
cache="${tmp_dir}/t9c-cache.tsv"
make_capture "${root}/rf09_20260109/traffic20260817_205320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
out=$(run_stubbed --root "$root" rf09_20260109 --no-dns)
sum="${root}/rf09_20260109/satcom-summary_rf09_20260109.txt"
assert_contains "opting out is recorded in the summary" "$(cat "$sum")" \
    "Hostnames: lookups skipped (--no-dns)"
out=$(run_stubbed --root "$root" rf09_20260109)
assert_not_contains "but a working resolver adds no note" "$(cat "$sum")" "Hostnames:"
assert_contains "and resolves the name" "$(cat "$sum")" "8.8.8.8 (dns.google)"

echo "Test 10: an address with no PTR record is reported, not hidden"
root="${tmp_dir}/t10"
cache="${tmp_dir}/noptr-cache.tsv"
make_capture "${root}/rf10_20260110/traffic20260110_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    151.101.17.91    1000000
ROWS
out=$(run_stubbed --root "$root" rf10_20260110)
sum="${root}/rf10_20260110/satcom-summary_rf10_20260110.txt"
assert_contains "the flow is still counted" "$(cat "$sum")" "151.101.17.91 (unknown)"
assert_contains "and it is listed as unresolved" "$(cat "$sum")" "No hostname found for 1 IP(s)"

echo "Test 11: a capture with nothing off-plane yields an empty analysis file"
root="${tmp_dir}/t11"
cache="${tmp_dir}/t11-cache.tsv"
# adslap6 saw only multicast, over the two hours before brix01's traffic.
make_capture "${root}/rf11_20260111/traffic20260817_205320_adslap6.pcap0" <<'ROWS'
192.168.84.160  239.0.0.10    2000000   1787000000
192.168.84.160  239.0.0.10    2000000   1787007200
ROWS
make_capture "${root}/rf11_20260111/traffic20260817_231320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8       1000000   1787010800
ROWS
out=$(run_stubbed --root "$root" rf11_20260111)
sum="${root}/rf11_20260111/satcom-summary_rf11_20260111.txt"
empty="${root}/rf11_20260111/satcom-analysis_20260817_205320_adslap6.txt"
assert_file "the analysis file is still written" "$empty"
assert_eq "it is empty" "$(wc -c < "$empty" | tr -d ' ')" "0"
assert_eq "the host contributes nothing to the total" "$(total_mb "$sum")" "1.00"
assert_eq "and does not appear as an onboard host" "$(host_row "$sum" 192.168.84.160)" "none"
assert_contains "but the capture is still counted" "$out" "host=adslap6"
# Collection time is how long the captures ran, not when off-plane traffic
# happened, so a capture that recorded only local traffic still counts.
assert_contains "a local-only capture still extends the collection window" \
    "$(collected "$sum")" "(>= 3.00 h)"

echo "Test 11b: a capture with no packets still reports when it started"
# This is what a quiet host looks like once the capture filter is live: an
# empty file. Reporting its start is what separates it from a dead capture.
root="${tmp_dir}/t11b"
cache="${tmp_dir}/t11b-cache.tsv"
make_capture "${root}/rf11_20260111/traffic20260817_205320_brix01.pcap0" < /dev/null
out=$(run_stubbed --root "$root" rf11_20260111)
sum="${root}/rf11_20260111/satcom-summary_rf11_20260111.txt"
assert_contains "the start is still known, from the filename" \
    "$(collected "$sum")" "from 2026-08-17 20:53:20 UTC"
assert_contains "and the unknown end is stated rather than guessed" \
    "$(collected "$sum")" "no packets captured; end unknown"
assert_eq "and the total is zero" "$(total_mb "$sum")" "0.00"

echo "Test 12: scopes - all flights, one flight, one file, one date stamp"
root="${tmp_dir}/t12"
cache="${tmp_dir}/t12-cache.tsv"
make_capture "${root}/rf12_20260112/traffic20260112_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
make_capture "${root}/rf13_20260113/traffic20260113_120000_brix05.pcap0" <<'ROWS'
192.168.84.164  8.8.8.8    500000
ROWS
# Maintenance captures must never be swept up by the rf* default.
make_capture "${root}/maint_days/traffic20260114_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
out=$(run_stubbed --root "$root")
assert_file "every rf* flight is summarized" \
    "${root}/rf12_20260112/satcom-summary_rf12_20260112.txt"
assert_file "including the second flight" \
    "${root}/rf13_20260113/satcom-summary_rf13_20260113.txt"
assert_no_file "maint_days is left alone" \
    "${root}/maint_days/satcom-analysis_20260114_120000_brix01.txt"

rm -f "${root}"/rf12_20260112/satcom-*
out=$(run_stubbed --root "$root" rf12_20260112)
assert_file "a single flight can be named" \
    "${root}/rf12_20260112/satcom-summary_rf12_20260112.txt"
assert_no_file "and the other flight is not touched" \
    "${root}/rf13_20260113/satcom-analysis_20260113_120000_brix05.txt.absent"

rm -f "${root}"/rf12_20260112/satcom-*
out=$(run_stubbed "${root}/rf12_20260112/traffic20260112_120000_brix01.pcap0")
assert_file "a single capture file can be named" \
    "${root}/rf12_20260112/satcom-summary_20260112_120000_brix01.txt"

rm -f "${root}"/rf12_20260112/satcom-*
out=$(run_stubbed --root "$root" 20260112_120000)
assert_file "a capture can be named by its date stamp" \
    "${root}/rf12_20260112/satcom-summary_20260112_120000_brix01.txt"
assert_contains "an unmatched date stamp is an error" \
    "$(run_stubbed --root "$root" 20991231_000000)" "no captures matching"

echo "Test 13: --skip-existing leaves analysis files alone but still summarizes"
root="${tmp_dir}/t13"
cache="${tmp_dir}/t13-cache.tsv"
make_capture "${root}/rf14_20260115/traffic20260115_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
analysis="${root}/rf14_20260115/satcom-analysis_20260115_120000_brix01.txt"
echo "PLACEHOLDER FROM AN EARLIER RUN" > "$analysis"
out=$(run_stubbed --root "$root" rf14_20260115 --skip-existing)
assert_contains "the existing file is reported as skipped" "$out" "skip (exists)"
assert_eq "and its contents are untouched" "$(cat "$analysis")" "PLACEHOLDER FROM AN EARLIER RUN"
assert_file "the summary is still written" \
    "${root}/rf14_20260115/satcom-summary_rf14_20260115.txt"
assert_eq "and is built from the capture, not the stale file" \
    "$(total_mb "${root}/rf14_20260115/satcom-summary_rf14_20260115.txt")" "1.00"

echo "Test 14: end to end over a real pcap, with the real mergecap and tshark"
if ! command -v text2pcap >/dev/null 2>&1 || ! command -v tshark >/dev/null 2>&1 \
   || ! command -v editcap >/dev/null 2>&1; then
    echo "  SKIP: text2pcap/tshark/editcap not installed"
else
    root="${tmp_dir}/t14"
    cache="${tmp_dir}/t14-cache.tsv"
    mkdir -p "${root}/rf15_20260116"

    # Full 1000-byte raw-IP packets, truncated afterwards with editcap -s 96
    # the way the real captures are. A pcap record carries both the captured
    # length and the original length on the wire; tcpdump -s 96 stores only 96
    # bytes but still records the true length, and that is what frame.len
    # reports. A short packet merely claiming a large ip.len would not model
    # this -- its recorded wire length would be short too, and frame.len would
    # read that short value.
    zero16="00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    e2e_mid=$(off=32
              while [ "$off" -lt 992 ]; do
                  printf '%06x  %s\n' "$off" "$zero16"
                  off=$((off + 16))
              done)
    emit_packets() {			# emit_packets <count> <src hex> <dst hex>
        local n=$1 s=$2 d=$3 i=0
        while [ "$i" -lt "$n" ]; do
            printf '000000  45 00 03 e8 00 00 00 00 40 11 00 00 %s\n' "$s"
            printf '000010  %s 00 00 00 00 00 00 00 00 00 00 00 00\n' "$d"
            printf '%s\n' "$e2e_mid"
            printf '0003e0  00 00 00 00 00 00 00 00\n'
            i=$((i + 1))
        done
    }
    {
        emit_packets 1000 "c0 a8 54 07" "80 75 2b 80"   # brix01 -> eol-hurricane, 1.00 MB
        emit_packets  500 "80 75 2b 80" "c0 a8 54 07"   # eol-hurricane -> brix01, 0.50 MB
        emit_packets 2000 "c0 a8 54 02" "ef 00 00 0a"   # NIDAS multicast,        2.00 MB
        emit_packets 1000 "c0 a8 54 02" "c0 a8 54 07"   # onboard to onboard,     1.00 MB
        emit_packets  500 "c0 a8 54 07" "ff ff ff ff"   # broadcast,              0.50 MB
    } > "${tmp_dir}/fixture.hex"
    # text2pcap stamps the packets with the time of conversion, so name the
    # capture for now as well to keep filename and packets consistent.
    e2e_stamp=$(date -u '+%Y%m%d_%H%M%S')
    text2pcap -q -l 101 "${tmp_dir}/fixture.hex" \
        "${tmp_dir}/fixture-full.pcap" 2>/dev/null
    editcap -s 96 "${tmp_dir}/fixture-full.pcap" \
        "${root}/rf15_20260116/traffic${e2e_stamp}_brix01.pcap0" 2>/dev/null

    # Real mergecap and tshark; only the resolver stays stubbed.
    out=$(DIG="${stub_bin}/dig" "$script" --cache "$cache" \
          --root "$root" rf15_20260116 2>&1)
    sum="${root}/rf15_20260116/satcom-summary_rf15_20260116.txt"

    assert_file "the summary is produced from a real pcap" "$sum"
    assert_eq "5.00 MB on the wire becomes 1.50 MB off-plane" "$(total_mb "$sum")" "1.50"
    assert_eq "outbound flow is measured" \
        "$(flow_mb "$sum" 192.168.84.7 128.117.43.128)" "1.00"
    assert_eq "inbound flow is measured" \
        "$(flow_mb "$sum" 128.117.43.128 192.168.84.7)" "0.50"
    assert_eq "the NIDAS multicast stream is excluded" \
        "$(flow_mb "$sum" 192.168.84.2 239.0.0.10)" "none"
    assert_eq "onboard to onboard is excluded" \
        "$(flow_mb "$sum" 192.168.84.2 192.168.84.7)" "none"
    assert_eq "broadcast is excluded" \
        "$(flow_mb "$sum" 192.168.84.7 255.255.255.255)" "none"
    assert_contains "the onboard host is named from the filename" \
        "$(cat "$sum")" "192.168.84.7 (brix01)"
    assert_contains "the far end is named from reverse DNS" \
        "$(cat "$sum")" "128.117.43.128 (eol-hurricane.eol.ucar.edu)"
    assert_contains "the per-capture analysis file keeps the original format" \
        "$(cat "${root}/rf15_20260116/satcom-analysis_${e2e_stamp}_brix01.txt")" \
        "192.168.84.7 => 128.117.43.128: 1.00 MB"
    # The duration here is whatever text2pcap stamped, so assert the shape of
    # the line rather than a number this fixture does not control.
    assert_contains "collection time is reported from the real timestamps" \
        "$(collected "$sum")" " UTC (>= "
    assert_not_contains "and is not left unknown" "$(collected "$sum")" "unknown"
fi

echo "Test 15: a missing tshark names the install command for this platform"
# uname and the package managers are all PATH lookups, so the platform dispatch
# can be exercised without the script knowing it is under test.
hintdir="${tmp_dir}/hint"
mkdir -p "$hintdir"
hint_for() {                    # hint_for <uname output> [package manager...]
    local os="$1" pm
    shift
    rm -f "$hintdir"/*
    printf '#!/bin/sh\necho %s\n' "$os" > "$hintdir/uname"
    for pm in "$@"; do printf '#!/bin/sh\nexit 0\n' > "$hintdir/$pm"; done
    chmod +x "$hintdir"/*
    PATH="$hintdir:$PATH" TSHARK=/nonexistent/tshark "$script" 2>&1 | sed -n 's/.*try: //p'
}
assert_eq "macOS is pointed at brew" "$(hint_for Darwin)" "brew install wireshark"
assert_eq "a dnf machine is pointed at wireshark-cli" \
    "$(hint_for Linux dnf)" "sudo dnf install wireshark-cli"
assert_eq "an unrecognized OS gets a generic hint" \
    "$(hint_for Plan9)" "install the wireshark command-line tools"
assert_contains "and the message says which tool is missing" \
    "$(PATH="$hintdir:$PATH" TSHARK=/nonexistent/tshark "$script" 2>&1)" \
    "/nonexistent/tshark not found"

echo "Test 16: --help works before wireshark is installed"
# Someone setting up a new machine reads --help before they have tshark.
out=$(TSHARK=/nonexistent/tshark MERGECAP=/nonexistent/mergecap "$script" --help 2>&1)
assert_contains "the usage is printed" "$out" "Summarize satcom traffic"
assert_not_contains "and no missing-tool error is raised" "$out" "not found"
assert_eq "exiting successfully" \
    "$(TSHARK=/nonexistent/tshark "$script" --help >/dev/null 2>&1; echo $?)" "0"

echo "Test 17: onboard DNS is reported without disturbing the off-plane totals"
if ! command -v text2pcap >/dev/null 2>&1 || ! command -v tshark >/dev/null 2>&1; then
    echo "  SKIP: text2pcap/tshark not installed"
else
    root="${tmp_dir}/t17"
    mkdir -p "${root}/rf17_20260117"

    # Real UDP/53 packets carrying a DNS message for "a.b", so tshark dissects
    # them and fills dns.flags.response -- the field the summary counts on.
    # Three queries and two answers: the third is unanswered, which is the
    # case worth reporting, since a timeout costs the lookup again on retry.
    dns_query() {
        printf '000000  45 00 00 31 00 00 00 00 40 11 00 00 c0 a8 54 02\n'
        printf '000010  c0 a8 54 01 c3 50 00 35 00 1d 00 00 12 34 01 00\n'
        printf '000020  00 01 00 00 00 00 00 00 01 61 01 62 00 00 01 00\n'
        printf '000030  01\n'
    }
    dns_reply() {
        printf '000000  45 00 00 41 00 00 00 00 40 11 00 00 c0 a8 54 01\n'
        printf '000010  c0 a8 54 02 00 35 c3 50 00 2d 00 00 12 34 81 80\n'
        printf '000020  00 01 00 01 00 00 00 00 01 61 01 62 00 00 01 00\n'
        printf '000030  01 c0 0c 00 01 00 01 00 00 00 3c 00 04 01 02 03\n'
        printf '000040  04\n'
    }
    {
        dns_query; dns_reply
        dns_query; dns_reply
        dns_query                       # no answer for this one
        # one off-plane packet, so the flow section has something of its own
        printf '000000  45 00 00 20 00 00 00 00 40 11 00 00 c0 a8 54 02\n'
        printf '000010  80 75 2b 80 13 88 0f a0 00 0c 00 00 00 00 00 00\n'
    } > "${tmp_dir}/t17.hex"
    t17_stamp=$(date -u '+%Y%m%d_%H%M%S')
    text2pcap -q -l 101 "${tmp_dir}/t17.hex" \
        "${root}/rf17_20260117/traffic${t17_stamp}_acserver.pcap0" 2>/dev/null

    out=$("$script" --no-dns --root "$root" rf17_20260117 2>&1)
    sum="${root}/rf17_20260117/satcom-summary_rf17_20260117.txt"

    assert_eq "queries to the onboard resolver are counted" \
        "$(count_col "$sum" "queries to resolver")" "3"
    assert_eq "responses are counted separately" \
        "$(count_col "$sum" "responses")" "2"
    assert_eq "the query that got no answer is reported" \
        "$(count_col "$sum" "unanswered")" "1"
    assert_eq "a name is counted once per query, not once per packet" \
        "$(dns_name_count "$sum" a.b)" "3"
    assert_eq "onboard DNS stays out of the off-plane flows" \
        "$(flow_mb "$sum" 192.168.84.2 192.168.84.1)" "none"
    assert_contains "the off-plane flow is still reported" \
        "$(cat "$sum")" "128.117.43.128"
fi

echo "Test 17b: a capture with no DNS omits the section entirely"
root="${tmp_dir}/t17b"
make_capture "${root}/rf18_20260118/traffic20260118_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
out=$(run_stubbed --root "$root" rf18_20260118)
sum="${root}/rf18_20260118/satcom-summary_rf18_20260118.txt"
assert_not_contains "no DNS heading when nothing was captured" "$(cat "$sum")" "queries to resolver"
assert_eq "and the flow totals are unaffected" "$(total_mb "$sum")" "1.00"

echo "Test 18: the router's syslog is kept verbatim and summarized"
if ! command -v text2pcap >/dev/null 2>&1 || ! command -v tshark >/dev/null 2>&1; then
    echo "  SKIP: text2pcap/tshark not installed"
else
    root="${tmp_dir}/t18"
    mkdir -p "${root}/rf19_20260119"

    # A real datagram from the router: UDP/514 carrying
    #   <134>Jan  1 00:00:00 rafgv k: DENY SRC=192.168.84.36
    # so tshark dissects it as syslog and fills syslog.msg with the body.
    # Nothing asserts on the message text beyond it surviving intact -- the
    # format belongs to the router, and the script deliberately does not parse it.
    syslog_packet() {
        printf '000000  45 00 00 50 00 00 00 00 40 11 00 00 c0 a8 54 01\n'
        printf '000010  c0 a8 54 02 02 02 02 02 00 3c 00 00 3c 31 33 34\n'
        printf '000020  3e 4a 61 6e 20 20 31 20 30 30 3a 30 30 3a 30 30\n'
        printf '000030  20 72 61 66 67 76 20 6b 3a 20 44 45 4e 59 20 53\n'
        printf '000040  52 43 3d 31 39 32 2e 31 36 38 2e 38 34 2e 33 36\n'
    }
    {
        syslog_packet
        syslog_packet
        printf '000000  45 00 00 20 00 00 00 00 40 11 00 00 c0 a8 54 02\n'
        printf '000010  80 75 2b 80 13 88 0f a0 00 0c 00 00 00 00 00 00\n'
    } > "${tmp_dir}/t18.hex"
    t18_stamp=$(date -u '+%Y%m%d_%H%M%S')
    text2pcap -q -l 101 "${tmp_dir}/t18.hex" \
        "${root}/rf19_20260119/traffic${t18_stamp}_acserver.pcap0" 2>/dev/null

    out=$("$script" --no-dns --root "$root" rf19_20260119 2>&1)
    sum="${root}/rf19_20260119/satcom-summary_rf19_20260119.txt"
    slog="${root}/rf19_20260119/satcom-syslog_rf19_20260119.txt"

    assert_file "the messages are written beside the summary" "$slog"
    assert_contains "verbatim, so the format can be read later" \
        "$(cat "$slog")" "DENY SRC=192.168.84.36"
    assert_eq "the summary counts them" "$(count_col "$sum" messages)" "2"
    assert_contains "and reports the onboard address mentioned" \
        "$(cat "$sum")" "2  192.168.84.36"
    assert_eq "syslog stays out of the off-plane flows" \
        "$(flow_mb "$sum" 192.168.84.1 192.168.84.2)" "none"
    assert_contains "the companion file is named on the console" "$out" "syslog:"
fi

echo "Test 18b: a capture with no syslog omits the section and writes no file"
root="${tmp_dir}/t18b"
make_capture "${root}/rf21_20260121/traffic20260121_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1000000
ROWS
out=$(run_stubbed --root "$root" rf21_20260121)
sum="${root}/rf21_20260121/satcom-summary_rf21_20260121.txt"
assert_not_contains "no syslog heading" "$(cat "$sum")" "Router syslog"
assert_no_file "and no empty companion file" \
    "${root}/rf21_20260121/satcom-syslog_rf21_20260121.txt"

echo "Test 19: gateway traffic is reported on its own, outside the flow totals"
root="${tmp_dir}/t19"
make_capture "${root}/rf22_20260122/traffic20260122_120000_acserver.pcap0" <<'ROWS'
192.168.84.1    192.168.84.2      100000
192.168.84.2    192.168.84.1       50000
192.168.84.2    192.168.84.7      100000
192.168.84.2    128.117.43.124    200000
ROWS
run_stubbed --root "$root" rf22_20260122 >/dev/null
sum="${root}/rf22_20260122/satcom-summary_rf22_20260122.txt"

assert_eq "traffic from the gateway is reported" \
    "$(gateway_mb "$sum" 192.168.84.1 192.168.84.2)" "0.10"
assert_eq "and traffic to it" \
    "$(gateway_mb "$sum" 192.168.84.2 192.168.84.1)" "0.05"
assert_eq "the section totals both directions" \
    "$(gateway_mb "$sum" total)" "0.15"
assert_eq "onboard traffic that misses the gateway is not in the section" \
    "$(gateway_mb "$sum" 192.168.84.2 192.168.84.7)" "none"
assert_eq "the gateway stays out of the off-plane flows" \
    "$(flow_mb "$sum" 192.168.84.1 192.168.84.2)" "none"
assert_eq "so the off-plane total counts only what crossed satcom" \
    "$(total_mb "$sum")" "0.20"

echo "Test 19b: a capture with no gateway traffic omits the section"
root="${tmp_dir}/t19b"
make_capture "${root}/rf23_20260123/traffic20260123_000000_brix01.pcap0" <<'ROWS'
192.168.84.7    128.117.43.124    5000000
ROWS
run_stubbed --root "$root" rf23_20260123 >/dev/null
sum="${root}/rf23_20260123/satcom-summary_rf23_20260123.txt"
assert_not_contains "no Gateway heading" "$(cat "$sum")" "Gateway ("
assert_eq "and the flow totals are unaffected" "$(total_mb "$sum")" "5.00"

echo "Test 19c: the gateway address is configurable"
root="${tmp_dir}/t19c"
make_capture "${root}/rf25_20260125/traffic20260125_120000_acserver.pcap0" <<'ROWS'
10.1.1.1    10.1.1.50    400000
ROWS
SATCOM_GATEWAY=10.1.1.1 run_stubbed --root "$root" rf25_20260125 >/dev/null
sum="${root}/rf25_20260125/satcom-summary_rf25_20260125.txt"
assert_eq "a gateway given in the environment is the one reported" \
    "$(gateway_mb "$sum" 10.1.1.1 10.1.1.50)" "0.40"

echo "Test 20: a syslog message quoted back in an ICMP error is counted once"
if ! command -v text2pcap >/dev/null 2>&1 || ! command -v tshark >/dev/null 2>&1; then
    echo "  SKIP: text2pcap/tshark not installed"
else
    root="${tmp_dir}/t20"
    mkdir -p "${root}/rf24_20260124"

    # The real datagram, then the port unreachable acserver sends back because
    # nothing listens on 514. The error quotes the datagram whole, so tshark
    # dissects the same message twice and the count doubles unless the ICMP
    # copy is skipped. This is what RF17 looked like: 372 reported, 186 real.
    {
        printf '000000  45 00 00 50 00 00 00 00 40 11 00 00 c0 a8 54 01\n'
        printf '000010  c0 a8 54 02 02 02 02 02 00 3c 00 00 3c 31 33 34\n'
        printf '000020  3e 4a 61 6e 20 20 31 20 30 30 3a 30 30 3a 30 30\n'
        printf '000030  20 72 61 66 67 76 20 6b 3a 20 44 45 4e 59 20 53\n'
        printf '000040  52 43 3d 31 39 32 2e 31 36 38 2e 38 34 2e 33 36\n'

        printf '000000  45 00 00 6c 00 00 00 00 40 01 00 00 c0 a8 54 02\n'
        printf '000010  c0 a8 54 01 03 03 00 00 00 00 00 00 45 00 00 50\n'
        printf '000020  00 00 00 00 40 11 00 00 c0 a8 54 01 c0 a8 54 02\n'
        printf '000030  02 02 02 02 00 3c 00 00 3c 31 33 34 3e 4a 61 6e\n'
        printf '000040  20 20 31 20 30 30 3a 30 30 3a 30 30 20 72 61 66\n'
        printf '000050  67 76 20 6b 3a 20 44 45 4e 59 20 53 52 43 3d 31\n'
        printf '000060  39 32 2e 31 36 38 2e 38 34 2e 33 36\n'
    } > "${tmp_dir}/t20.hex"
    t20_stamp=$(date -u '+%Y%m%d_%H%M%S')
    text2pcap -q -l 101 "${tmp_dir}/t20.hex" \
        "${root}/rf24_20260124/traffic${t20_stamp}_acserver.pcap0" 2>/dev/null

    "$script" --no-dns --root "$root" rf24_20260124 >/dev/null 2>&1
    sum="${root}/rf24_20260124/satcom-summary_rf24_20260124.txt"
    slog="${root}/rf24_20260124/satcom-syslog_rf24_20260124.txt"

    assert_eq "the message is counted once, not once per dissection" \
        "$(count_col "$sum" messages)" "1"
    assert_eq "and written once to the companion file" \
        "$(wc -l < "$slog" | tr -d ' ')" "1"
    assert_contains "the message itself is unchanged" \
        "$(cat "$slog")" "DENY SRC=192.168.84.36"
fi

echo "Test 21: an allowlist keeps router-blocked traffic out of the total"
root="${tmp_dir}/t21"
make_capture "${root}/rf26_20260126/traffic20260126_120000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    3000000
192.168.84.7      128.117.43.124    1000000
192.168.84.164    151.101.1.1        500000
ROWS
SATCOM_ALLOWED=192.168.84.2,192.168.84.7 \
    run_stubbed --root "$root" rf26_20260126 >/dev/null
sum="${root}/rf26_20260126/satcom-summary_rf26_20260126.txt"

assert_eq "the total counts only what the router lets out" \
    "$(total_mb "$sum")" "4.00"
assert_contains "the blocked bytes are stated, not discarded" \
    "$(cat "$sum")" "Blocked at router: 0.50 MB"
assert_contains "and attributed to the host that sent them" \
    "$(cat "$sum")" "0.50  192.168.84.164"
assert_eq "a blocked host is not in the off-plane flows" \
    "$(flow_mb "$sum" 192.168.84.164 151.101.1.1)" "none"
assert_eq "an allowed host still is" \
    "$(flow_mb "$sum" 192.168.84.2 128.117.43.124)" "3.00"

echo "Test 21b: with no allowlist the totals are unchanged"
root="${tmp_dir}/t21b"
make_capture "${root}/rf27_20260127/traffic20260127_120000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    3000000
192.168.84.164    151.101.1.1        500000
ROWS
run_stubbed --root "$root" rf27_20260127 >/dev/null
sum="${root}/rf27_20260127/satcom-summary_rf27_20260127.txt"
assert_eq "every onboard host counts toward the total" \
    "$(total_mb "$sum")" "3.50"
assert_not_contains "and nothing is reported as blocked" \
    "$(cat "$sum")" "Blocked at router"

echo "Test 22: off-plane traffic is bucketed into the UTC hour it crossed in"
# 1767227400 is 2026-01-01 00:30:00 UTC, 1767229200 is 01:00:00, and
# 1767233400 is 02:10:00 -- chosen so the buckets are unambiguous.
root="${tmp_dir}/t22"
make_capture "${root}/rf28_20260128/traffic20260128_000000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    1000000    1767227400
128.117.43.124    192.168.84.2      3000000    1767227400
192.168.84.2      128.117.43.124    2000000    1767229200
128.117.43.124    192.168.84.2      4000000    1767233400
ROWS
run_stubbed --root "$root" rf28_20260128 >/dev/null
sum="${root}/rf28_20260128/satcom-summary_rf28_20260128.txt"

assert_eq "the first hour splits sent from received" \
    "$(hour_row "$sum" "2026-01-01 00:00")" "1.00 3.00 4.00 4.00"
assert_eq "the second carries only what moved in it, and accumulates" \
    "$(hour_row "$sum" "2026-01-01 01:00")" "2.00 0.00 2.00 6.00"
assert_eq "and the third likewise" \
    "$(hour_row "$sum" "2026-01-01 02:00")" "0.00 4.00 4.00 10.00"
assert_eq "the running total ends at the off-plane total" \
    "$(total_mb "$sum")" "10.00"

echo "Test 22b: the hourly figures honour the allowlist"
root="${tmp_dir}/t22b"
make_capture "${root}/rf29_20260129/traffic20260129_000000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    1000000    1767227400
192.168.84.164    151.101.1.1        500000    1767227400
ROWS
SATCOM_ALLOWED=192.168.84.2 run_stubbed --root "$root" rf29_20260129 >/dev/null
sum="${root}/rf29_20260129/satcom-summary_rf29_20260129.txt"
assert_eq "a blocked host's bytes are not in the hour" \
    "$(hour_row "$sum" "2026-01-01 00:00")" "1.00 0.00 1.00 1.00"
assert_eq "matching the total, so the two can be compared" \
    "$(total_mb "$sum")" "1.00"

echo "Test 22c: the partial hours at each end are marked, the rest are not"
# Packets at 00:30, 01:30 and 02:30, so the capture window starts and ends
# inside an hour at each end but covers the middle one completely.
root="${tmp_dir}/t22c"
make_capture "${root}/rf30_20260130/traffic20260130_000000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    1000000    1767227400
192.168.84.2      128.117.43.124    1000000    1767231000
192.168.84.2      128.117.43.124    1000000    1767234600
ROWS
run_stubbed --root "$root" rf30_20260130 >/dev/null
sum="${root}/rf30_20260130/satcom-summary_rf30_20260130.txt"
assert_eq "the first hour is partial, the capture having started inside it" \
    "$(hour_mark "$sum" "2026-01-01 00:00")" "partial"
assert_eq "the middle hour is whole" \
    "$(hour_mark "$sum" "2026-01-01 01:00")" "full"
assert_eq "and the last is partial too" \
    "$(hour_mark "$sum" "2026-01-01 02:00")" "partial"

echo "Test 22d: one flight's hours never leak into another's summary"
# Everything a scope accumulates lives in one shared $TMP, so a run covering
# several flights has to empty it between them. Missing one file is invisible
# in a single-flight run and silently sums every flight in a multi-flight one.
root="${tmp_dir}/t22d"
make_capture "${root}/rf31_20260131/traffic20260131_000000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    1000000    1767227400
ROWS
make_capture "${root}/rf32_20260201/traffic20260201_000000_acserver.pcap0" <<'ROWS'
192.168.84.2      128.117.43.124    5000000    1769905800
ROWS
run_stubbed --root "$root" >/dev/null       # no target: both flights, one run
sum1="${root}/rf31_20260131/satcom-summary_rf31_20260131.txt"
sum2="${root}/rf32_20260201/satcom-summary_rf32_20260201.txt"

assert_eq "the first flight reports its own hour" \
    "$(hour_row "$sum1" "2026-01-01 00:00")" "1.00 0.00 1.00 1.00"
assert_eq "the second reports its own" \
    "$(hour_row "$sum2" "2026-02-01 00:00")" "5.00 0.00 5.00 5.00"
assert_eq "and not the first flight's hour as well" \
    "$(hour_row "$sum2" "2026-01-01 00:00")" "none"
assert_eq "so the cumulative still lands on that flight's total" \
    "$(total_mb "$sum2")" "5.00"

echo
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]

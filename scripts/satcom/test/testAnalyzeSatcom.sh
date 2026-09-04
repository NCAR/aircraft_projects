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
192.168.84.7    8.8.8.8         1048576
8.8.8.8         192.168.84.7     524288
192.168.84.2    239.0.0.10      2097152
192.168.84.2    224.0.0.251      104857
192.168.84.7    192.168.84.2    1048576
10.0.0.5        192.168.84.7    1048576
192.168.84.7    255.255.255.255  524288
0.0.0.0         255.255.255.255   10485
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
192.168.84.7    128.117.43.224  1048576
192.168.84.7    223.255.255.255  524288
192.168.84.7    224.0.0.0        524288
192.168.84.7    239.255.255.255  524288
192.168.84.7    240.0.0.1        524288
192.168.84.7    172.15.0.1       524288
192.168.84.7    172.16.0.1       524288
192.168.84.7    172.31.255.255   524288
192.168.84.7    172.32.0.1       524288
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
192.168.84.7,1.2.3.4    1.2.3.4,192.168.84.7    1048576
ROWS
out=$(run_stubbed --root "$root" rf03_20260103)
sum="${root}/rf03_20260103/satcom-summary_rf03_20260103.txt"
assert_eq "outer header is used" "$(flow_mb "$sum" 192.168.84.7 1.2.3.4)" "1.00"
assert_not_contains "the comma-joined pair is not reported verbatim" \
    "$(cat "$sum")" "192.168.84.7,1.2.3.4"

echo "Test 4: hostnames come from the capture filenames, both conventions"
root="${tmp_dir}/t4"
make_capture "${root}/rf04_20260104/traffic20260104_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1048576
ROWS
# The Windows captures under applanix/ have no host token in the name.
make_capture "${root}/rf04_20260104/applanix/satcom_20260104_130000.pcap" <<'ROWS'
192.168.84.183  8.8.8.8     524288
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
192.168.84.7    8.8.8.8    524288    1787000000
ROWS
make_capture "${root}/rf05_20260105/traffic20260817_205320_brix01.pcap1" <<'ROWS'
192.168.84.7    8.8.8.8    524288    1787003600
ROWS
make_capture "${root}/rf05_20260105/traffic20260817_212320_brix05.pcap0" <<'ROWS'
192.168.84.164  8.8.8.8    1048576   1787001800
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
192.168.84.7    8.8.8.8    524288    1787003600
192.168.84.7    8.8.8.8    524288    1787007200
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
192.168.84.7    8.8.8.8    524288    1786996400
192.168.84.7    8.8.8.8    524288    1787000000
ROWS
out=$(run_stubbed --root "$root" rf05_20260105)
sum="${root}/rf05_20260105/satcom-summary_rf05_20260105.txt"
assert_contains "the earlier packet time is used as the start" \
    "$(collected "$sum")" "2026-08-17 19:53:20 to 2026-08-17 20:53:20 UTC"

echo "Test 6: megabytes are rounded once at the end, not per capture"
root="${tmp_dir}/t6"
# 5000 bytes rounds to 0.00 MB on its own; the two together are 0.01 MB.
make_capture "${root}/rf06_20260106/traffic20260106_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    5000
ROWS
make_capture "${root}/rf06_20260106/traffic20260106_140000_brix05.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    5000
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
192.168.84.7    8.8.8.8    1048576
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
192.168.84.7    8.8.8.8    1048576
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
192.168.84.7    8.8.8.8    1048576
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
192.168.84.7    8.8.8.8    1048576
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
192.168.84.7    151.101.17.91    1048576
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
192.168.84.160  239.0.0.10    2097152   1787000000
192.168.84.160  239.0.0.10    2097152   1787007200
ROWS
make_capture "${root}/rf11_20260111/traffic20260817_231320_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8       1048576   1787010800
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
192.168.84.7    8.8.8.8    1048576
ROWS
make_capture "${root}/rf13_20260113/traffic20260113_120000_brix05.pcap0" <<'ROWS'
192.168.84.164  8.8.8.8    524288
ROWS
# Maintenance captures must never be swept up by the rf* default.
make_capture "${root}/maint_days/traffic20260114_120000_brix01.pcap0" <<'ROWS'
192.168.84.7    8.8.8.8    1048576
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
192.168.84.7    8.8.8.8    1048576
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
if ! command -v text2pcap >/dev/null 2>&1 || ! command -v tshark >/dev/null 2>&1; then
    echo "  SKIP: text2pcap/tshark not installed"
else
    root="${tmp_dir}/t14"
    cache="${tmp_dir}/t14-cache.tsv"
    mkdir -p "${root}/rf15_20260116"

    # One 20-byte IPv4 header per packet, raw-IP encapsulation. Each claims a
    # total length of 1024 bytes while only the header is captured, which is
    # the same truncation the real -s 96 captures have: tshark reads ip.len
    # from the header field rather than from the bytes on disk.
    emit_packets() {			# emit_packets <count> <src hex> <dst hex>
        local n=$1 s=$2 d=$3 i=0
        while [ "$i" -lt "$n" ]; do
            printf '000000  45 00 04 00 00 00 00 00 40 11 00 00 %s %s\n' "$s" "$d"
            i=$((i + 1))
        done
    }
    {
        emit_packets 1024 "c0 a8 54 07" "80 75 2b 80"   # brix01 -> eol-hurricane, 1.00 MB
        emit_packets  512 "80 75 2b 80" "c0 a8 54 07"   # eol-hurricane -> brix01, 0.50 MB
        emit_packets 2048 "c0 a8 54 02" "ef 00 00 0a"   # NIDAS multicast,        2.00 MB
        emit_packets 1024 "c0 a8 54 02" "c0 a8 54 07"   # onboard to onboard,     1.00 MB
        emit_packets  512 "c0 a8 54 07" "ff ff ff ff"   # broadcast,              0.50 MB
    } > "${tmp_dir}/fixture.hex"
    # text2pcap stamps the packets with the time of conversion, so name the
    # capture for now as well to keep filename and packets consistent.
    e2e_stamp=$(date -u '+%Y%m%d_%H%M%S')
    text2pcap -q -l 101 "${tmp_dir}/fixture.hex" \
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

echo
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]

#!/bin/bash
#
# Tests for satcom-overview.sh: which summary files it reads, how it groups
# off-plane destinations, and how it attributes collection hours to them.
#
# The fixtures are synthetic satcom-summary_*.txt files in the format
# analyze-satcom.sh writes, so these tests need no pcaps, no wireshark and no
# DNS. Everything happens in a scratch directory. Run from anywhere:
#
#     ./testSatcomOverview.sh
#
# Exits 0 if all tests pass, 1 otherwise.

test_dir=$(cd "$(dirname "$0")" && pwd)
satcom_src=$(dirname "$test_dir")	# .../scripts/satcom
script="${satcom_src}/satcom-overview.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

assert_eq() {
    if [ "$2" = "$3" ]; then pass "$1"; else fail "$1 (got '$2', expected '$3')"; fi
}

assert_contains() {
    case "$2" in
        *"$3"*) pass "$1" ;;
        *) fail "$1 (expected to find: $3)" ;;
    esac
}

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

tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/testSatcomOverview.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT

##
# make_summary <path> <hours|none> [hostnames note]
#
# Writes a summary file in analyze-satcom.sh's format. Flow rows arrive on
# stdin as "MB src srcname dst dstname"; use "unknown" for a name that reverse
# DNS could not resolve. Pass "none" for hours to mimic a capture that
# recorded no packets, whose end time is unknown. A third argument becomes the
# Hostnames: line analyze-satcom.sh writes when it could not resolve names.
##
make_summary() {
    local path="$1" hours="$2" note="${3:-}" scope
    mkdir -p "$(dirname "$path")"
    scope=$(basename "$path" .txt); scope=${scope#satcom-summary_}
    {
        echo "Satcom off-plane traffic summary: $scope"
        echo "Generated: 2026-09-04 00:00:00 UTC"
        echo "Captures:  1 session(s) from testhost"
        if [ "$hours" = "none" ]; then
            echo "Collected: from 2026-08-17 20:53:20 UTC (no packets captured; end unknown)"
        else
            echo "Collected: 2026-08-17 20:53:20 to 2026-08-17 22:53:20 UTC (>= ${hours} h)"
        fi
        echo "Excluded:  multicast (224.0.0.0/4), broadcast, and onboard-only traffic"
        [ -n "$note" ] && echo "Hostnames: $note"
        echo
        echo "Total off-plane: 0.00 MB"
        echo
        echo "Onboard hosts"
        printf "  %-34s %10s %10s\n" "HOST" "SENT MB" "RECV MB"
        printf "  %-34s %10s %10s\n" "192.168.84.7 (brix01)" "0.00" "0.00"
        echo
        echo "Flows"
        printf "  %10s  %-48s %s\n" "MB" "SOURCE" "DESTINATION"
        awk '{ printf "  %10.2f  %-48s %s\n", $1, $2 " (" $3 ")", $4 " (" $5 ")" }'
        echo
        echo "No hostname found for 0 IP(s):"
    } > "$path"
}

##
# dest_cols <overview file> <destination label> -> "MB HOURS MB/HR", or "none"
#
# A label can contain spaces, so the numbers are taken as the last three
# fields and whatever precedes them is the label.
##
dest_cols() {
    awk -v want="$2" '
        /^  [^ ]/ {
            if (NF < 4) next
            mb = $(NF - 2); h = $(NF - 1); rate = $NF
            label = $0
            sub(/[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]+[^ \t]+[ \t]*$/, "", label)
            sub(/^[ \t]+/, "", label)
            if (label == want) { print mb, h, rate; found = 1; exit }
        }
        END { if (!found) print "none" }' "$1"
}

hdr() { awk -F': +' -v k="$2" '$1 == k { print $2; exit }' "$1"; }

# ------------------------------ The tests --------------------------------

echo "Test 1: every 128.117 address gets its own row"
root="${tmp_dir}/t1"
make_summary "${root}/rf01_20260101/satcom-summary_rf01_20260101.txt" 2.00 <<'ROWS'
10.00  128.117.43.128 eol-hurricane.eol.ucar.edu  192.168.84.2 acserver
 4.00  128.117.43.124 eol-ric.ucar.edu            192.168.84.2 acserver
 2.00  128.117.31.145 unknown                     192.168.84.2 acserver
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "the named UCAR host is its own row" \
    "$(dest_cols "$ov" eol-hurricane.eol.ucar.edu)" "10.00 2.00 5.000"
assert_eq "a second UCAR host is not merged into it" \
    "$(dest_cols "$ov" eol-ric.ucar.edu)" "4.00 2.00 2.000"
assert_eq "an unnamed UCAR address shows as the bare IP" \
    "$(dest_cols "$ov" 128.117.31.145)" "2.00 2.00 1.000"
assert_not_contains "UCAR addresses are never grouped under ucar.edu" \
    "$(cat "$ov")" "UCAR (other)"

echo "Test 2: other destinations group by operator, across domains and ranges"
root="${tmp_dir}/t2"
make_summary "${root}/rf02_20260102/satcom-summary_rf02_20260102.txt" 4.00 <<'ROWS'
1.00  142.250.1.1  ge-in-f95.1e100.net                       192.168.84.7 brix01
2.00  34.107.1.1   1-1-107-34.bc.googleusercontent.com       192.168.84.7 brix01
0.50  23.0.162.112 a23-0-162-112.deploy.static.akamaitechnologies.com 192.168.84.7 brix01
0.40  192.43.244.39 dnsx1.ucar.edu                           192.168.84.7 brix01
0.30  23.92.92.94  mirror.nodesdirect.com                    192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "1e100.net and googleusercontent.com are one Google row" \
    "$(dest_cols "$ov" "Google (2 addrs)")" "3.00 4.00 0.750"
assert_eq "akamaitechnologies.com becomes Akamai" \
    "$(dest_cols "$ov" Akamai)" "0.50 4.00 0.125"
assert_eq "non-128.117 UCAR addresses group together" \
    "$(dest_cols "$ov" "UCAR (other)")" "0.40 4.00 0.100"
# An operator with no alias of its own still collapses to its registrable
# domain, so per-host names do not each become their own row.
assert_eq "an unaliased host groups under its registrable domain" \
    "$(dest_cols "$ov" nodesdirect.com)" "0.30 4.00 0.075"
assert_contains "a single-address group carries no address count" \
    "$(cat "$ov")" "Akamai  "

echo "Test 3: unnamed addresses follow their neighbours, then a known block"
root="${tmp_dir}/t3"
make_summary "${root}/rf03_20260103/satcom-summary_rf03_20260103.txt" 2.00 <<'ROWS'
1.00  142.251.1.1  uj-in-f95.1e100.net   192.168.84.7 brix01
3.00  142.251.2.2  unknown               192.168.84.7 brix01
5.00  151.101.1.1  unknown               192.168.84.7 brix01
0.70  203.0.113.5  unknown               192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "an unnamed address joins the operator its /16 resolved to" \
    "$(dest_cols "$ov" "Google (2 addrs)")" "4.00 2.00 2.000"
assert_eq "a wholly unnamed known block is labelled" \
    "$(dest_cols "$ov" "Fastly CDN")" "5.00 2.00 2.500"
assert_eq "anything else is reported as an unresolved /16" \
    "$(dest_cols "$ov" "unresolved 203.0.x.x")" "0.70 2.00 0.350"

echo "Test 4: MB is sent plus received"
root="${tmp_dir}/t4"
make_summary "${root}/rf04_20260104/satcom-summary_rf04_20260104.txt" 2.00 <<'ROWS'
1.00  192.168.84.7 brix01        8.8.8.8      dns.google
3.00  8.8.8.8      dns.google    192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "both directions land on one row" \
    "$(dest_cols "$ov" "dns.google")" "4.00 2.00 2.000"

echo "Test 5: hours count only the flights a destination appeared in"
root="${tmp_dir}/t5"
make_summary "${root}/rf05_20260105/satcom-summary_rf05_20260105.txt" 2.00 <<'ROWS'
1.00  128.117.43.128 eol-hurricane.eol.ucar.edu  192.168.84.2 acserver
1.00  128.117.43.124 eol-ric.ucar.edu            192.168.84.2 acserver
ROWS
make_summary "${root}/rf06_20260106/satcom-summary_rf06_20260106.txt" 3.00 <<'ROWS'
2.00  128.117.43.124 eol-ric.ucar.edu            192.168.84.2 acserver
4.00  128.117.43.118 eol-aeolian.eol.ucar.edu    192.168.84.2 acserver
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "a destination seen on one flight is charged that flight only" \
    "$(dest_cols "$ov" eol-hurricane.eol.ucar.edu)" "1.00 2.00 0.500"
assert_eq "a destination seen on both is charged both" \
    "$(dest_cols "$ov" eol-ric.ucar.edu)" "3.00 5.00 0.600"
assert_eq "and one seen only on the later flight likewise" \
    "$(dest_cols "$ov" eol-aeolian.eol.ucar.edu)" "4.00 3.00 1.333"
assert_eq "the header collection time is the sum over flights" \
    "$(hdr "$ov" Collection)" "5.00 hr"

echo "Test 6: totals and the overall rate"
assert_eq "off-plane total is the sum of all destinations" \
    "$(hdr "$ov" Off-plane)" "8.00 MB"
assert_eq "the overall rate is off-plane over collection" \
    "$(hdr "$ov" Overall)" "1.600 MB/HR   (off-plane / collection)"
# The total row's hours must be the collection window, not 2+5+3 from the column.
assert_eq "the total row uses the collection window, not a column sum" \
    "$(dest_cols "$ov" "TOTAL (all destinations)")" "8.00 5.00 1.600"

echo "Test 7: --min hides small rows but never loses them from the total"
root="${tmp_dir}/t7"
make_summary "${root}/rf07_20260107/satcom-summary_rf07_20260107.txt" 2.00 <<'ROWS'
5.00  8.8.8.8      dns.google    192.168.84.7 brix01
0.05  1.2.3.4      tiny.example  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "the small row is hidden by default" \
    "$(dest_cols "$ov" tiny.example)" "none"
assert_contains "and the omission is reported" "$(cat "$ov")" \
    "1 of 2 destinations shown; 1 below 0.1 MB omitted, 0.05 MB between them."
assert_eq "the total still includes it" \
    "$(dest_cols "$ov" "TOTAL (all destinations)")" "5.05 2.00 2.525"
out=$("$script" --root "$root" --min 0)
assert_eq "--min 0 shows it" "$(dest_cols "$ov" tiny.example)" "0.05 2.00 0.025"
assert_not_contains "and reports no omissions" "$(cat "$ov")" "omitted"

echo "Test 8: which summary files get read"
root="${tmp_dir}/t8"
# A flight-level summary covers every capture beneath it, so the per-capture
# summary beside it and the nested one below it must both be skipped.
make_summary "${root}/rf08_20260108/satcom-summary_rf08_20260108.txt" 2.00 <<'ROWS'
10.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
make_summary "${root}/rf08_20260108/satcom-summary_20260108_120000_brix01.txt" 2.00 <<'ROWS'
7.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
make_summary "${root}/rf08_20260108/applanix/satcom-summary_applanix.txt" 1.00 <<'ROWS'
3.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
# A flight with no summary of its own is descended into.
make_summary "${root}/rf09_20260109/applanix/satcom-summary_applanix.txt" 4.00 <<'ROWS'
5.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
# Maintenance days stay out of the default scope.
make_summary "${root}/maint_days/satcom-summary_maint_days.txt" 9.00 <<'ROWS'
99.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "a flight summary prunes the rest of its subtree" \
    "$(hdr "$ov" Off-plane)" "15.00 MB"
assert_eq "so only two summaries are counted" "$(hdr "$ov" Flights" ")" ""
assert_contains "the flight summary is used for rf08" "$(hdr "$ov" Flights)" "rf08_20260108"
assert_contains "the nested summary is used for rf09" \
    "$(hdr "$ov" Flights)" "rf09_20260109/applanix"
assert_not_contains "maint_days is excluded" "$(cat "$ov")" "maint_days"
assert_eq "hours come from the two files actually read" \
    "$(hdr "$ov" Collection)" "6.00 hr"

echo "Test 9: nested summaries are keyed by path, not by directory name"
root="${tmp_dir}/t9"
# Both flights lack a flight-level summary and both nest an applanix one.
# Keyed by bare name they would collide and one set of hours would be lost.
make_summary "${root}/rf10_20260110/applanix/satcom-summary_applanix.txt" 2.00 <<'ROWS'
4.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
make_summary "${root}/rf11_20260111/applanix/satcom-summary_applanix.txt" 3.00 <<'ROWS'
6.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_contains "both are listed under their own flight" \
    "$(hdr "$ov" Flights)" "rf10_20260110/applanix"
assert_contains "and the second too" "$(hdr "$ov" Flights)" "rf11_20260111/applanix"
assert_eq "neither set of hours is lost to a collision" \
    "$(hdr "$ov" Collection)" "5.00 hr"
assert_eq "and the destination is charged both" \
    "$(dest_cols "$ov" dns.google)" "10.00 5.00 2.000"

echo "Test 10: scope selection and where the report is written"
root="${tmp_dir}/t10"
make_summary "${root}/rf12_20260112/satcom-summary_rf12_20260112.txt" 2.00 <<'ROWS'
4.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
make_summary "${root}/rf13_20260113/satcom-summary_rf13_20260113.txt" 3.00 <<'ROWS'
6.00  1.2.3.4  other.example.com  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
assert_file "the default run writes satcom-overview.txt to the root" \
    "${root}/satcom-overview.txt"
assert_eq "and covers every flight" "$(hdr "${root}/satcom-overview.txt" Off-plane)" "10.00 MB"

out=$("$script" --root "$root" rf12_20260112)
assert_file "a scoped run writes its own file to the root" \
    "${root}/satcom-overview_rf12_20260112.txt"
assert_eq "covering only that flight" \
    "$(hdr "${root}/satcom-overview_rf12_20260112.txt" Off-plane)" "4.00 MB"
assert_eq "and leaves the full report alone" \
    "$(hdr "${root}/satcom-overview.txt" Off-plane)" "10.00 MB"

out=$("$script" --root "$root" rf12_20260112 rf13_20260113)
assert_file "several flights combine into one scoped file" \
    "${root}/satcom-overview_rf12_20260112+rf13_20260113.txt"
out=$("$script" "${root}/rf13_20260113/satcom-summary_rf13_20260113.txt" --root "$root")
assert_eq "an explicit summary file can be named" \
    "$(hdr "${root}/satcom-overview_satcom-summary_rf13_20260113.txt" Off-plane)" "6.00 MB"

echo "Test 11: a flight whose capture recorded no packets"
root="${tmp_dir}/t11"
make_summary "${root}/rf14_20260114/satcom-summary_rf14_20260114.txt" none <<'ROWS'
2.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
make_summary "${root}/rf15_20260115/satcom-summary_rf15_20260115.txt" 4.00 <<'ROWS'
8.00  1.2.3.4  other.example.com  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_eq "it contributes no hours" "$(hdr "$ov" Collection)" "4.00 hr"
assert_contains "and that is stated rather than hidden" "$(cat "$ov")" \
    "1 flight(s) had no packet timestamps, so contribute 0 hr."
assert_eq "a destination seen only there reports no rate" \
    "$(dest_cols "$ov" dns.google)" "2.00 0.00 0.000"
assert_eq "its MB still counts toward the total" "$(hdr "$ov" Off-plane)" "10.00 MB"

echo "Test 11b: a summary built without reverse DNS is flagged here too"
root="${tmp_dir}/t11b"
# One flight analyzed on a host with no resolver, one analyzed normally.
make_summary "${root}/rf16_20260116/satcom-summary_rf16_20260116.txt" 2.00 \
    "dig not found, so no lookups were made; public addresses show as unknown" <<'ROWS'
3.00  151.101.1.1  unknown     192.168.84.7 brix01
ROWS
make_summary "${root}/rf17_20260117/satcom-summary_rf17_20260117.txt" 3.00 <<'ROWS'
5.00  8.8.8.8      dns.google  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_contains "the overview says how many summaries lacked names" \
    "$(cat "$ov")" "Hostnames:  1 of 2 summaries had no reverse DNS"
assert_contains "and repeats the reason from the summary" \
    "$(cat "$ov")" "dig not found, so no lookups were made"
assert_contains "and names the symptom a reader would see" \
    "$(cat "$ov")" 'show as "unresolved <block>.x.x"'
assert_eq "the resolved flight is unaffected" \
    "$(dest_cols "$ov" dns.google)" "5.00 3.00 1.667"

echo "Test 11c: nothing is said when every summary had reverse DNS"
root="${tmp_dir}/t11c"
make_summary "${root}/rf18_20260118/satcom-summary_rf18_20260118.txt" 2.00 <<'ROWS'
4.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
assert_not_contains "no note when there is nothing to explain" \
    "$(cat "${root}/satcom-overview.txt")" "Hostnames:"

echo "Test 12: units are consistent, and errors are reported"
root="${tmp_dir}/t12"
make_summary "${root}/rf16_20260116/satcom-summary_rf16_20260116.txt" 2.00 <<'ROWS'
4.00  8.8.8.8  dns.google  192.168.84.7 brix01
ROWS
out=$("$script" --root "$root")
ov="${root}/satcom-overview.txt"
assert_contains "the hours column says HR" "$(cat "$ov")" "COLLECTION (HR)"
assert_contains "the rate column says MB/HR" "$(cat "$ov")" "MB/HR"
assert_not_contains "no stray (H) unit is left" "$(cat "$ov")" "(H)"
mkdir -p "${tmp_dir}/empty-root"
assert_contains "a root with no flights is an error" \
    "$("$script" --root "${tmp_dir}/empty-root" 2>&1)" "no rf* directories"
assert_contains "a missing root is a different error" \
    "$("$script" --root "${tmp_dir}/no-such-root" 2>&1)" "capture root not found"
assert_contains "an unknown target is an error" \
    "$("$script" --root "$root" nosuchflight 2>&1)" "no such flight or summary file"
assert_contains "--help works" "$("$script" --help)" "OFF-PLANE DESTINATION"

echo
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]

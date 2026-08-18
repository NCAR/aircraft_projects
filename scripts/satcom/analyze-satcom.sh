#!/bin/bash
##
# Summarize traffic volume per src/dst pair from a satcom capture.
#
# Usage: analyze-satcom.sh YYYYMMDD_HHMMSS
#   The date stamp is the one satcom_capture.sh put in the pcap filename,
#   e.g. traffic20260818_173026.pcap00 -> 20260818_173026
#   Run `ls /var/log/satcom-capture/` to see available captures.
##
if [ $# -ne 1 ]; then
    {
        echo "Usage: $(basename "$0") YYYYMMDD_HHMMSS"
        echo "Available captures:"
        ls /var/log/satcom-capture/ 2>/dev/null
    } >&2
    exit 1
fi

CAPTURE_DATE="$1"

# Exit if no matches for the given date
shopt -s nullglob # don't expand to literal string if no matches
files=(/var/log/satcom-capture/traffic${CAPTURE_DATE}.pcap*)
[ ${#files[@]} -gt 0 ] || { echo "no captures for $CAPTURE_DATE" >&2; exit 1; }

echo "Analyzing ${#files[@]} file(s):"
printf '  %s\n' "${files[@]}"

OUTPUT_DIR="/var/log/ads/satcom"
OUTPUT_FILE="satcom-analysis_${CAPTURE_DATE}.txt"

if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
fi

mergecap -w - /var/log/satcom-capture/traffic${CAPTURE_DATE}.pcap* | tshark -r - --disable-protocol drbd -T fields \
    -e ip.src -e ip.dst -e ip.len | \
    awk '{
        flow = $1 " => " $2
        bytes[flow] += $3
    }
    END {
        for (f in bytes) {
            printf "%s: %.2f MB\n", f, bytes[f]/1024/1024
        }
    }' | sort -t: -k2 -rn > "$OUTPUT_DIR/$OUTPUT_FILE"

echo "Analysis complete: $OUTPUT_DIR/$OUTPUT_FILE"

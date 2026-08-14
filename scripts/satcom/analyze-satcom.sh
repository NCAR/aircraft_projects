#!/bin/bash
OUTPUT="/home/local/projects/scripts/satcom/satcom-analysis.txt"

tshark $(for f in /var/log/satcom-capture/traffic.pcap*; do echo "-r $f"; done) -T fields \
    -e ip.src -e ip.dst -e ip.len | \
    awk '{
        flow = $1 " => " $2
        bytes[flow] += $3
    }
    END {
        for (f in bytes) {
            printf "%s: %.2f MB\n", f, bytes[f]/1024/1024
        }
    }' | sort -t: -k2 -rn > "$OUTPUT"

echo "Analysis complete: $OUTPUT"

#!/bin/bash

## Run this script to log in as nimbus to create production files
### This script will create a temporary file with the necessary xauth entry and display variable that are needed to run nimbus.

XAUTH_ENTRY=$(xauth list | grep "$(hostname)/unix" | tail -1)

if [ -z "$XAUTH_ENTRY" ]; then
  echo "ERROR: No xauth entry found. Is your session using X11 forwarding (-Y)?"
  exit 1
fi

XAUTH_DISPLAY=$(echo "$XAUTH_ENTRY" | awk '{print $1}')
XAUTH_PROTO=$(echo "$XAUTH_ENTRY"   | awk '{print $2}')
XAUTH_COOKIE=$(echo "$XAUTH_ENTRY"  | awk '{print $3}')
CURRENT_DISPLAY="$DISPLAY"

TMPFILE=$(mktemp /tmp/nimbus-setup-XXXX.csh)
chmod 644 $TMPFILE

cat > $TMPFILE << EOF
xauth add $XAUTH_DISPLAY $XAUTH_PROTO $XAUTH_COOKIE
setenv DISPLAY $CURRENT_DISPLAY
rm $TMPFILE
EOF

echo ""
echo "========================================"
echo "Once you are logged in as nimbus, run:"
echo ""
echo "  source $TMPFILE"
echo ""
echo "========================================"
echo ""

sudo su - nimbus

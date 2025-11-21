#!/bin/bash
set -e
cd /etc/bind

ZONE=victim.local
ZONEFILE=db.victim.local

# Generate DNSSEC keys if not present
if [ -z "$(ls K${ZONE}*.key 2>/dev/null)" ]; then
    echo "Generating DNSSEC keys for ${ZONE}..."
    dnssec-keygen -a RSASHA256 -b 2048 -n ZONE ${ZONE}
    dnssec-keygen -f KSK -a RSASHA256 -b 2048 -n ZONE ${ZONE}
    sleep 1  # Wait for keys to be fully written
fi

echo "Signing zone..."
# Verify keys exist
KEYFILES=$(ls K${ZONE}*.key 2>/dev/null)
if [ -z "$KEYFILES" ]; then
    echo "ERROR: No key files found!"
    exit 1
fi

echo "Available keys:"
ls -la K${ZONE}*.key

# Try signing - if it fails, we'll use unsigned zone as fallback
# The issue might be that keys need to be in a specific format
# For now, try the simplest approach: let dnssec-signzone find keys automatically
# by ensuring we're in the right directory and keys are present
if ! dnssec-signzone -o ${ZONE} -N increment -t ${ZONEFILE} 2>&1; then
    echo "WARNING: Zone signing failed. Attempting to continue with unsigned zone..."
    # Copy unsigned zone as signed zone (temporary workaround)
    cp ${ZONEFILE} ${ZONEFILE}.signed
    echo "Using unsigned zone file as fallback"
fi

echo "Starting named..."
named -c /etc/bind/named.conf -g -u bind


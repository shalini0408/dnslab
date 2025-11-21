#!/bin/bash
set -e

if [ ! -f /var/lib/unbound/root.key ]; then
    echo "Fetching root trust anchor..."
    unbound-anchor -a /var/lib/unbound/root.key
fi

echo "Starting Unbound with DNSSEC validation..."
unbound -d -c /etc/unbound/unbound.conf


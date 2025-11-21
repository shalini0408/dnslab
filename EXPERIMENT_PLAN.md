# DNS Cache Poisoning Experiment Plan

## Overview
This experiment demonstrates DNS cache poisoning attacks against:
1. **Vulnerable resolver** (dnsmasq) - No DNSSEC validation
2. **Protected resolver** (Unbound) - With DNSSEC validation

## Architecture

```
┌─────────────────┐
│  Attacker       │  Sends forged DNS responses
│  10.5.0.60/61   │  (random TXIDs, fake IP: 10.5.0.99)
└────────┬────────┘
         │
         ▼
┌─────────────────┐         ┌──────────────────┐
│ Plain Resolver  │────────▶│ Auth DNS Server  │
│ (dnsmasq)       │         │ (BIND9)          │
│ 10.5.0.53       │         │ 10.5.0.2         │
│ ❌ No DNSSEC    │         │ victim.local     │
└─────────────────┘         └──────────────────┘
         │
         ▼
┌─────────────────┐
│ DNSSEC Resolver │────────▶│ Auth DNS Server  │
│ (Unbound)       │         │ (BIND9)          │
│ 10.5.0.54       │         │ 10.5.0.2         │
│ ✅ DNSSEC Valid │         │ victim.local     │
└─────────────────┘         └──────────────────┘
```

## Experiment Steps

### Phase 1: Manual Testing

#### Step 1: Baseline - Normal DNS Resolution
```powershell
# Test authoritative server directly
docker run --rm --network dnslab_dnslab debian:stable-slim bash -c "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && dig @10.5.0.2 www.victim.local +short"
# Expected: 10.5.0.10 (real IP)

# Test plain resolver (should get real IP)
docker run --rm --network dnslab_dnslab debian:stable-slim bash -c "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && dig @10.5.0.53 www.victim.local +short"
# Expected: 10.5.0.10 (real IP)
```

#### Step 2: Start Attack Against Plain Resolver
```powershell
# Attacker is already running, but let's restart it to clear cache
docker-compose restart attacker_plain

# Wait a moment, then query the resolver multiple times
# The attacker sends forged responses with random TXIDs
# If we get lucky and match a TXID, the cache gets poisoned
```

#### Step 3: Test Cache Poisoning Success
```powershell
# Query the plain resolver multiple times
# Some queries might return the fake IP (10.5.0.99) if poisoning succeeded
docker run --rm --network dnslab_dnslab debian:stable-slim bash -c "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && dig @10.5.0.53 www.victim.local +short"
```

#### Step 4: Test DNSSEC Protection
```powershell
# Query the DNSSEC resolver
# Should always return the real IP (10.5.0.10) because DNSSEC validation rejects forged responses
docker run --rm --network dnslab_dnslab debian:stable-slim bash -c "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && dig @10.5.0.54 www.victim.local +short"
# Expected: 10.5.0.10 (always, protected by DNSSEC)
```

### Phase 2: Automated Measurement

#### Run the measurement script:
```powershell
cd experiments
python measure.py
```

This script will:
1. Run 30 trials against the plain resolver
2. Run 30 trials against the DNSSEC resolver
3. Measure:
   - Success rate of poisoning
   - Time to successful poisoning
4. Save results to `measurements.csv`

#### Generate visualization:
```powershell
python plot_results.py
# Creates poison_success.png showing comparison
```

### Phase 3: Analysis

#### Expected Results:
- **Plain Resolver (no_dnssec)**: 
  - Some successful poisonings (depends on TXID guessing luck)
  - Variable time to poison
  
- **DNSSEC Resolver (dnssec)**:
  - Zero successful poisonings
  - Always returns correct IP

## Attack Mechanism

The attacker (`attacker.py`) works by:
1. **Spoofing DNS responses** with random transaction IDs (TXIDs)
2. **Sending forged responses** faster than the legitimate server
3. **Hoping to match** the TXID of a pending query
4. **If matched**: The resolver caches the fake IP (10.5.0.99)

**Why it works on plain resolver:**
- No cryptographic validation
- Accepts any response with matching TXID
- Caches the first valid-looking response

**Why it fails on DNSSEC resolver:**
- Validates cryptographic signatures
- Rejects responses without valid DNSSEC signatures
- Only caches cryptographically verified responses

## Monitoring

### View attacker logs:
```powershell
docker-compose logs -f attacker_plain
```

### View resolver logs:
```powershell
docker-compose logs -f resolver_plain
docker-compose logs -f resolver_dnssec
```

### Capture network traffic:
```powershell
# In another terminal, capture DNS traffic
docker run --rm --network dnslab_dnslab --cap-add=NET_ADMIN nicolaka/netshoot tcpdump -nn -i eth0 udp port 53
```

## Troubleshooting

1. **If poisoning never succeeds:**
   - Increase attack rate (reduce SLEEP in attacker.py)
   - Clear resolver cache more frequently
   - Check that attacker is actually sending packets

2. **If DNSSEC resolver fails:**
   - Check that auth server has DNSSEC keys
   - Verify Unbound trust anchor is set up
   - Check resolver_dnssec logs for validation errors

3. **Network issues:**
   - Verify all containers are on `dnslab_dnslab` network
   - Check IP addresses match expected values
   - Ensure containers can reach each other


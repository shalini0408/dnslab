#!/usr/bin/env python3
"""
Simple demonstration script for DNS cache poisoning experiment.
Shows the difference between vulnerable and protected resolvers.
"""

import subprocess
import time
import sys

PLAIN_RESOLVER = "10.5.0.53"
DNSSEC_RESOLVER = "10.5.0.54"
TARGET = "www.victim.local"
REAL_IP = "10.5.0.10"
FAKE_IP = "10.5.0.99"

def run_dig(resolver_ip, target):
    """Run dig command and return the IP address."""
    cmd = [
        "docker", "run", "--rm", "--network", "dnslab_dnslab",
        "debian:stable-slim",
        "bash", "-c",
        "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && "
        f"dig @{resolver_ip} {target} +short"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()

def clear_cache(service_name):
    """Restart a service to clear its cache."""
    print(f"  [*] Clearing cache for {service_name}...")
    subprocess.run(["docker-compose", "restart", service_name], 
                   capture_output=True, timeout=10)
    time.sleep(2)

def main():
    print("=" * 70)
    print("DNS Cache Poisoning Experiment Demonstration")
    print("=" * 70)
    print()
    
    # Step 1: Baseline
    print("STEP 1: Baseline - Normal DNS Resolution")
    print("-" * 70)
    print(f"Querying plain resolver ({PLAIN_RESOLVER})...")
    result1 = run_dig(PLAIN_RESOLVER, TARGET)
    print(f"  Result: {result1}")
    print(f"  Expected: {REAL_IP}")
    print(f"  Status: {'[OK] CORRECT' if result1 == REAL_IP else '[X] WRONG'}")
    print()
    
    print(f"Querying DNSSEC resolver ({DNSSEC_RESOLVER})...")
    result2 = run_dig(DNSSEC_RESOLVER, TARGET)
    print(f"  Result: {result2}")
    print(f"  Expected: {REAL_IP}")
    print(f"  Status: {'[OK] CORRECT' if result2 == REAL_IP else '[X] WRONG'}")
    print()
    
    # Step 2: Start attack and test
    print("STEP 2: Testing Cache Poisoning Attack")
    print("-" * 70)
    print("The attacker is sending forged DNS responses with random TXIDs...")
    print("Let's query the plain resolver multiple times to see if we get poisoned.")
    print()
    
    clear_cache("resolver_plain")
    clear_cache("attacker_plain")
    
    print("Querying plain resolver 10 times (attack in progress)...")
    poisoned_count = 0
    for i in range(10):
        result = run_dig(PLAIN_RESOLVER, TARGET)
        status = "POISONED!" if result == FAKE_IP else "OK"
        if result == FAKE_IP:
            poisoned_count += 1
        print(f"  Query {i+1}: {result:12} [{status}]")
        time.sleep(0.5)
    
    print()
    print(f"  Poisoning success rate: {poisoned_count}/10 ({poisoned_count*10}%)")
    print()
    
    # Step 3: Test DNSSEC protection
    print("STEP 3: Testing DNSSEC Protection")
    print("-" * 70)
    print("Now querying the DNSSEC-protected resolver...")
    print("DNSSEC should reject all forged responses.")
    print()
    
    clear_cache("resolver_dnssec")
    clear_cache("attacker_dnssec")
    
    print("Querying DNSSEC resolver 10 times (attack in progress)...")
    protected_count = 0
    for i in range(10):
        result = run_dig(DNSSEC_RESOLVER, TARGET)
        status = "PROTECTED" if result == REAL_IP else "COMPROMISED!"
        if result == REAL_IP:
            protected_count += 1
        print(f"  Query {i+1}: {result:12} [{status}]")
        time.sleep(0.5)
    
    print()
    print(f"  Protection rate: {protected_count}/10 ({protected_count*10}%)")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Plain Resolver (vulnerable):")
    print(f"  - Got poisoned: {poisoned_count}/10 times")
    print(f"  - Risk: HIGH - Accepts forged responses")
    print()
    print(f"DNSSEC Resolver (protected):")
    print(f"  - Got poisoned: {10-protected_count}/10 times")
    print(f"  - Risk: LOW - Validates all responses cryptographically")
    print()
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


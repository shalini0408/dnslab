#!/usr/bin/env python3
"""
Measure DNSSEC performance overhead (latency and CPU usage).
Compares DNS resolution performance with and without DNSSEC validation.
"""

import subprocess
import time
import csv
import threading
from collections import defaultdict

N_TRIALS = 100
TARGET_NAME = "www.victim.local"
PLAIN_RESOLVER = "10.5.0.53"
DNSSEC_RESOLVER = "10.5.0.54"

# For CPU monitoring
cpu_samples = defaultdict(list)
monitoring = False

def monitor_cpu(container_name, label):
    """Monitor CPU usage of a container."""
    global monitoring
    while monitoring:
        try:
            # Get container stats
            cmd = ["docker", "stats", "--no-stream", "--format", "{{.CPUPerc}}", container_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                cpu_percent = float(result.stdout.strip().rstrip('%'))
                cpu_samples[label].append(cpu_percent)
        except Exception as e:
            pass
        time.sleep(0.1)  # Sample every 100ms

def run_dig(resolver: str, count: int = 1):
    """Run dig command and measure latency."""
    cmd = [
        "docker", "run", "--rm", "--network", "dnslab_dnslab",
        "debian:stable-slim",
        "bash", "-c",
        "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && "
        f"dig @{resolver} {TARGET_NAME} +short"
    ]
    
    latencies = []
    for _ in range(count):
        t0 = time.time()
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        t1 = time.time()
        latency_ms = (t1 - t0) * 1000.0
        latencies.append(latency_ms)
    
    return latencies

def measure_resolver_performance(resolver_ip: str, resolver_name: str, container_name: str, label: str):
    """Measure performance metrics for a resolver."""
    print(f"\n[{label}] Measuring performance for {resolver_name} ({resolver_ip})...")
    
    global monitoring, cpu_samples
    cpu_samples[label] = []
    
    # Start CPU monitoring thread
    monitoring = True
    cpu_thread = threading.Thread(target=monitor_cpu, args=(container_name, label), daemon=True)
    cpu_thread.start()
    
    # Warm-up queries (to fill cache, avoid cold start effects)
    print(f"  [*] Warm-up queries...")
    run_dig(resolver_ip, count=5)
    time.sleep(1)
    
    # Clear CPU samples after warm-up
    cpu_samples[label] = []
    
    # Measure latency
    print(f"  [*] Running {N_TRIALS} latency measurements...")
    all_latencies = []
    
    for i in range(0, N_TRIALS, 10):  # Run in batches of 10
        batch = min(10, N_TRIALS - i)
        latencies = run_dig(resolver_ip, count=batch)
        all_latencies.extend(latencies)
        
        if (i + batch) % 20 == 0:
            print(f"    Progress: {i + batch}/{N_TRIALS}")
        time.sleep(0.1)  # Small delay between batches
    
    # Stop CPU monitoring
    monitoring = False
    time.sleep(0.5)  # Wait for last CPU samples
    
    # Calculate statistics
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    min_latency = min(all_latencies) if all_latencies else 0
    max_latency = max(all_latencies) if all_latencies else 0
    
    avg_cpu = sum(cpu_samples[label]) / len(cpu_samples[label]) if cpu_samples[label] else 0
    max_cpu = max(cpu_samples[label]) if cpu_samples[label] else 0
    
    print(f"  [✓] Completed")
    print(f"    Average latency: {avg_latency:.2f} ms")
    print(f"    Min latency: {min_latency:.2f} ms")
    print(f"    Max latency: {max_latency:.2f} ms")
    print(f"    Average CPU: {avg_cpu:.2f}%")
    print(f"    Max CPU: {max_cpu:.2f}%")
    
    return {
        "resolver": label,
        "resolver_ip": resolver_ip,
        "avg_latency_ms": avg_latency,
        "min_latency_ms": min_latency,
        "max_latency_ms": max_latency,
        "avg_cpu_percent": avg_cpu,
        "max_cpu_percent": max_cpu,
        "all_latencies": all_latencies,
        "all_cpu_samples": cpu_samples[label]
    }

def main():
    print("=" * 70)
    print("DNSSEC Performance Overhead Measurement")
    print("=" * 70)
    print(f"Trials: {N_TRIALS}")
    print(f"Target: {TARGET_NAME}")
    print()
    
    # Check if containers are running
    try:
        subprocess.run(["docker", "ps", "--filter", "name=resolver_plain"], 
                      capture_output=True, check=True)
        subprocess.run(["docker", "ps", "--filter", "name=resolver_dnssec"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("ERROR: Resolvers are not running. Please start them with:")
        print("  docker-compose up -d resolver_plain resolver_dnssec")
        return
    
    # Measure plain resolver (no DNSSEC)
    plain_results = measure_resolver_performance(
        PLAIN_RESOLVER, 
        "Plain Resolver (dnsmasq)", 
        "dnslab-resolver_plain-1",
        "no_dnssec"
    )
    
    time.sleep(2)  # Brief pause between measurements
    
    # Measure DNSSEC resolver
    dnssec_results = measure_resolver_performance(
        DNSSEC_RESOLVER, 
        "DNSSEC Resolver (Unbound)", 
        "dnslab-resolver_dnssec-1",
        "dnssec"
    )
    
    # Calculate overhead
    latency_overhead = dnssec_results["avg_latency_ms"] - plain_results["avg_latency_ms"]
    latency_overhead_percent = (latency_overhead / plain_results["avg_latency_ms"] * 100) if plain_results["avg_latency_ms"] > 0 else 0
    
    cpu_overhead = dnssec_results["avg_cpu_percent"] - plain_results["avg_cpu_percent"]
    
    print("\n" + "=" * 70)
    print("PERFORMANCE OVERHEAD ANALYSIS")
    print("=" * 70)
    print(f"\nLatency Overhead:")
    print(f"  DNSSEC adds: {latency_overhead:.2f} ms ({latency_overhead_percent:.1f}% increase)")
    print(f"  Plain:  {plain_results['avg_latency_ms']:.2f} ms")
    print(f"  DNSSEC: {dnssec_results['avg_latency_ms']:.2f} ms")
    
    print(f"\nCPU Overhead:")
    print(f"  DNSSEC adds: {cpu_overhead:.2f}% CPU")
    print(f"  Plain:  {plain_results['avg_cpu_percent']:.2f}%")
    print(f"  DNSSEC: {dnssec_results['avg_cpu_percent']:.2f}%")
    
    # Save detailed results to CSV
    with open("performance_overhead.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "resolver", "resolver_ip", "avg_latency_ms", "min_latency_ms", "max_latency_ms",
            "avg_cpu_percent", "max_cpu_percent", "latency_overhead_ms", "latency_overhead_percent", "cpu_overhead_percent"
        ])
        writer.writeheader()
        
        # Plain resolver row
        writer.writerow({
            "resolver": "no_dnssec",
            "resolver_ip": PLAIN_RESOLVER,
            "avg_latency_ms": plain_results["avg_latency_ms"],
            "min_latency_ms": plain_results["min_latency_ms"],
            "max_latency_ms": plain_results["max_latency_ms"],
            "avg_cpu_percent": plain_results["avg_cpu_percent"],
            "max_cpu_percent": plain_results["max_cpu_percent"],
            "latency_overhead_ms": 0,
            "latency_overhead_percent": 0,
            "cpu_overhead_percent": 0
        })
        
        # DNSSEC resolver row
        writer.writerow({
            "resolver": "dnssec",
            "resolver_ip": DNSSEC_RESOLVER,
            "avg_latency_ms": dnssec_results["avg_latency_ms"],
            "min_latency_ms": dnssec_results["min_latency_ms"],
            "max_latency_ms": dnssec_results["max_latency_ms"],
            "avg_cpu_percent": dnssec_results["avg_cpu_percent"],
            "max_cpu_percent": dnssec_results["max_cpu_percent"],
            "latency_overhead_ms": latency_overhead,
            "latency_overhead_percent": latency_overhead_percent,
            "cpu_overhead_percent": cpu_overhead
        })
    
    print(f"\n[+] Saved detailed results to performance_overhead.csv")
    
    # Save raw latency data for plotting
    with open("performance_latencies.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["resolver", "trial", "latency_ms"])
        for i, latency in enumerate(plain_results["all_latencies"], 1):
            writer.writerow(["no_dnssec", i, latency])
        for i, latency in enumerate(dnssec_results["all_latencies"], 1):
            writer.writerow(["dnssec", i, latency])
    
    print(f"[+] Saved raw latency data to performance_latencies.csv")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMeasurement interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


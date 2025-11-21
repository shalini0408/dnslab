#!/usr/bin/env python3
"""
Plot performance overhead comparison charts.
Creates visualizations for latency and CPU overhead.
"""

import csv
import matplotlib.pyplot as plt
import numpy as np

def plot_latency_comparison():
    """Plot latency comparison between plain and DNSSEC resolvers."""
    latencies_plain = []
    latencies_dnssec = []
    
    try:
        with open("performance_latencies.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["resolver"] == "no_dnssec":
                    latencies_plain.append(float(row["latency_ms"]))
                elif row["resolver"] == "dnssec":
                    latencies_dnssec.append(float(row["latency_ms"]))
    except FileNotFoundError:
        print("ERROR: performance_latencies.csv not found. Run measure_performance.py first.")
        return
    
    if not latencies_plain or not latencies_dnssec:
        print("ERROR: No data found in performance_latencies.csv")
        return
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Box plot comparison
    ax1.boxplot([latencies_plain, latencies_dnssec], labels=["No DNSSEC", "DNSSEC"])
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title("DNS Resolution Latency Comparison")
    ax1.grid(True, alpha=0.3)
    
    # Histogram comparison
    ax2.hist(latencies_plain, bins=30, alpha=0.7, label="No DNSSEC", color="blue")
    ax2.hist(latencies_dnssec, bins=30, alpha=0.7, label="DNSSEC", color="red")
    ax2.set_xlabel("Latency (ms)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Latency Distribution")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("performance_latency_comparison.png", dpi=150)
    print("[+] Saved performance_latency_comparison.png")

def plot_overhead_summary():
    """Plot overhead summary from performance_overhead.csv."""
    try:
        with open("performance_overhead.csv") as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        print("ERROR: performance_overhead.csv not found. Run measure_performance.py first.")
        return
    
    if len(data) < 2:
        print("ERROR: Insufficient data in performance_overhead.csv")
        return
    
    plain_data = next((d for d in data if d["resolver"] == "no_dnssec"), None)
    dnssec_data = next((d for d in data if d["resolver"] == "dnssec"), None)
    
    if not plain_data or not dnssec_data:
        print("ERROR: Missing data for comparison")
        return
    
    # Extract values
    plain_latency = float(plain_data["avg_latency_ms"])
    dnssec_latency = float(dnssec_data["avg_latency_ms"])
    plain_cpu = float(plain_data["avg_cpu_percent"])
    dnssec_cpu = float(dnssec_data["avg_cpu_percent"])
    latency_overhead = float(dnssec_data["latency_overhead_ms"])
    latency_overhead_pct = float(dnssec_data["latency_overhead_percent"])
    cpu_overhead = float(dnssec_data["cpu_overhead_percent"])
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Latency comparison bar chart
    categories = ["No DNSSEC", "DNSSEC", "Overhead"]
    latencies = [plain_latency, dnssec_latency, latency_overhead]
    colors = ["blue", "red", "orange"]
    bars1 = ax1.bar(categories, latencies, color=colors, alpha=0.7)
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title(f"Latency Comparison\n(Overhead: {latency_overhead:.2f} ms, {latency_overhead_pct:.1f}%)")
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
    
    # CPU comparison bar chart
    cpu_values = [plain_cpu, dnssec_cpu, cpu_overhead]
    bars2 = ax2.bar(categories, cpu_values, color=colors, alpha=0.7)
    ax2.set_ylabel("CPU Usage (%)")
    ax2.set_title(f"CPU Usage Comparison\n(Overhead: {cpu_overhead:.2f}%)")
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig("performance_overhead_summary.png", dpi=150)
    print("[+] Saved performance_overhead_summary.png")

def main():
    print("=" * 70)
    print("Generating Performance Overhead Plots")
    print("=" * 70)
    print()
    
    plot_latency_comparison()
    plot_overhead_summary()
    
    print("\n[+] All plots generated successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


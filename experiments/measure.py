import subprocess
import time
import csv

N_TRIALS = 100
TARGET_NAME = "www.victim.local"
PLAIN_RESOLVER = "10.5.0.53"
DNSSEC_RESOLVER = "10.5.0.54"
FAKE_IP = "10.5.0.99"

def run_dig(resolver: str):
    cmd = [
        "docker", "run", "--rm", "--network", "dnslab_dnslab",
        "debian:stable-slim",
        "bash", "-c",
        "apt-get update >/dev/null && apt-get install -y dnsutils >/dev/null && "
        f"dig @{resolver} {TARGET_NAME} +short"
    ]
    t0 = time.time()
    out = subprocess.run(cmd, capture_output=True, text=True)
    t1 = time.time()
    return out.stdout.strip(), (t1 - t0)*1000.0

def restart_service(service: str):
    subprocess.run(["docker", "restart", service], check=False)

def measure_mode(resolver_ip: str, attacker_service: str, mode_label: str):
    rows = []
    for i in range(1, N_TRIALS+1):
        print(f"[{mode_label}] Trial {i}/{N_TRIALS}")
        restart_service(attacker_service)
        time.sleep(1)

        t_start = time.time()
        poisoned = False
        time_to_poison_ms = None

        for _ in range(30):
            ans, latency_ms = run_dig(resolver_ip)
            if ans == FAKE_IP:
                poisoned = True
                time_to_poison_ms = (time.time() - t_start)*1000.0
                break

        rows.append({
            "mode": mode_label,
            "trial": i,
            "poisoned": int(poisoned),
            "time_to_poison_ms": time_to_poison_ms if poisoned else "",
        })

    return rows

def main():
    all_rows = []
    all_rows += measure_mode(PLAIN_RESOLVER, "attacker_plain", "no_dnssec")
    all_rows += measure_mode(DNSSEC_RESOLVER, "attacker_dnssec", "dnssec")

    with open("measurements.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["mode","trial","poisoned","time_to_poison_ms"])
        writer.writeheader()
        writer.writerows(all_rows)

    print("[+] Wrote measurements.csv")

if __name__ == "__main__":
    main()


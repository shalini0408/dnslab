# DNS Cache Poisoning vs DNSSEC Lab (Docker + Python + Angular)

This repository implements a reproducible DNS security lab:

- Non-DNSSEC resolver (dnsmasq) vulnerable to cache poisoning.
- DNSSEC-enabled authoritative server (BIND9) + validating resolver (Unbound).
- Python/Scapy attacker that forges DNS replies.
- PCAP-based analysis with tcpdump/Wireshark.
- Empirical measurements (CSV + plots).
- Anomaly detector scanning PCAPs.
- Optional Angular dashboard (see `frontend/README-angular-setup.md`) via a Flask `control_api`.

## 1. Prerequisites (Windows)

- Docker Desktop
- Python 3.x (for experiments + detector)
- Node.js + Angular CLI (for the dashboard)
- Wireshark (optional but recommended)

## 2. Run the lab

From the repo root:

```powershell
docker-compose up --build
```

## 3. Run Experiments

### Attack Success Rate Measurement
```powershell
cd experiments
python measure.py
python plot_results.py
```

### Performance Overhead Measurement
```powershell
cd experiments
python measure_performance.py
python plot_performance.py
```

This measures:
- Latency overhead (response time with vs without DNSSEC)
- CPU overhead (CPU usage during DNSSEC validation)


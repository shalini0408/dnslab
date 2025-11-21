from scapy.all import rdpcap, DNS, IP
import sys
from collections import defaultdict

def analyze_pcap(pcap_file: str, auth_ip: str = "10.5.0.2"):
    packets = rdpcap(pcap_file)
    suspicious = []

    responses_by_qname = defaultdict(list)

    for pkt in packets:
        if pkt.haslayer(DNS) and pkt[DNS].qr == 1:
            src = pkt[IP].src
            qname = pkt[DNS].qd.qname.decode(errors="ignore") if pkt[DNS].qd else "?"
            an = pkt[DNS].an
            rdata = ""
            if an and hasattr(an, "rdata"):
                rdata = str(an.rdata)
            responses_by_qname[qname].append((src, rdata, pkt.time))

    for qname, entries in responses_by_qname.items():
        non_auth = [e for e in entries if e[0] != auth_ip]
        if len(non_auth) > 5:
            suspicious.append((qname, len(non_auth)))

    print("=== Suspicious DNS activity ===")
    if not suspicious:
        print("No obvious anomalies detected.")
    else:
        for qname, count in suspicious:
            print(f"{qname}: {count} non-authoritative responses observed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dns_detector.py <pcap_file>")
        sys.exit(1)
    analyze_pcap(sys.argv[1])


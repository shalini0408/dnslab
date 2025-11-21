from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import json
import socket

app = Flask(__name__)
CORS(app)

RESOLVERS = {
    "plain": "10.5.0.53",
    "dnssec": "10.5.0.54"
}

# State management
dnssec_enabled = False  # False = plain, True = dnssec
attack_running = {"plain": False, "dnssec": False}

def run(cmd: str) -> str:
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return out.stdout or out.stderr

def resolve_dns(hostname: str, resolver_ip: str) -> str:
    """Resolve DNS using specific resolver."""
    try:
        cmd = [
            "docker", "run", "--rm", "--network", "dnslab_dnslab",
            "debian:stable-slim",
            "bash", "-c",
            "apt-get update >/dev/null 2>&1 && apt-get install -y dnsutils >/dev/null 2>&1 && "
            f"dig @{resolver_ip} {hostname} +short"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/dig")
def dig():
    resolver = request.args.get("resolver", "plain")
    ip = RESOLVERS.get(resolver, RESOLVERS["plain"])
    output = run(f"dig @{ip} www.victim.local +dnssec")
    return jsonify({"resolver": resolver, "output": output})

@app.get("/tcpdump")
def tcpdump():
    resolver = request.args.get("resolver", "plain")
    ip = RESOLVERS.get(resolver, RESOLVERS["plain"])
    cmd = (
        "docker run --rm --network dnslab_dnslab --cap-add=NET_ADMIN "
        f"nicolaka/netshoot tcpdump -nn -i eth0 host {ip} and udp port 53 -c 20"
    )
    output = run(cmd)
    return jsonify({"resolver": resolver, "tcpdump": output})

@app.get("/logs")
def logs():
    resolver = request.args.get("resolver", "plain")
    service = "resolver_plain" if resolver == "plain" else "resolver_dnssec"
    container_name = f"dnslab-{service}-1"
    output = run(f"docker logs {container_name} --tail=50")
    return jsonify({"resolver": resolver, "logs": output})

@app.post("/attack/start")
def start_attack():
    mode = request.args.get("mode", "plain")
    attacker = "dnslab-attacker_plain-1" if mode == "plain" else "dnslab-attacker_dnssec-1"
    run(f"docker start {attacker}")
    return jsonify({"status": f"{attacker} started"})

@app.post("/attack/stop")
def stop_attack():
    run("docker stop dnslab-attacker_plain-1")
    run("docker stop dnslab-attacker_dnssec-1")
    return jsonify({"status": "all attackers stopped"})

@app.get("/dnssec/status")
def dnssec_status():
    output = run("docker logs dnslab-resolver_dnssec-1 | grep -i dnssec || echo 'no dnssec logs yet'")
    return jsonify({"status": output})

# New endpoints for dashboard

@app.get("/resolver/current")
def get_current_resolver():
    """Get current resolver IP based on DNSSEC state."""
    resolver_type = "dnssec" if dnssec_enabled else "plain"
    return jsonify({
        "dnssec_enabled": dnssec_enabled,
        "resolver_type": resolver_type,
        "resolver_ip": RESOLVERS[resolver_type],
        "resolver_name": "DNSSEC Resolver (Unbound)" if dnssec_enabled else "Plain Resolver (dnsmasq)"
    })

@app.post("/dnssec/toggle")
def toggle_dnssec():
    """Toggle DNSSEC on/off."""
    global dnssec_enabled
    data = request.get_json() or {}
    dnssec_enabled = data.get("enabled", not dnssec_enabled)
    return jsonify({
        "dnssec_enabled": dnssec_enabled,
        "resolver_ip": RESOLVERS["dnssec" if dnssec_enabled else "plain"],
        "message": f"DNSSEC {'enabled' if dnssec_enabled else 'disabled'}"
    })

@app.get("/dns/resolve")
def resolve_dns_endpoint():
    """Resolve DNS using current resolver."""
    hostname = request.args.get("hostname", "www.victim.local")
    resolver_type = "dnssec" if dnssec_enabled else "plain"
    resolver_ip = RESOLVERS[resolver_type]
    
    ip = resolve_dns(hostname, resolver_ip)
    
    return jsonify({
        "hostname": hostname,
        "resolved_ip": ip,
        "resolver_type": resolver_type,
        "resolver_ip": resolver_ip,
        "dnssec_enabled": dnssec_enabled,
        "is_poisoned": ip == "10.5.0.99",
        "is_correct": ip == "10.5.0.10"
    })

@app.get("/attack/status")
def get_attack_status():
    """Get current attack status."""
    return jsonify({
        "plain": attack_running["plain"],
        "dnssec": attack_running["dnssec"],
        "any_running": attack_running["plain"] or attack_running["dnssec"]
    })

@app.post("/cache/clear")
def clear_cache():
    """Clear resolver cache by restarting service."""
    resolver_type = request.args.get("resolver", "plain")
    service = "resolver_plain" if resolver_type == "plain" else "resolver_dnssec"
    
    try:
        run(f"docker-compose restart {service}")
        return jsonify({"status": "success", "message": f"Cache cleared for {service}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.get("/proxy/website")
def proxy_website():
    """Proxy website through selected resolver."""
    hostname = request.args.get("hostname", "www.victim.local")
    resolver_type = "dnssec" if dnssec_enabled else "plain"
    resolver_ip = RESOLVERS[resolver_type]
    
    # Resolve DNS
    ip = resolve_dns(hostname, resolver_ip)
    
    # Determine which website to serve
    if ip == "10.5.0.99":
        # Poisoned - serve fake website
        website_url = "http://10.5.0.99"
    else:
        # Correct - serve real website
        website_url = "http://10.5.0.10"
    
    # Fetch website content
    try:
        import requests
        response = requests.get(website_url, timeout=5)
        return response.text, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        # Fallback: return redirect or error page
        return f"""
        <html>
        <head><title>Website Proxy</title></head>
        <body>
            <h1>Website Proxy</h1>
            <p>Resolved IP: {ip}</p>
            <p>Website URL: {website_url}</p>
            <p>Error: {str(e)}</p>
            <iframe src="{website_url}" width="100%" height="600px"></iframe>
        </body>
        </html>
        """, 200, {'Content-Type': 'text/html'}

@app.get("/plot/data")
def get_plot_data():
    """Get plot data as JSON."""
    plot_type = request.args.get("type", "attack")  # "attack" or "performance"
    
    if plot_type == "attack":
        # Read measurements.csv
        csv_path = "/app/measurements.csv"
        if os.path.exists(csv_path):
            import csv
            data = {"no_dnssec": 0, "dnssec": 0}
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("poisoned") == "1":
                        mode = row.get("mode", "")
                        if mode in data:
                            data[mode] += 1
            return jsonify(data)
        else:
            return jsonify({"no_dnssec": 0, "dnssec": 0, "note": "No data file found"})
    
    elif plot_type == "performance":
        # Read performance_overhead.csv
        csv_path = "/app/performance_overhead.csv"
        if os.path.exists(csv_path):
            import csv
            data = {}
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    resolver = row.get("resolver", "")
                    data[resolver] = {
                        "avg_latency_ms": float(row.get("avg_latency_ms", 0)),
                        "avg_cpu_percent": float(row.get("avg_cpu_percent", 0)),
                        "latency_overhead_ms": float(row.get("latency_overhead_ms", 0)),
                        "cpu_overhead_percent": float(row.get("cpu_overhead_percent", 0))
                    }
            return jsonify(data)
        else:
            return jsonify({"note": "No performance data file found"})
    
    return jsonify({"error": "Invalid plot type"}), 400

@app.post("/attack/start")
def start_attack():
    """Start attack against selected resolver."""
    mode = request.args.get("mode", None)
    if mode is None:
        mode = "dnssec" if dnssec_enabled else "plain"
    
    attacker = "attacker_plain" if mode == "plain" else "attacker_dnssec"
    container_name = f"dnslab-{attacker}-1"
    
    try:
        # Check if container exists and start it
        result = run(f"docker ps -a --filter name={container_name} --format '{{{{.Names}}}}'")
        if container_name in result:
            run(f"docker start {container_name}")
            attack_running[mode] = True
            return jsonify({"status": "success", "message": f"{attacker} started", "mode": mode})
        else:
            return jsonify({"status": "error", "message": f"Container {container_name} not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.post("/attack/stop")
def stop_attack():
    """Stop all attacks."""
    try:
        run("docker stop dnslab-attacker_plain-1 dnslab-attacker_dnssec-1 2>/dev/null || true")
        attack_running["plain"] = False
        attack_running["dnssec"] = False
        return jsonify({"status": "success", "message": "All attackers stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


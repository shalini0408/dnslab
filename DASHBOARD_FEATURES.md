# Dashboard Features Explanation

## 1. TCPDUMP - Network Traffic Capture

### How TCPDUMP Works:
**Current Implementation:**
```python
# In control_api/app.py
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
```

**What it does:**
1. **Creates a temporary container** using `nicolaka/netshoot` (network troubleshooting image)
2. **Captures DNS traffic** (`udp port 53`) going to/from the selected resolver
3. **Shows 20 packets** (`-c 20`) - DNS queries and responses
4. **Returns the output** as text to display in dashboard

**What you'll see in tcpdump output:**
```
20:30:45.123456 IP 10.5.0.60.53 > 10.5.0.53.53: UDP, length 64
20:30:45.123789 IP 10.5.0.53.53 > 10.5.0.2.53: UDP, length 72
20:30:45.124012 IP 10.5.0.2.53 > 10.5.0.53.53: UDP, length 88
20:30:45.124234 IP 10.5.0.60.53 > 10.5.0.53.53: UDP, length 64  <-- Forged response!
```

**Dashboard Usage:**
- **Button**: "Show Network Traffic" or "Capture Packets"
- **Display**: Scrollable text area showing packet capture
- **Purpose**: Visual proof of attack - shows forged DNS responses being sent
- **When to use**: During attack to see the attacker sending spoofed packets

---

## 2. LOGS - Service Activity Monitoring

### How LOGS Work:
**Current Implementation:**
```python
@app.get("/logs")
def logs():
    resolver = request.args.get("resolver", "plain")
    service = "dnslab-resolver_plain-1" if resolver == "plain" else "dnslab-resolver_dnssec-1"
    output = run(f"docker logs {service} --tail=50")
    return jsonify({"resolver": resolver, "logs": output})
```

**What it shows:**
- **Resolver logs**: DNS query processing, cache hits/misses, DNSSEC validation results
- **Attacker logs**: Forged packet transmission (TXID numbers)
- **Last 50 lines** of log output

**What you'll see in logs:**

**Plain Resolver (dnsmasq):**
```
dnsmasq[1]: query[A] www.victim.local from 10.5.0.40
dnsmasq[1]: forwarded www.victim.local to 10.5.0.2
dnsmasq[1]: reply www.victim.local is 10.5.0.10
dnsmasq[1]: cached www.victim.local is 10.5.0.99  <-- Poisoned!
```

**DNSSEC Resolver (Unbound):**
```
[123456] info: validation failure www.victim.local A IN
[123457] info: bogus response rejected
[123458] info: query www.victim.local A IN validated
```

**Dashboard Usage:**
- **Button**: "Show Resolver Logs" or "View Activity"
- **Display**: Auto-updating log viewer (like terminal output)
- **Purpose**: See what the resolver is doing, validation failures, cache updates
- **When to use**: Real-time monitoring during attack

---

## 3. PLOTS - Attack Statistics Visualization

### How PLOTS Work:
**Current Implementation:**
```python
# experiments/plot_results.py
# Reads measurements.csv and creates bar chart
plt.bar(labels, values)
plt.ylabel("Number of successful poisonings")
plt.title("Poisoning success: no DNSSEC vs DNSSEC")
plt.savefig("poison_success.png")
```

**What it shows:**
- **Bar chart** comparing:
  - Number of successful poisonings (DNSSEC OFF)
  - Number of successful poisonings (DNSSEC ON) - should be 0
- **Visual comparison** of attack effectiveness

**Dashboard Integration:**
- **Option A**: Run plot script server-side, serve image
  ```python
  @app.get("/plot")
  def get_plot():
      # Run plot_results.py
      # Return image as base64 or file path
  ```
- **Option B**: Generate plot data, let frontend create chart (Chart.js, D3.js)
  ```python
  @app.get("/plot/data")
  def get_plot_data():
      # Read measurements.csv
      # Return JSON with data points
      return jsonify({"no_dnssec": 15, "dnssec": 0})
  ```

**Dashboard Usage:**
- **Button**: "Show Statistics" or "View Results"
- **Display**: Chart/graph showing attack success rates
- **Purpose**: Visual proof that DNSSEC prevents poisoning
- **When to use**: After running multiple attack trials

---

## 4. IFRAME - Website Display (Option A)

### How IFRAME Works:
**Implementation:**
```html
<!-- In Angular dashboard -->
<iframe 
  [src]="websiteUrl" 
  width="100%" 
  height="600px"
  [title]="'Victim Website - ' + (dnssecEnabled ? 'Protected' : 'Vulnerable')">
</iframe>
```

**Challenge:**
- Browser's DNS resolution uses **system DNS settings**, not our Docker resolvers
- Need to make browser use our resolver

**Solutions:**

**Option 1: Proxy Approach (Recommended)**
```python
# Add to control_api/app.py
@app.route('/proxy/<path:url>')
def proxy(url):
    # Resolve DNS using selected resolver
    # Fetch website content
    # Return to iframe
```

**Option 2: DNS Override (Complex)**
- Use browser extension or local DNS proxy
- Route `www.victim.local` to our resolver

**Option 3: Direct IP Access**
```html
<!-- Show IP address, let user click to open -->
<div>
  <p>Resolved IP: {{ resolvedIp }}</p>
  <iframe [src]="'http://' + resolvedIp" ...></iframe>
</div>
```

**Dashboard Layout:**
```
┌─────────────────────────────────────────┐
│  DNS Cache Poisoning Lab Dashboard      │
├─────────────────────────────────────────┤
│  [DNSSEC: OFF ▼]  [Start Attack]       │
│  [Stop Attack]    [Show Logs]          │
│  [Show TCPDUMP]   [Show Plot]          │
├─────────────────────────────────────────┤
│  Current Resolver: 10.5.0.53 (Plain)   │
│  Resolved IP: 10.5.0.99 (POISONED!)    │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐ │
│  │                                   │ │
│  │   IFRAME: www.victim.local        │ │
│  │   (Shows fake website when        │ │
│  │    poisoned, real when protected) │ │
│  │                                   │ │
│  └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Logs/TCPDUMP/Plot panels (tabs)       │
└─────────────────────────────────────────┘
```

---

## Complete Dashboard Feature List

### Control Panel:
1. ✅ **DNSSEC Toggle** - Switch between plain/dnssec resolver
2. ✅ **Start Attack** - Begin poisoning attempt
3. ✅ **Stop Attack** - Stop all attackers
4. ✅ **Clear Cache** - Reset resolver cache

### Monitoring:
5. ✅ **Show TCPDUMP** - Network packet capture
6. ✅ **Show Logs** - Resolver/attacker activity
7. ✅ **Show Plot** - Attack statistics chart
8. ✅ **Current Status** - Resolver IP, resolved IP, attack state

### Visualization:
9. ✅ **Website Iframe** - Shows victim website
10. ✅ **DNS Result Display** - Shows current resolved IP
11. ✅ **Attack Status** - Visual indicator (safe/poisoned)

---

## Enhanced API Endpoints Needed

```python
# New endpoints to add:

@app.get("/resolver/current")
def get_current_resolver():
    # Return current resolver IP based on DNSSEC state
    pass

@app.get("/dns/resolve")
def resolve_dns():
    # Resolve www.victim.local using current resolver
    # Return IP address
    pass

@app.get("/attack/status")
def attack_status():
    # Return if attack is running, which mode
    pass

@app.post("/cache/clear")
def clear_cache():
    # Restart resolver to clear cache
    pass

@app.get("/plot/data")
def get_plot_data():
    # Return plot data as JSON
    pass

@app.get("/proxy/website")
def proxy_website():
    # Proxy website through selected resolver
    pass
```

---

## Summary

**TCPDUMP**: Shows network packets - proves attack is happening
**LOGS**: Shows resolver activity - validation failures, cache updates
**PLOTS**: Shows statistics - visual proof DNSSEC works
**IFRAME**: Shows website - visual impact of poisoning

All integrated into one dashboard for complete experiment control and visualization!


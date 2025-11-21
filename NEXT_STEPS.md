# Next Steps - Implementation Roadmap

## ✅ Completed
1. ✅ DNS infrastructure (auth server, resolvers, attackers)
2. ✅ Attack measurement scripts (100 trials)
3. ✅ Performance overhead measurement (latency + CPU)
4. ✅ Detector for PCAP analysis
5. ✅ Basic Control API (Flask)

---

## 🎯 Next Steps (In Order)

### **Step 1: Create Web Servers** (Priority: HIGH)
**Purpose:** Visual demonstration of DNS poisoning (real vs fake website)

**What to create:**
- **Real Website** (10.5.0.10) - Legitimate victim website
- **Fake Website** (10.5.0.99) - Attacker's fake website

**Files needed:**
- `websites/real/Dockerfile` - Simple HTTP server
- `websites/real/index.html` - Real website content
- `websites/fake/Dockerfile` - Simple HTTP server  
- `websites/fake/index.html` - Fake website content
- Update `docker-compose.yml` to add web servers

**Why first:** Dashboard needs websites to display in iframe

---

### **Step 2: Enhance Control API** (Priority: HIGH)
**Purpose:** Add missing endpoints for dashboard functionality

**New endpoints needed:**
- `GET /resolver/current` - Get current resolver based on DNSSEC state
- `GET /dns/resolve` - Resolve DNS using current resolver, return IP
- `GET /attack/status` - Check if attack is running
- `POST /cache/clear` - Clear resolver cache
- `GET /proxy/website` - Proxy website through selected resolver (for iframe)
- `GET /plot/data` - Return plot data as JSON
- `POST /dnssec/toggle` - Toggle DNSSEC on/off (state management)

**Files to modify:**
- `control_api/app.py` - Add new endpoints

**Why second:** Dashboard needs these APIs to function

---

### **Step 3: Build Angular Dashboard** (Priority: HIGH)
**Purpose:** Complete user interface for experiment control

**Components needed:**
- Dashboard component with:
  - DNSSEC toggle switch
  - Attack start/stop buttons
  - Current status display (resolver IP, resolved IP)
  - Website iframe
  - Tabs/panels for: TCPDUMP, Logs, Plots
- API service for backend communication
- Real-time updates (polling or WebSocket)

**Files to create:**
- `frontend/dns-dashboard/src/app/services/api.service.ts`
- `frontend/dns-dashboard/src/app/dashboard/dashboard.component.ts`
- `frontend/dns-dashboard/src/app/dashboard/dashboard.component.html`
- `frontend/dns-dashboard/src/app/app.component.html`

**Why third:** Final piece to complete the lab

---

## 📋 Detailed Implementation Plan

### Phase 1: Web Servers (30 min)
```
1. Create websites/real/ folder
   - Dockerfile (nginx or python http.server)
   - index.html (real website content)

2. Create websites/fake/ folder
   - Dockerfile (nginx or python http.server)
   - index.html (fake/attacker website content)

3. Update docker-compose.yml
   - Add website_real service (10.5.0.10)
   - Add website_fake service (10.5.0.99)
```

### Phase 2: Control API Enhancement (45 min)
```
1. Add state management (DNSSEC on/off)
2. Add new endpoints:
   - /resolver/current
   - /dns/resolve
   - /attack/status
   - /cache/clear
   - /proxy/website
   - /plot/data
   - /dnssec/toggle
3. Test all endpoints
```

### Phase 3: Angular Dashboard (2-3 hours)
```
1. Create Angular app (if not exists)
2. Build API service
3. Build dashboard component
4. Add real-time updates
5. Style and polish
```

---

## 🚀 Quick Start (Recommended Order)

**Option A: Full Implementation**
1. Create web servers
2. Enhance Control API
3. Build Angular dashboard

**Option B: Incremental (Test as you go)**
1. Create web servers → Test manually
2. Enhance Control API → Test with curl/Postman
3. Build Angular dashboard → Test full flow

---

## 📝 Current Status

| Component | Status | Priority |
|-----------|--------|----------|
| DNS Infrastructure | ✅ Complete | - |
| Attack Measurement | ✅ Complete | - |
| Performance Measurement | ✅ Complete | - |
| Detector | ✅ Complete | - |
| **Web Servers** | ❌ **Missing** | **HIGH** |
| **Control API Enhancement** | ⚠️ **Partial** | **HIGH** |
| **Angular Dashboard** | ❌ **Not Built** | **HIGH** |

---

## 🎯 Recommendation

**Start with Step 1 (Web Servers)** because:
- Quick to implement (simple HTTP servers)
- Needed for visual demonstration
- Can test immediately
- Unblocks dashboard development

**Then Step 2 (API Enhancement)** because:
- Dashboard depends on these endpoints
- Can test independently before dashboard

**Finally Step 3 (Dashboard)** because:
- Requires both web servers and API
- Final integration step

---

## Ready to Start?

Would you like me to:
1. **Create the web servers now?** (Recommended first step)
2. **Enhance the Control API?**
3. **Build the Angular dashboard?**
4. **Do all three in sequence?**

Let me know which you'd like to tackle first!


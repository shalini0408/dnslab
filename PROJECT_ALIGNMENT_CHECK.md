# Project Alignment Check

## Comparison: Project Document vs Current Implementation

### ✅ **ALIGNED - What We Have Correctly:**

#### 1. **Empirical Measurements (CSV + Plots)**
**Project Requirement:**
- Time-to-poison and success-rate (no DNSSEC) vs. failure rates (with DNSSEC)
- CSV output + plots

**Our Implementation:**
- ✅ `experiments/measure.py` - Measures time-to-poison and success rate
- ✅ `experiments/plot_results.py` - Creates bar charts
- ✅ CSV output: `measurements.csv` with columns: `mode`, `trial`, `poisoned`, `time_to_poison_ms`
- ✅ Compares `no_dnssec` vs `dnssec` modes

**Status:** ✅ **ALIGNED**

---

#### 2. **Detector Prototype (Logs/PCAPs)**
**Project Requirement:**
- Detector that scans logs/PCAPs for anomalous responses

**Our Implementation:**
- ✅ `detector/dns_detector.py` - Scans PCAP files for suspicious DNS activity
- ✅ Detects non-authoritative responses
- ✅ Flags anomalous patterns

**Status:** ✅ **ALIGNED**

---

#### 3. **Tools: Wireshark/tcpdump**
**Project Requirement:**
- Wireshark/tcpdump for network traffic analysis

**Our Implementation:**
- ✅ `control_api/app.py` - `/tcpdump` endpoint using tcpdump
- ✅ Captures DNS traffic (UDP port 53)
- ✅ Uses `nicolaka/netshoot` container for packet capture

**Status:** ✅ **ALIGNED**

---

#### 4. **Logs Analysis**
**Project Requirement:**
- Analysis of logs for detection

**Our Implementation:**
- ✅ `control_api/app.py` - `/logs` endpoint
- ✅ Shows resolver logs (dnsmasq/Unbound)
- ✅ Shows attacker logs
- ✅ Detector can analyze logs (mentioned in project)

**Status:** ✅ **ALIGNED**

---

#### 5. **Dashboard (Angular + Flask)**
**Project Requirement:**
- Presentation/demonstration interface

**Our Implementation:**
- ✅ `control_api/` - Flask backend with REST API
- ✅ `frontend/` - Angular setup instructions
- ✅ Dashboard controls: attack, logs, tcpdump, plots

**Status:** ✅ **ALIGNED**

---

### ⚠️ **PARTIALLY ALIGNED - Needs Enhancement:**

#### 6. **Number of Trials**
**Project Requirement:**
- Run N-trial experiments (50-200 trials)

**Our Implementation:**
- ⚠️ `N_TRIALS = 30` in `experiments/measure.py`
- Should be 50-200 trials

**Status:** ⚠️ **NEEDS UPDATE** - Should increase to 50-200 trials

---

### ❌ **MISSING - Not Yet Implemented:**

#### 7. **DNSSEC Performance Overhead Measurement**
**Project Requirement:**
- Measure DNSSEC validation overhead (latency and CPU)

**Our Implementation:**
- ❌ **NOT IMPLEMENTED** - We measure time-to-poison but not:
  - Latency overhead of DNSSEC validation
  - CPU overhead comparison (with vs without DNSSEC)

**What's Missing:**
- Latency measurement: Compare response time with DNSSEC vs without
- CPU usage measurement: Monitor CPU during DNSSEC validation
- Performance metrics in CSV output

**Status:** ❌ **MISSING** - Need to add performance overhead measurement

---

## Summary Table

| Requirement | Status | Notes |
|------------|--------|-------|
| CSV + Plots (time-to-poison, success-rate) | ✅ ALIGNED | Working correctly |
| Detector (logs/PCAPs) | ✅ ALIGNED | `detector/dns_detector.py` exists |
| tcpdump/Wireshark | ✅ ALIGNED | Integrated in API |
| Logs analysis | ✅ ALIGNED | API endpoint exists |
| Dashboard | ✅ ALIGNED | Flask + Angular planned |
| N-trials (50-200) | ⚠️ PARTIAL | Currently 30, should be 50-200 |
| **DNSSEC overhead (latency/CPU)** | ❌ **MISSING** | **Not implemented** |

---

## Required Changes

### 1. **Increase Trial Count** (Quick Fix)
```python
# experiments/measure.py
N_TRIALS = 100  # Changed from 30 to 100 (within 50-200 range)
```

### 2. **Add Performance Overhead Measurement** (New Feature)
Need to add:
- **Latency measurement**: Compare DNS response time with/without DNSSEC
- **CPU measurement**: Monitor CPU usage during validation
- **New CSV columns**: `latency_ms`, `cpu_percent`, `dnssec_overhead_ms`

**New script needed:** `experiments/measure_performance.py`
- Measure baseline latency (no DNSSEC)
- Measure latency with DNSSEC
- Calculate overhead
- Monitor CPU usage

---

## Recommendation

**Before making changes, we should:**

1. ✅ **Keep current implementation** - It's mostly aligned
2. ⚠️ **Update trial count** - Change 30 → 100 (or make configurable)
3. ❌ **Add performance overhead measurement** - This is the main missing piece

**Priority:**
- **High**: Add DNSSEC performance overhead measurement (latency + CPU)
- **Medium**: Increase trial count to 50-200
- **Low**: Everything else is good

---

## Next Steps

1. **Confirm**: Do we need to add performance overhead measurement now?
2. **Update**: Should we change N_TRIALS to 100?
3. **Proceed**: Continue with dashboard implementation (it's aligned with project)


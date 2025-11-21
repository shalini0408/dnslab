# Changes Summary - Performance Overhead & Trial Count

## ✅ Completed Changes

### 1. Updated Trial Count
**File:** `experiments/measure.py`
- **Changed:** `N_TRIALS = 30` → `N_TRIALS = 100`
- **Reason:** Project requirement specifies 50-200 trials
- **Status:** ✅ Complete

### 2. Added Performance Overhead Measurement
**New Files Created:**

#### `experiments/measure_performance.py`
- Measures latency overhead (response time with vs without DNSSEC)
- Measures CPU overhead (CPU usage during DNSSEC validation)
- Runs 100 trials for each resolver
- Outputs:
  - `performance_overhead.csv` - Summary statistics
  - `performance_latencies.csv` - Raw latency data for plotting

**Features:**
- ✅ Latency measurement (average, min, max)
- ✅ CPU monitoring using `docker stats`
- ✅ Warm-up queries to avoid cold start effects
- ✅ Calculates overhead (absolute and percentage)
- ✅ Threaded CPU monitoring for accurate sampling

#### `experiments/plot_performance.py`
- Creates visualization plots from performance data
- Generates:
  - `performance_latency_comparison.png` - Box plots and histograms
  - `performance_overhead_summary.png` - Bar charts showing overhead

**Features:**
- ✅ Latency comparison (box plot + histogram)
- ✅ CPU comparison (bar chart)
- ✅ Overhead visualization

### 3. Updated Documentation
**File:** `README.md`
- Added section on running performance experiments
- Documented new scripts and their outputs

---

## Usage

### Run Attack Success Rate Measurement (100 trials)
```powershell
cd experiments
python measure.py
python plot_results.py
```

### Run Performance Overhead Measurement (100 trials)
```powershell
cd experiments
python measure_performance.py
python plot_performance.py
```

---

## Output Files

### Attack Success Rate:
- `measurements.csv` - Trial results (poisoned, time-to-poison)
- `poison_success.png` - Bar chart comparison

### Performance Overhead:
- `performance_overhead.csv` - Summary statistics
  - Columns: resolver, avg_latency_ms, min_latency_ms, max_latency_ms, avg_cpu_percent, max_cpu_percent, latency_overhead_ms, latency_overhead_percent, cpu_overhead_percent
- `performance_latencies.csv` - Raw latency data
  - Columns: resolver, trial, latency_ms
- `performance_latency_comparison.png` - Latency visualization
- `performance_overhead_summary.png` - Overhead summary charts

---

## Project Alignment Status

| Requirement | Status | Notes |
|------------|--------|-------|
| N-trials (50-200) | ✅ **COMPLETE** | Updated to 100 trials |
| Latency overhead | ✅ **COMPLETE** | New script measures this |
| CPU overhead | ✅ **COMPLETE** | New script measures this |
| CSV + Plots | ✅ **COMPLETE** | Both attack and performance |

---

## Next Steps

The project now fully aligns with the requirements. You can:
1. Run both measurement scripts to collect data
2. Generate all plots for analysis
3. Proceed with dashboard implementation
4. Use the data for final report and presentation


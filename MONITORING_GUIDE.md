# 🔍 Performance Monitoring & Segfault Detection Guide

## What's Been Added

Your application now has **automatic performance monitoring** that will alert you when operations are taking too long (potential segfault causes).

## 📊 Alert Levels

### 🚨 CRITICAL (>5 seconds)
```
🚨 CRITICAL: PHIVOLCS fetch took 7.23s - POTENTIAL SEGFAULT RISK!
🚨 VERY SLOW REQUEST: GET /api/earthquakes/phivolcs took 8.45s (threshold: 5.0s) - POTENTIAL SEGFAULT RISK!
```

**What this means:**
- Operation is taking dangerously long
- High risk of segfault if this continues
- Likely cause: Network timeout, HTML parsing issue, or C library problem

**Action:**
1. Check Grafana Cloud Profiles flame graph at this time
2. Look for which C library is consuming CPU
3. Check if segfault happens shortly after

### ⚠️ WARNING (>2 seconds)
```
⚠️  SLOW: PHIVOLCS fetch took 3.12s
⚠️  SLOW REQUEST: GET /api/earthquakes/usgs took 2.8s (threshold: 2.0s)
```

**What this means:**
- Operation is slower than normal
- Not immediate danger, but monitor for patterns
- May indicate network issues or API slowdown

**Action:**
1. Monitor if this becomes frequent
2. Check if cache is working properly
3. Verify external APIs are responding

### ✓ NORMAL (<2 seconds)
```
✓ PHIVOLCS fetch completed in 1.23s
✓ GET /api/weather completed in 0.845s
```

**What this means:**
- Everything is working normally
- Performance is healthy

## 🔎 How to Monitor

### 1. Watch Logs in Real-Time

```bash
# On your remote server
tail -f /path/to/app.log | grep -E "CRITICAL|SLOW|ERROR"
```

Or if running with `python3 app.py`:
```bash
python3 app.py 2>&1 | grep -E "CRITICAL|SLOW|ERROR"
```

### 2. Search for Critical Issues

```bash
# Find all critical performance issues
grep "CRITICAL" app.log

# Find all slow operations
grep "SLOW" app.log

# Find operations before a crash (if crash happened at 14:30)
grep "14:2[0-9]" app.log | grep -E "CRITICAL|SLOW"
```

### 3. Check Response Times

Every HTTP response now includes a header showing how long it took:
```
X-Response-Time: 1.234s
```

You can see this in browser DevTools → Network tab.

## 🎯 Segfault Investigation Workflow

### When a Segfault Happens:

1. **Note the exact crash time** (e.g., `2025-10-17 14:35:22`)

2. **Check logs 5-10 minutes before crash:**
   ```bash
   # If crash at 14:35, check 14:25-14:35
   grep "14:[23][0-9]" app.log | grep -E "CRITICAL|SLOW|ERROR"
   ```

3. **Look for patterns:**
   - Was there a CRITICAL alert right before crash?
   - Which endpoint was being called?
   - Was it during PHIVOLCS fetching?

4. **Check Grafana Cloud Profiles:**
   - Go to: https://misua.grafana.net/a/grafana-pyroscope-app/profiles-explorer
   - Set time range: 10 minutes before crash
   - Look at flame graph
   - Identify which function was consuming CPU

5. **Correlate logs with flame graph:**
   - If logs show "CRITICAL: PHIVOLCS fetch took 8s"
   - AND flame graph shows high CPU in `lxml` or `urllib3`
   - Then you've found the culprit!

## 📋 Common Patterns to Watch For

### Pattern 1: Repeated CRITICAL Alerts
```
14:30:15 🚨 CRITICAL: PHIVOLCS fetch took 6.2s
14:30:45 🚨 CRITICAL: PHIVOLCS fetch took 7.1s
14:31:15 🚨 CRITICAL: PHIVOLCS fetch took 8.5s
[SEGFAULT]
```
**Diagnosis:** PHIVOLCS website is slow or returning malformed HTML

### Pattern 2: Sudden Spike Then Crash
```
14:30:00 ✓ PHIVOLCS fetch completed in 1.2s
14:30:30 ✓ PHIVOLCS fetch completed in 1.3s
14:31:00 🚨 CRITICAL: PHIVOLCS fetch took 12.8s
[SEGFAULT]
```
**Diagnosis:** Specific HTML content triggered parser bug

### Pattern 3: Network Errors Before Crash
```
14:30:00 ⚠ Network error fetching PHIVOLCS data: Timeout
14:30:30 ⚠ Network error fetching PHIVOLCS data: SSL Error
14:31:00 🚨 CRITICAL: PHIVOLCS fetch took 15.2s
[SEGFAULT]
```
**Diagnosis:** SSL/TLS library (OpenSSL) causing segfault

## 🛠️ Adjusting Alert Thresholds

If you're getting too many alerts, edit `utils/performance_monitor.py`:

```python
# Make alerts less sensitive
SLOW_REQUEST_THRESHOLD = 3.0  # Was 2.0
VERY_SLOW_REQUEST_THRESHOLD = 8.0  # Was 5.0
```

If you want more sensitive alerts:
```python
# Make alerts more sensitive
SLOW_REQUEST_THRESHOLD = 1.0  # Was 2.0
VERY_SLOW_REQUEST_THRESHOLD = 3.0  # Was 5.0
```

## 📊 Example Investigation

### Scenario: Segfault at 2025-10-17 14:35:22

**Step 1: Check logs**
```bash
grep "14:[23][0-9]" app.log | tail -20
```

**Output:**
```
14:32:15 ✓ PHIVOLCS fetch completed in 1.2s
14:32:45 ✓ PHIVOLCS fetch completed in 1.3s
14:33:15 ⚠️  SLOW: PHIVOLCS fetch took 3.4s
14:33:45 🚨 CRITICAL: PHIVOLCS fetch took 7.8s - POTENTIAL SEGFAULT RISK!
14:34:15 🚨 CRITICAL: PHIVOLCS fetch took 9.2s - POTENTIAL SEGFAULT RISK!
14:34:45 🚨 CRITICAL: PHIVOLCS fetch took 11.5s - POTENTIAL SEGFAULT RISK!
[CRASH]
```

**Step 2: Check Grafana Profiles**
- Time: 14:30 - 14:35
- Flame graph shows: `html/parser.py` consuming 8 minutes
- Also shows: `bs4/builder/` taking 5 minutes

**Step 3: Diagnosis**
- PHIVOLCS website returned malformed HTML
- BeautifulSoup parser got stuck parsing it
- Eventually caused segfault in C extension

**Step 4: Solution**
- Add timeout to HTML parsing
- Add validation before parsing
- Consider switching to different parser

## 🎯 Quick Reference

| Alert | Threshold | Action |
|-------|-----------|--------|
| 🚨 CRITICAL | >5s | Check Grafana immediately, potential crash |
| ⚠️ WARNING | >2s | Monitor for patterns |
| ✓ NORMAL | <2s | All good |

## 📞 Need Help?

If you see repeated CRITICAL alerts:
1. Take a screenshot of the logs
2. Check Grafana Cloud Profiles flame graph
3. Note which endpoint/function is slow
4. Check if segfault happens after these alerts

---

**The monitoring is now active!** Watch your logs for CRITICAL alerts - they'll tell you exactly what's about to cause a segfault. 🎯

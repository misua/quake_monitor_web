# Profiling Approaches Comparison

## Overview

This document compares different approaches for adding profiling to the Earthquake & Weather Monitor application.

## Approach Comparison Matrix

| Feature | **Pyroscope SDK (Chosen)** | Grafana Alloy + SDK | Grafana Alloy + eBPF | Local Pyroscope Server |
|---------|---------------------------|---------------------|---------------------|------------------------|
| **Setup Complexity** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Moderate | ⭐⭐ Complex | ⭐⭐⭐ Moderate |
| **Infrastructure** | None (SDK only) | Alloy container/binary | Alloy + kernel 4.9+ | Docker/binary + storage |
| **Cost** | Free (Grafana Cloud) | Free (Grafana Cloud) | Free (Grafana Cloud) | Free (self-hosted) |
| **Python Support** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **CPU Overhead** | <5% | <5% | <1% | <5% |
| **Memory Overhead** | 10-20 MB | 50-100 MB | 20-50 MB | 100+ MB |
| **GIL Tracking** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Subprocess Detection** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Multi-Language** | ❌ Python only | ✅ Yes | ✅ Yes | ✅ Yes |
| **Data Retention** | 15 days (free tier) | 15 days (free tier) | 15 days (free tier) | Unlimited (disk space) |
| **Best For** | Single Python app | Multi-app/language | System-wide profiling | Air-gapped/on-prem |

## Detailed Comparison

### 1. Pyroscope Python SDK (Direct Push) ⭐ **CHOSEN**

**How it works:**
```python
import pyroscope
pyroscope.configure(
    application_name="quake-monitor-web",
    server_address="https://profiles-prod-XXX.grafana.net",
    basic_auth_username="123456",
    basic_auth_password="glc_xxx"
)
```

**Pros:**
- ✅ Simplest setup (2 lines of code)
- ✅ No infrastructure needed
- ✅ Python-specific optimizations (GIL tracking)
- ✅ Direct push to Grafana Cloud
- ✅ Perfect for single Python app
- ✅ Lowest memory footprint

**Cons:**
- ❌ Python-only (not an issue for this app)
- ❌ Requires code changes (minimal)
- ❌ No centralized config for multiple apps

**Use Case:** ✅ **Perfect for this app** - single Python FastAPI application with low volume

---

### 2. Grafana Alloy + Pyroscope SDK (Push to Alloy)

**How it works:**
```
App (Pyroscope SDK) → Alloy (localhost:4040) → Grafana Cloud
```

**Setup:**
1. Run Alloy as sidecar/daemon
2. Configure Alloy to receive profiles
3. Point SDK to local Alloy instead of Grafana Cloud

**Pros:**
- ✅ Centralized credential management
- ✅ Can enrich profiles with infrastructure labels
- ✅ Better for multiple applications
- ✅ Reduces app's network overhead

**Cons:**
- ❌ Additional process to manage
- ❌ More complex deployment
- ❌ Higher memory usage (Alloy + SDK)
- ❌ Overkill for single app

**Use Case:** Better for microservices or multiple apps sharing Alloy

---

### 3. Grafana Alloy + eBPF Profiling

**How it works:**
```
Alloy (eBPF) → Kernel → Profile all processes → Grafana Cloud
```

**Setup:**
1. Ensure Linux kernel 4.9+
2. Run Alloy with eBPF profiling enabled
3. No code changes needed

**Pros:**
- ✅ No code changes required
- ✅ Lowest CPU overhead (<1%)
- ✅ Profiles entire system
- ✅ Works with compiled languages (C/C++, Go, Rust)
- ✅ Can profile without restarting app

**Cons:**
- ❌ Requires Linux kernel 4.9+
- ❌ No GIL tracking for Python
- ❌ Less Python-specific insights
- ❌ More complex troubleshooting
- ❌ Requires root/CAP_SYS_ADMIN

**Use Case:** Better for multi-language environments or when you can't modify code

---

### 4. Local Pyroscope Server (Self-Hosted)

**How it works:**
```
App (Pyroscope SDK) → Local Pyroscope Server → Local Storage
```

**Setup:**
1. Run Pyroscope server (Docker/binary)
2. Configure storage backend
3. Point SDK to local server

**Pros:**
- ✅ Full control over data
- ✅ Unlimited retention (disk space)
- ✅ No external dependencies
- ✅ Works in air-gapped environments

**Cons:**
- ❌ Infrastructure to manage
- ❌ Storage costs
- ❌ No built-in dashboards (need Grafana)
- ❌ Backup/HA complexity

**Use Case:** Better for on-premises or air-gapped deployments

---

## Why Pyroscope SDK (Direct Push) Was Chosen

### Decision Factors

1. **Application Profile**
   - Single Python FastAPI app
   - Low data volume (<100 samples/sec)
   - No multi-language requirements
   - Simple deployment (single instance)

2. **Operational Simplicity**
   - No additional infrastructure to manage
   - No container orchestration needed
   - Environment variable configuration
   - Easy rollback (disable via env var)

3. **Cost Efficiency**
   - Grafana Cloud free tier sufficient
   - No infrastructure costs
   - No storage management needed

4. **Python-Specific Benefits**
   - GIL tracking (important for Python performance)
   - Subprocess detection
   - Better Python stack trace resolution

5. **Time to Value**
   - 5-minute setup
   - Immediate profiling data
   - No learning curve for Alloy/eBPF

### When to Reconsider

Consider switching to **Grafana Alloy + eBPF** if:
- App grows to multiple services
- Need to profile C extensions (lxml, etc.)
- Want system-wide profiling
- Data volume exceeds free tier

Consider switching to **Local Pyroscope** if:
- Need longer retention (>15 days)
- Air-gapped deployment required
- Data sovereignty concerns

## Migration Path

If you outgrow direct SDK push:

### Step 1: Add Alloy (No Code Changes)
```yaml
# docker-compose.yml
services:
  alloy:
    image: grafana/alloy:latest
    ports:
      - "4040:4040"
    volumes:
      - ./alloy-config.yaml:/etc/alloy/config.yaml
```

### Step 2: Update SDK Config
```python
# Change server_address to local Alloy
server_address="http://localhost:4040"
# Remove basic_auth (Alloy handles it)
```

### Step 3: Configure Alloy
```yaml
# alloy-config.yaml
pyroscope.receive_http "default" {
  http {
    listen_address = "0.0.0.0"
    listen_port    = 4040
  }
  forward_to = [pyroscope.write.grafana_cloud.receiver]
}

pyroscope.write "grafana_cloud" {
  endpoint {
    url = "https://profiles-prod-XXX.grafana.net"
    basic_auth {
      username = "123456"
      password = "glc_xxx"
    }
  }
}
```

## Summary

| Approach | Setup Time | Complexity | Best For |
|----------|-----------|------------|----------|
| **SDK Direct** | 5 min | Low | Single Python app ⭐ |
| **Alloy + SDK** | 30 min | Medium | Multiple apps |
| **Alloy + eBPF** | 1 hour | High | Multi-language |
| **Local Pyroscope** | 1 hour | Medium | On-premises |

**Recommendation:** Start with **Pyroscope SDK (Direct Push)** and migrate to Alloy only if needed.

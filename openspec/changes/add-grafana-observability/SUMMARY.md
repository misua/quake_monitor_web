# Grafana Cloud Observability Integration - Summary

## Overview

This proposal adds continuous profiling to the Earthquake & Weather Monitor application using **Grafana Cloud Profiles (Pyroscope)** to diagnose intermittent segmentation faults. The solution uses Grafana Cloud's **free tier** with direct SDK push (no local infrastructure needed).

## Key Benefits

✅ **Zero Infrastructure Cost**: Uses Grafana Cloud free tier (15 days retention, 50GB storage)  
✅ **Minimal Overhead**: <5% CPU impact with 100Hz sampling  
✅ **Simple Setup**: Direct Python SDK push, no Alloy collector needed  
✅ **Segfault Debugging**: Captures CPU/memory patterns leading to crashes  
✅ **Non-Invasive**: Optional profiling via environment variable, no business logic changes  

## What You Get

### 1. Continuous Profiling
- CPU usage flame graphs
- Memory allocation tracking
- Thread behavior and GIL contention analysis
- Stack traces at time of high resource usage

### 2. Grafana Cloud Free Tier
- **Data Retention**: 15 days
- **Storage**: 50 GB profiles
- **Series**: Unlimited
- **Users**: 3 users
- **Cost**: $0 (free tier)

### 3. Profiling Features
- Application-wide CPU profiling
- Endpoint-specific labels (earthquake, weather, monitoring APIs)
- Background task profiling (APScheduler jobs)
- Environment metadata tags (version, region, environment)

## Quick Start (After Implementation)

### 1. Create Grafana Cloud Account
```bash
# Sign up at https://grafana.com/auth/sign-up/create-user
# Navigate to your stack → Pyroscope → Details
# Copy: URL, User, Password
```

### 2. Configure Environment Variables
```bash
# Add to .env file
PROFILING_ENABLED=true
PYROSCOPE_SERVER_URL=https://profiles-prod-XXX.grafana.net
PYROSCOPE_USERNAME=123456
PYROSCOPE_API_KEY=glc_xxxxxxxxxxxxx
ENVIRONMENT=production
```

### 3. Install and Run
```bash
pip install -r requirements.txt  # Includes pyroscope-io
python app.py
```

### 4. View Profiles
- Open Grafana Cloud → Profiles
- Select `quake-monitor-web` application
- View flame graphs and analyze CPU usage

## Why Not Grafana Alloy?

**Decision**: Use Pyroscope Python SDK with direct push instead of Grafana Alloy

**Reasoning**:
- ✅ **Simpler**: No local collector infrastructure needed
- ✅ **Free Tier Compatible**: Grafana Cloud supports direct SDK push
- ✅ **Low Volume**: App generates <100 samples/sec (well within limits)
- ✅ **Python-Specific**: Better GIL tracking and subprocess detection
- ✅ **Less Overhead**: No additional process to manage

**When to Use Alloy**:
- Multi-language environments (Go, Java, Python, etc.)
- High-volume applications (>1000 samples/sec)
- eBPF profiling requirements (kernel-level profiling)
- Centralized profiling for multiple services

## Implementation Checklist

### Phase 1: Setup (Non-Breaking)
- [ ] Add `pyroscope-io==0.8.11` to `requirements.txt`
- [ ] Create `.env.example` with profiling variables
- [ ] Create `utils/profiling.py` configuration module

### Phase 2: Instrumentation (Non-Breaking)
- [ ] Initialize profiling in `app.py` startup (conditional)
- [ ] Add profiling labels to critical endpoints
- [ ] Test with profiling disabled (default behavior)

### Phase 3: Enable & Monitor
- [ ] Configure Grafana Cloud credentials
- [ ] Enable profiling in production
- [ ] Monitor for 24-48 hours to capture segfault patterns

## Technical Details

### Profiling Configuration
```python
import pyroscope
import os

pyroscope.configure(
    application_name="quake-monitor-web",
    server_address=os.getenv("PYROSCOPE_SERVER_URL"),
    basic_auth_username=os.getenv("PYROSCOPE_USERNAME"),
    basic_auth_password=os.getenv("PYROSCOPE_API_KEY"),
    sample_rate=100,  # 100Hz sampling
    oncpu=True,       # CPU profiling
    gil_only=True,    # GIL-holding threads
    tags={
        "environment": "production",
        "version": "2.0",
        "region": "davao-city"
    }
)
```

### Endpoint Labeling
```python
from pyroscope import tag_wrapper

@router.get("/api/earthquakes/phivolcs")
async def get_phivolcs_earthquakes(request: Request):
    with tag_wrapper({"endpoint": "phivolcs", "data_source": "external_api"}):
        earthquakes = fetch_phivolcs_earthquakes()
        return templates.TemplateResponse(...)
```

## Estimated Impact

### Data Volume
- **Sample Rate**: 100 samples/second
- **Daily Volume**: ~8.6M samples/day
- **Storage**: ~50-100 MB/day (compressed)
- **Free Tier Limit**: 50 GB (500+ days of data)

### Performance Overhead
- **CPU**: <5% additional usage
- **Memory**: ~10-20 MB for SDK
- **Network**: ~1-2 KB/sec to Grafana Cloud

## Rollback Plan

If profiling causes issues:
```bash
# Disable profiling (no code changes needed)
PROFILING_ENABLED=false

# Or remove environment variable entirely
unset PROFILING_ENABLED
```

Application continues to work normally without profiling.

## Next Steps

1. **Review this proposal** - Ensure approach aligns with your needs
2. **Approve proposal** - Confirm you want to proceed
3. **Implement changes** - Follow tasks.md checklist
4. **Setup Grafana Cloud** - Create account and get credentials
5. **Enable profiling** - Configure environment and monitor
6. **Analyze data** - Use flame graphs to debug segfaults

## Questions?

- **Q**: Will this slow down my app?  
  **A**: No, <5% overhead with 100Hz sampling (configurable)

- **Q**: Do I need to deploy anything?  
  **A**: No, just add Python SDK and configure environment variables

- **Q**: What if I exceed free tier limits?  
  **A**: Very unlikely (<100 samples/sec), but you can reduce sample rate

- **Q**: Can I use this with other monitoring tools?  
  **A**: Yes, Pyroscope is complementary to logs/metrics/traces

- **Q**: What if the segfault is in a C extension?  
  **A**: Python profiler may not capture it directly, but will show patterns leading up to crash. Consider eBPF profiling if needed.

## Resources

- [Grafana Cloud Free Tier](https://grafana.com/pricing/)
- [Pyroscope Python SDK Docs](https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/python/)
- [Grafana Cloud Profiles Setup](https://grafana.com/docs/grafana-cloud/monitor-applications/profiles/)
- [Flame Graph Interpretation](https://www.brendangregg.com/flamegraphs.html)

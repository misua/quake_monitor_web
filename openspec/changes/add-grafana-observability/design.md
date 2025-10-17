## Context

The Earthquake & Weather Monitor FastAPI application experiences intermittent segmentation faults without error logs, making debugging extremely difficult. The application fetches data from multiple external APIs (PHIVOLCS, USGS, PAGASA, IOC) and uses libraries like BeautifulSoup, requests, and httpx that could be sources of memory issues or crashes.

Continuous profiling will provide visibility into:
- CPU usage patterns and hotspots
- Memory allocation and potential leaks
- Thread behavior and GIL contention
- Stack traces at the time of high resource usage

## Goals / Non-Goals

**Goals:**
- Enable continuous CPU and memory profiling with minimal overhead
- Send profiling data to Grafana Cloud's free tier (no infrastructure costs)
- Provide actionable insights for debugging segmentation faults
- Keep configuration simple and environment-based
- Minimal code changes to existing application

**Non-Goals:**
- Local Grafana Alloy deployment (overkill for small app, free tier supports direct push)
- Distributed tracing (out of scope, focus on profiling only)
- Custom metrics or logging infrastructure
- eBPF profiling (requires kernel 4.9+, Python SDK is simpler for FastAPI)

## Decisions

### Decision 1: Direct Pyroscope SDK Push vs Grafana Alloy

**Choice:** Use Pyroscope Python SDK with direct push to Grafana Cloud

**Rationale:**
- Application is small with low data volume (<100 samples/sec)
- Grafana Cloud free tier supports direct SDK push
- No need for local infrastructure (Alloy collector)
- Simpler setup and maintenance
- SDK provides better Python-specific profiling (GIL tracking, subprocess detection)

**Alternatives considered:**
- Grafana Alloy with eBPF: More complex, requires Linux kernel 4.9+, better for multi-language environments
- Grafana Alloy as local collector: Unnecessary overhead for small app, adds deployment complexity

### Decision 2: Profiling Configuration

**Choice:** Environment variable-based configuration with optional profiling

**Rationale:**
- Allows enabling/disabling profiling without code changes
- Keeps credentials out of source code
- Easy to configure per environment (dev, staging, prod)
- Graceful degradation if credentials not provided

### Decision 3: Profiling Scope

**Choice:** Application-wide profiling with optional endpoint-specific labels

**Rationale:**
- Start with broad profiling to capture segfault context
- Add labels to critical endpoints (earthquake fetching, weather API) for granular analysis
- Keep overhead minimal by not over-instrumenting

### Decision 4: Grafana Cloud Free Tier Limits

**Free tier includes:**
- 15 days data retention
- 50 GB profile storage
- Unlimited series
- 3 users

**Estimated usage:**
- ~10-50 samples/sec for single-instance FastAPI app
- Well within free tier limits
- No cost concerns for this use case

## Risks / Trade-offs

### Risk 1: Profiling Overhead
- **Impact:** CPU/memory overhead from profiling
- **Mitigation:** Pyroscope SDK has <5% overhead, configurable sample rate (default 100Hz)
- **Monitoring:** Track application performance before/after enabling profiling

### Risk 2: Credential Management
- **Impact:** Grafana Cloud API key needs secure storage
- **Mitigation:** Use environment variables, document secure practices, never commit to git
- **Alternative:** Use Cloud Access Policy tokens with limited scope

### Risk 3: Segfault May Not Be Captured
- **Impact:** If segfault is in C extension (lxml, urllib3), Python profiler may not capture it
- **Mitigation:** Profiling will still show patterns leading up to crash, consider eBPF if needed
- **Fallback:** Add core dump analysis if profiling insufficient

## Migration Plan

1. **Phase 1: Setup (non-breaking)**
   - Add dependency to requirements.txt
   - Add environment variables to .env.example
   - Create profiling utility module

2. **Phase 2: Instrumentation (non-breaking)**
   - Add profiling initialization with conditional enable
   - Test with profiling disabled (default behavior unchanged)
   - Deploy with profiling disabled

3. **Phase 3: Enable Profiling**
   - Configure Grafana Cloud credentials
   - Enable profiling in production
   - Monitor for 24-48 hours to capture segfault

4. **Rollback Plan:**
   - Set `PROFILING_ENABLED=false` environment variable
   - Application continues to work without profiling
   - No code changes needed for rollback

## Technical Implementation

### Pyroscope SDK Configuration

```python
import pyroscope
import os

def init_profiling():
    if not os.getenv("PROFILING_ENABLED", "false").lower() == "true":
        return
    
    pyroscope.configure(
        application_name="quake-monitor-web",
        server_address=os.getenv("PYROSCOPE_SERVER_URL"),
        basic_auth_username=os.getenv("PYROSCOPE_USERNAME"),
        basic_auth_password=os.getenv("PYROSCOPE_API_KEY"),
        sample_rate=100,  # 100Hz sampling
        detect_subprocesses=False,
        oncpu=True,  # CPU profiling
        gil_only=True,  # Focus on GIL-holding threads
        enable_logging=True,
        tags={
            "environment": os.getenv("ENVIRONMENT", "production"),
            "version": "2.0",
            "region": "davao-city"
        }
    )
```

### Endpoint Labeling Example

```python
from pyroscope import tag_wrapper

@router.get("/api/earthquakes/phivolcs")
async def get_phivolcs_earthquakes(request: Request):
    with tag_wrapper({"endpoint": "phivolcs", "data_source": "external_api"}):
        earthquakes = fetch_phivolcs_earthquakes()
        return templates.TemplateResponse(...)
```

## Open Questions

1. **Q:** Should we enable profiling by default or require explicit opt-in?
   **A:** Require opt-in via environment variable for safety

2. **Q:** Do we need memory profiling in addition to CPU profiling?
   **A:** Start with CPU profiling (default), can enable memory profiling if needed

3. **Q:** Should we add profiling to background tasks (APScheduler)?
   **A:** Yes, if segfaults occur during scheduled data fetching

4. **Q:** What sample rate should we use?
   **A:** Start with default 100Hz, can reduce to 50Hz if overhead is concern

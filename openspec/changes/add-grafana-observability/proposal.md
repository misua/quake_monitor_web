## Why

The application experiences intermittent segmentation faults with no error logs, making it impossible to diagnose the root cause. Continuous profiling with Grafana Cloud Profiles (Pyroscope) will provide CPU and memory profiling data to identify performance bottlenecks, memory leaks, and the source of crashes. Grafana Cloud's free tier provides sufficient capacity for this small application.

## What Changes

- Add Pyroscope Python SDK to instrument the FastAPI application for continuous profiling
- Configure direct push to Grafana Cloud Profiles using the free tier (no local Alloy needed for small data volumes)
- Add environment-based configuration for Grafana Cloud credentials (URL, user, API key)
- Instrument key application endpoints and background tasks with profiling labels
- Add profiling initialization to application startup
- Document setup instructions for Grafana Cloud configuration

## Impact

- **Affected specs**: `app-profiling` (new capability)
- **Affected code**: 
  - `app.py` - Add profiling initialization
  - `requirements.txt` - Add `pyroscope-io` dependency
  - `.env.example` - Add Grafana Cloud configuration template
  - `README.md` - Add profiling setup documentation
  - API routers (`api/*.py`) - Optional profiling labels for specific endpoints
- **Dependencies**: Grafana Cloud account (free tier) required
- **Data volume**: Minimal (<100 samples/sec for small app fits within free tier limits)

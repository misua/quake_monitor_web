# Quick Start: Grafana Cloud Profiling Setup

## TL;DR

Add continuous profiling to debug segmentation faults using Grafana Cloud's free tier. No local infrastructure needed, just Python SDK + environment variables.

## 1. Create Grafana Cloud Account (5 minutes)

1. Go to https://grafana.com/auth/sign-up/create-user
2. Sign up for free tier (no credit card required)
3. Create a stack (choose closest region)
4. Navigate to **Profiles** section in your stack
5. Click **Details** to get credentials

## 2. Get Your Credentials

In Grafana Cloud → Your Stack → Profiles → Details, copy:

```
URL:      https://profiles-prod-XXX.grafana.net
User:     123456
Password: glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 3. Configure Your App

Create or edit `.env` file:

```bash
# Enable profiling
PROFILING_ENABLED=true

# Grafana Cloud credentials (from step 2)
PYROSCOPE_SERVER_URL=https://profiles-prod-XXX.grafana.net
PYROSCOPE_USERNAME=123456
PYROSCOPE_API_KEY=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: environment identifier
ENVIRONMENT=production
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
# This includes pyroscope-io SDK
```

## 5. Run Your App

```bash
python app.py
```

You should see in logs:
```
✓ Pyroscope profiler initialized
✓ Sending profiles to Grafana Cloud
```

## 6. View Profiles in Grafana Cloud

1. Open Grafana Cloud → Profiles
2. Select application: `quake-monitor-web`
3. View flame graphs and CPU usage
4. Filter by endpoint labels (phivolcs, usgs, weather, etc.)

## 7. Debug Segmentation Faults

When a segfault occurs:

1. Go to Grafana Cloud Profiles
2. Select time range around the crash
3. View flame graph to see:
   - Which functions were using CPU before crash
   - Call stack patterns
   - Memory allocation hotspots
4. Identify the problematic code path

## Troubleshooting

### Profiling not starting?

Check logs for errors:
```bash
python app.py 2>&1 | grep -i pyroscope
```

### No data in Grafana Cloud?

1. Verify credentials are correct
2. Check network connectivity: `curl -I https://profiles-prod-XXX.grafana.net`
3. Ensure `PROFILING_ENABLED=true` is set
4. Wait 30-60 seconds for first data to appear

### App running slow?

Reduce sample rate in `utils/profiling.py`:
```python
sample_rate=50,  # Reduce from 100Hz to 50Hz
```

### Want to disable profiling?

```bash
# Option 1: Set to false
PROFILING_ENABLED=false

# Option 2: Remove variable
unset PROFILING_ENABLED

# Option 3: Comment out in .env
# PROFILING_ENABLED=true
```

## What Gets Profiled?

- ✅ All FastAPI endpoints
- ✅ Background tasks (APScheduler)
- ✅ External API calls (PHIVOLCS, USGS, etc.)
- ✅ HTML parsing (BeautifulSoup)
- ✅ HTTP requests (requests, httpx)

## Cost

**$0** - Grafana Cloud free tier includes:
- 15 days data retention
- 50 GB profile storage
- Unlimited series
- 3 users

Your app generates ~50-100 MB/day, so you're well within limits.

## Next Steps

1. **Run for 24-48 hours** to capture segfault patterns
2. **Analyze flame graphs** when crashes occur
3. **Add more labels** to specific endpoints if needed
4. **Share findings** with team using Grafana Cloud dashboards

## Need Help?

- [Grafana Cloud Profiles Docs](https://grafana.com/docs/grafana-cloud/monitor-applications/profiles/)
- [Pyroscope Python SDK](https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/python/)
- [Flame Graph Guide](https://www.brendangregg.com/flamegraphs.html)

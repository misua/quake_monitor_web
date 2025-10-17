# 🔥 Grafana Cloud Profiling - Quick Setup Guide

## ✅ Implementation Complete!

The application now supports continuous profiling with Grafana Cloud Profiles (Pyroscope) to help debug segmentation faults and performance issues.

## 📋 What Was Implemented

### 1. Dependencies Added
- ✅ `pyroscope-io==0.8.11` added to `requirements.txt`

### 2. Configuration Files
- ✅ `.env.example` updated with profiling environment variables
- ✅ `utils/profiling.py` - Profiling configuration module created

### 3. Application Changes
- ✅ `app.py` - Profiling initialization on startup
- ✅ `api/earthquake.py` - Profiling labels for PHIVOLCS, USGS, Top5 endpoints
- ✅ `api/weather.py` - Profiling labels for weather data endpoint

### 4. Documentation
- ✅ `README.md` - Complete profiling setup guide added
- ✅ Troubleshooting section for profiling issues

## 🚀 Next Steps: Enable Profiling

### Step 1: Install Dependencies

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

### Step 2: Create `.env` File

Create a `.env` file in the project root with your Grafana Cloud credentials:

```bash
# Enable profiling
PROFILING_ENABLED=true

# Your Grafana Cloud credentials (you already have these!)
PYROSCOPE_SERVER_URL=https://profiles-prod-007.grafana.net
PYROSCOPE_USERNAME=1408536
PYROSCOPE_API_KEY=glc_eyJvIjoiMTU2MzI0MjMyIsImsiOiJjZGFjay0xNDA4NTM2LWhXLXJ1YWQtGVzdHBzCm9zY29wZS1sIm5iMzYzNHMyeTcyYWwxNzZnhMYzcxNTMweTcyYTFCMDhhHw6NwZzEiLCJtIjp7InIiOiJwcm9kLXVzLWVhc3QtMCJ9fQ==

# Optional: environment identifier
ENVIRONMENT=production
```

### Step 3: Test Without Profiling First

```bash
# Test that the app still works without profiling
PROFILING_ENABLED=false python3 app.py
```

You should see:
```
🌍 Starting Earthquake & Weather Monitor...
📊 Continuous profiling disabled
✓ Application startup complete
```

### Step 4: Enable Profiling

```bash
# Run with profiling enabled
python3 app.py
```

You should see:
```
🌍 Starting Earthquake & Weather Monitor...
✓ Pyroscope profiler initialized successfully
  Server: https://profiles-prod-007.grafana.net
  Application: quake-monitor-web
  Sample Rate: 100Hz
  Environment: production
📊 Continuous profiling enabled - data will be sent to Grafana Cloud
✓ Application startup complete
```

### Step 5: View Profiles in Grafana Cloud

1. Open your browser to: https://misua.grafana.net/a/grafana-pyroscope-app/profiles-explorer
2. Select application: `quake-monitor-web`
3. Wait 30-60 seconds for first data to appear
4. View flame graphs showing CPU usage
5. Filter by labels:
   - `endpoint:phivolcs` - PHIVOLCS earthquake data fetching
   - `endpoint:usgs` - USGS earthquake data fetching
   - `endpoint:weather` - Weather data fetching
   - `endpoint:top5` - Earthquake cluster analysis

## 🧪 Testing Checklist

- [ ] **Install dependencies**: `pip install -r requirements.txt`
- [ ] **Test without profiling**: Verify app works with `PROFILING_ENABLED=false`
- [ ] **Test with profiling**: Verify profiling initializes successfully
- [ ] **Check Grafana Cloud**: Confirm data appears in Profiles UI
- [ ] **Monitor performance**: Ensure <5% CPU overhead
- [ ] **Run for 24-48 hours**: Capture segfault patterns if they occur

## 📊 What Gets Profiled

### Endpoints with Labels
- `/api/earthquakes/phivolcs` - PHIVOLCS data fetching
- `/api/earthquakes/usgs` - USGS data fetching
- `/api/earthquakes/top5` - Earthquake cluster analysis
- `/api/weather` - Weather, typhoon, rainfall, tide data

### Data Sources Tracked
- External API calls (PHIVOLCS, USGS, Open-Meteo, PAGASA)
- HTML parsing (BeautifulSoup)
- Data processing and aggregation

### Profiling Tags
- `environment`: production/development
- `version`: 2.0
- `region`: davao-city
- `app`: earthquake-weather-monitor
- `endpoint`: phivolcs/usgs/weather/top5
- `type`: earthquake_data/weather_data/earthquake_clusters
- `data_source`: phivolcs/external_api

## 🔍 Debugging Segmentation Faults

When a segfault occurs:

1. **Check the time** of the crash
2. **Open Grafana Cloud Profiles**
3. **Select the time range** around the crash (e.g., 5 minutes before)
4. **View the flame graph** to see:
   - Which functions were using CPU before crash
   - Call stack patterns
   - Memory allocation hotspots
5. **Filter by endpoint** to narrow down the source
6. **Look for patterns**:
   - Repeated calls to specific functions
   - Deep call stacks
   - External API timeouts
   - HTML parsing issues

## ⚙️ Configuration Options

### Disable Profiling
```bash
PROFILING_ENABLED=false
```

### Reduce Sample Rate (Lower Overhead)
Edit `utils/profiling.py`:
```python
sample_rate=50,  # Reduce from 100Hz to 50Hz
```

### Change Environment Tag
```bash
ENVIRONMENT=development  # or staging, production
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pyroscope'"
```bash
pip install pyroscope-io
```

### "Profiling is enabled but credentials are missing"
Check your `.env` file has all required variables:
- `PYROSCOPE_SERVER_URL`
- `PYROSCOPE_USERNAME`
- `PYROSCOPE_API_KEY`

### No data in Grafana Cloud
1. Wait 60 seconds for first data
2. Verify credentials are correct
3. Check network: `curl -I https://profiles-prod-007.grafana.net`
4. Check logs: `python3 app.py 2>&1 | grep -i pyroscope`

### App running slow
1. Check CPU usage: `top` or `htop`
2. Reduce sample rate to 50Hz
3. Disable profiling temporarily

## 📚 Resources

- [Grafana Cloud Profiles Docs](https://grafana.com/docs/grafana-cloud/monitor-applications/profiles/)
- [Pyroscope Python SDK](https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/python/)
- [Flame Graph Guide](https://www.brendangregg.com/flamegraphs.html)
- [Your Grafana Cloud Stack](https://grafana.com/orgs/misua)

## 🎯 Success Criteria

✅ Application runs normally without profiling  
✅ Profiling initializes successfully when enabled  
✅ Data appears in Grafana Cloud Profiles UI  
✅ CPU overhead is <5%  
✅ Flame graphs show endpoint-specific data  
✅ Can debug segfaults using profiling data  

---

**Ready to enable profiling?** Follow the steps above and start monitoring your application!

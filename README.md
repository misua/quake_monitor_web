# 🌍 Earthquake & Weather Monitor - Web Version

A real-time monitoring dashboard for earthquakes, weather, tsunamis, typhoons, and more using **Python + FastAPI + HTMX**.

## Features

- 🌡️ **Real-time Weather Data** - Temperature, humidity, UV index, air quality (PM2.5, AQI)
- 🌊 **Tsunami Warnings** - IOC Sea Level Monitoring alerts
- 📊 **Sea Level Monitoring** - Real-time sea level data
- 🌀 **Typhoon Tracking** - PAGASA typhoon information
- 🌧️ **Rainfall Monitor** - PAGASA rainfall data
- 🔴 **PHIVOLCS Earthquakes** - Real-time Philippine earthquake data
- 🌎 **USGS Major Earthquakes** - Worldwide magnitude 4.5+ earthquakes
- 📍 **Top 5 Earthquake Clusters** - Most active locations in last 6 hours
- 🌓 **Day/Night Mode** - Automatic theme switching based on time
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTMX + TailwindCSS
- **Data Sources**: PHIVOLCS, USGS, Open-Meteo, PAGASA, IOC
- **Updates**: Real-time polling via HTMX

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Navigate to the project directory:**
   ```bash
   cd quake_monitor_web
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

Single worker (recommended):
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Multiple workers (requires gunicorn):
```bash
pip install gunicorn
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Access the Dashboard

Open your browser and navigate to:
- **Local**: http://localhost:8000
- **Network**: http://YOUR_IP:8000

## Project Structure

```
quake_monitor_web/
├── app.py                    # Main FastAPI application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── api/                      # API route handlers
│   ├── __init__.py
│   ├── weather.py           # Weather data endpoints
│   ├── earthquake.py        # Earthquake data endpoints
│   ├── tsunami.py           # Tsunami warnings
│   └── monitoring.py        # Sea level, typhoon, rainfall
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Main dashboard
│   └── components/         # HTMX components
│       ├── weather.html
│       ├── tsunami.html
│       ├── sea_level.html
│       ├── phivolcs.html
│       ├── usgs.html
│       ├── top5.html
│       ├── typhoon.html
│       └── rainfall.html
└── static/                  # Static assets
    ├── css/
    │   └── styles.css      # Custom styles
    └── js/
        └── theme.js        # Day/night theme logic
```

## API Endpoints

### Weather
- `GET /api/weather` - Current weather and forecast

### Earthquakes
- `GET /api/earthquakes/phivolcs` - PHIVOLCS earthquake data
- `GET /api/earthquakes/usgs` - USGS major earthquakes
- `GET /api/earthquakes/top5` - Top 5 earthquake clusters

### Monitoring
- `GET /api/tsunami` - Tsunami warnings
- `GET /api/sea-level` - Sea level monitoring
- `GET /api/typhoon` - Typhoon tracking
- `GET /api/rainfall` - Rainfall data

### Health
- `GET /health` - Health check endpoint

## Update Intervals

- **Weather**: Every 30 seconds
- **Earthquakes**: Every 60 seconds
- **Tsunami/Typhoon/Rainfall**: Every 5 minutes (300 seconds)

## Configuration

Edit the configuration in `app.py`:

```python
LATITUDE = 7.190708      # Your location latitude
LONGITUDE = 125.455338   # Your location longitude
LOCATION_NAME = "Davao City, Philippines"
```

## Day/Night Mode

The application automatically switches between day and night themes:
- **Night Mode**: 19:00 (7 PM) - 07:00 (7 AM)
- **Day Mode**: 07:00 (7 AM) - 19:00 (7 PM)

## Continuous Profiling (Optional)

The application supports continuous profiling with **Grafana Cloud Profiles (Pyroscope)** to help diagnose performance issues and segmentation faults.

### Why Use Profiling?

- 🔍 **Debug Segmentation Faults** - Capture CPU/memory patterns before crashes
- 📊 **Performance Analysis** - Identify bottlenecks in data fetching
- 🔥 **Flame Graphs** - Visualize where your app spends CPU time
- 💰 **Free Tier** - Grafana Cloud includes free profiling (15 days retention, 50GB storage)

### Setup Grafana Cloud Profiles

1. **Create Grafana Cloud Account** (Free)
   - Go to https://grafana.com/auth/sign-up/create-user
   - Create a new stack (choose closest region)

2. **Get Your Credentials**
   - Navigate to: Grafana Cloud Portal → Your Stack → Profiles → Details
   - Copy: URL, Username, and Password

3. **Configure Environment Variables**
   
   Create a `.env` file in the project root:
   ```bash
   # Enable profiling
   PROFILING_ENABLED=true
   
   # Grafana Cloud credentials (from step 2)
   PYROSCOPE_SERVER_URL=https://profiles-prod-007.grafana.net
   PYROSCOPE_USERNAME=1408536
   PYROSCOPE_API_KEY=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Optional: environment identifier
   ENVIRONMENT=production
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```
   
   You should see:
   ```
   ✓ Pyroscope profiler initialized successfully
   📊 Continuous profiling enabled - data will be sent to Grafana Cloud
   ```

5. **View Profiles in Grafana Cloud**
   - Open Grafana Cloud → Profiles
   - Select application: `quake-monitor-web`
   - View flame graphs and CPU usage
   - Filter by endpoint labels (phivolcs, usgs, weather, etc.)

### Profiling Configuration

The profiling system is **optional** and **disabled by default**. It only activates when you explicitly enable it.

**Environment Variables:**
- `PROFILING_ENABLED` - Set to `true` to enable profiling (default: `false`)
- `PYROSCOPE_SERVER_URL` - Grafana Cloud Profiles URL
- `PYROSCOPE_USERNAME` - Grafana Cloud username
- `PYROSCOPE_API_KEY` - Grafana Cloud API key
- `ENVIRONMENT` - Environment name for tagging (default: `production`)

**Performance Impact:**
- CPU overhead: <5%
- Memory overhead: ~10-20 MB
- Sample rate: 100Hz (configurable)

### Disable Profiling

To disable profiling, simply set:
```bash
PROFILING_ENABLED=false
```

Or remove the environment variable entirely. The application will run normally without profiling.

### Troubleshooting Profiling

**Profiling not starting?**
```bash
# Check logs for errors
python app.py 2>&1 | grep -i pyroscope
```

**No data in Grafana Cloud?**
1. Verify credentials are correct
2. Check network connectivity: `curl -I https://profiles-prod-XXX.grafana.net`
3. Ensure `PROFILING_ENABLED=true` is set
4. Wait 30-60 seconds for first data to appear

**Want to reduce overhead?**

Edit `utils/profiling.py` and change:
```python
sample_rate=50,  # Reduce from 100Hz to 50Hz
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Module Not Found
Make sure you're in the parent directory where the original modules exist, or copy them to the web project.

### CORS Issues
If accessing from a different domain, configure CORS in `app.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/quake-monitor.service`:

```ini
[Unit]
Description=Earthquake & Weather Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/quake_monitor_web
ExecStart=/path/to/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable quake-monitor
sudo systemctl start quake-monitor
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t quake-monitor .
docker run -p 8000:8000 quake-monitor
```

## License

This project uses data from:
- PHIVOLCS (Philippine Institute of Volcanology and Seismology)
- USGS (United States Geological Survey)
- Open-Meteo (Weather API)
- PAGASA (Philippine Atmospheric, Geophysical and Astronomical Services Administration)
- IOC (Intergovernmental Oceanographic Commission)

## Contributing

Feel free to submit issues and enhancement requests!

## Author

Created as a web-based alternative to the Pygame desktop version.

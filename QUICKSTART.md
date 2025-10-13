# 🚀 Quick Start Guide

## Get Started in 3 Steps

### 1️⃣ Navigate to the project
```bash
cd quake_monitor_web
```

### 2️⃣ Run the startup script
```bash
./start.sh
```

### 3️⃣ Open your browser
Navigate to: **http://localhost:8000**

---

## Alternative: Manual Setup

### Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the application
```bash
python app.py
```

---

## What You'll See

The dashboard displays 8 real-time panels:

1. **Weather Panel** (top-left)
   - Current temperature, conditions
   - UV index, AQI, PM2.5
   - 3-hour forecast
   - Updates every 30 seconds

2. **Tsunami Warnings** (top-right)
   - IOC tsunami alerts
   - Updates every 5 minutes

3. **Sea Level Monitor** (top-right)
   - Real-time sea level data
   - Updates every 5 minutes

4. **PHIVOLCS Earthquakes** (middle-left)
   - Philippine earthquake data
   - Shows up to 8 recent quakes
   - Updates every 60 seconds

5. **USGS Major Earthquakes** (middle-right)
   - Worldwide magnitude 4.5+
   - Updates every 60 seconds

6. **Top 5 Earthquake Clusters** (bottom-left)
   - Most active locations (last 6h)
   - Grouped by city
   - Updates every 60 seconds

7. **Typhoon Tracker** (bottom-center)
   - PAGASA typhoon data
   - Updates every 5 minutes

8. **Rainfall Monitor** (bottom-right)
   - PAGASA rainfall stations
   - Updates every 5 minutes

---

## Features

✅ **Automatic Day/Night Mode**
- Night mode: 7 PM - 7 AM
- Day mode: 7 AM - 7 PM

✅ **Real-time Updates**
- HTMX polling (no page refresh)
- Independent panel updates

✅ **Responsive Design**
- Works on desktop, tablet, mobile
- Panels stack on smaller screens

✅ **Color-coded Alerts**
- Red: High magnitude/danger
- Orange: Moderate
- Green: Low/safe

---

## Troubleshooting

**Port 8000 already in use?**
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

**Module not found?**
Make sure you're running from the parent directory where the original Python modules exist.

**No data showing?**
- Check your internet connection
- Wait 30-60 seconds for initial data load
- Check browser console for errors (F12)

---

## Stopping the Application

Press **Ctrl+C** in the terminal

---

## Access from Other Devices

Find your IP address:
```bash
hostname -I
```

Then access from other devices on the same network:
```
http://YOUR_IP:8000
```

---

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize location in `app.py`
- Deploy to production server
- Set up systemd service for auto-start

---

**Enjoy your real-time monitoring dashboard! 🌍**

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import defaultdict
import urllib3
import hashlib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add parent directory to path
PARENT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PARENT_DIR))

from usgs_monitor import fetch_usgs_earthquakes

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

EARTHQUAKE_URL = "https://earthquake.phivolcs.dost.gov.ph/"


def fetch_phivolcs_earthquakes():
    """Fetch and parse earthquakes from PHIVOLCS"""
    try:
        response = requests.get(EARTHQUAKE_URL, verify=False, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
            if not (any('date' in h or 'time' in h for h in headers) and 
                   any('mag' in h for h in headers)):
                continue
            
            events = []
            for row in rows[1:9]:  # Get top 8 earthquakes
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 6:
                    location = cols[5].get_text(strip=True).replace('Â°', '°').replace('Â', '')
                    depth = cols[3].get_text(strip=True)
                    
                    # Extract latitude and longitude (columns 1 and 2)
                    try:
                        latitude = float(cols[1].get_text(strip=True))
                        longitude = float(cols[2].get_text(strip=True))
                    except:
                        latitude = None
                        longitude = None
                    
                    events.append({
                        'datetime': cols[0].get_text(strip=True),
                        'latitude': latitude,
                        'longitude': longitude,
                        'magnitude': cols[4].get_text(strip=True),
                        'location': location,
                        'depth': f"{depth} km",
                        'id': hashlib.md5(f"{cols[0].get_text(strip=True)}|{cols[4].get_text(strip=True)}|{location}".encode()).hexdigest()
                    })
            
            if events:
                print(f"✓ PHIVOLCS: Found {len(events)} earthquakes")
                return events
        
        print("⚠ PHIVOLCS: No earthquake table found")
        return []
    except Exception as e:
        print(f"Error fetching PHIVOLCS data: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_top5_earthquakes():
    """Get top 5 earthquakes by location count in last 6 hours"""
    try:
        earthquakes = fetch_phivolcs_earthquakes()
        
        # Filter last 6 hours
        now = datetime.now()
        six_hours_ago = now - timedelta(hours=6)
        
        location_counts = defaultdict(list)
        
        for eq in earthquakes:
            try:
                eq_time = datetime.strptime(eq['datetime'], '%d %B %Y - %I:%M %p')
                if eq_time >= six_hours_ago:
                    # Extract city from location
                    location = eq['location']
                    if '(' in location and ')' in location:
                        city = location[location.rfind('(') + 1:location.rfind(')')].strip()
                    else:
                        city = location
                    
                    location_counts[city].append(eq)
            except:
                continue
        
        # Sort by count
        top5 = sorted(location_counts.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        result = []
        for city, quakes in top5:
            latest = quakes[0]
            result.append({
                'city': city,
                'count': len(quakes),
                'magnitude': latest['magnitude'],
                'datetime': latest['datetime'],
                'location': latest['location']
            })
        
        return result
    except Exception as e:
        print(f"Error getting top 5: {e}")
        return []


@router.get("/earthquakes/phivolcs", response_class=HTMLResponse)
async def get_phivolcs_earthquakes(request: Request):
    """Get PHIVOLCS earthquake data"""
    try:
        earthquakes = fetch_phivolcs_earthquakes()
        
        if not earthquakes:
            return templates.TemplateResponse(
                "components/error.html",
                {
                    "request": request,
                    "error_type": "network",
                    "title": "🌍 PHIVOLCS Data Unavailable",
                    "message": "Unable to connect to PHIVOLCS earthquake monitoring service. The website may be down or your internet connection may be offline.",
                    "component": "PHIVOLCS panel"
                }
            )
        
        return templates.TemplateResponse(
            "components/phivolcs.html",
            {"request": request, "earthquakes": earthquakes}
        )
    except requests.exceptions.Timeout:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "timeout",
                "title": "🌍 PHIVOLCS Timeout",
                "message": "The PHIVOLCS website is taking too long to respond. Please wait while we retry.",
                "component": "PHIVOLCS panel"
            }
        )
    except requests.exceptions.ConnectionError:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "network",
                "title": "🌍 No Internet Connection",
                "message": "Cannot reach PHIVOLCS servers. Please check your network connection.",
                "component": "PHIVOLCS panel"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "general",
                "title": "🌍 PHIVOLCS Error",
                "message": "An error occurred while loading earthquake data from PHIVOLCS.",
                "component": "PHIVOLCS panel"
            }
        )


@router.get("/earthquakes/usgs", response_class=HTMLResponse)
async def get_usgs_earthquakes(request: Request):
    """Get USGS earthquake data"""
    try:
        # Try 4.5+ past day first
        earthquakes = fetch_usgs_earthquakes(feed='4.5_day', philippines_only=True)
        
        # If no results, try past week
        if not earthquakes:
            earthquakes = fetch_usgs_earthquakes(feed='4.5_week', philippines_only=True)
        
        # If still no results, try 2.5+ past day
        if not earthquakes:
            earthquakes = fetch_usgs_earthquakes(feed='2.5_day', philippines_only=True)
        
        if not earthquakes:
            return templates.TemplateResponse(
                "components/error.html",
                {
                    "request": request,
                    "error_type": "info",
                    "title": "🌎 No Recent Earthquakes",
                    "message": "No significant earthquakes detected in the Philippines region recently. This is good news!",
                    "component": "USGS panel"
                }
            )
        
        return templates.TemplateResponse(
            "components/usgs.html",
            {"request": request, "earthquakes": earthquakes}
        )
    except requests.exceptions.ConnectionError:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "network",
                "title": "🌎 No Internet Connection",
                "message": "Cannot reach USGS servers. Check your network.",
                "component": "USGS panel"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "general",
                "title": "🌎 USGS Error",
                "message": "Error loading USGS earthquake data.",
                "component": "USGS panel"
            }
        )


@router.get("/earthquakes/top5", response_class=HTMLResponse)
async def get_top5(request: Request):
    """Get top 5 earthquakes by location"""
    try:
        top5 = get_top5_earthquakes()
        return templates.TemplateResponse(
            "components/top5.html",
            {"request": request, "top5": top5}
        )
    except requests.exceptions.ConnectionError:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "network",
                "title": "📊 Connection Error",
                "message": "Cannot load earthquake cluster data. Check your internet connection.",
                "component": "Top 5 panel"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "data",
                "title": "📊 Data Error",
                "message": "Unable to process earthquake cluster data.",
                "component": "Top 5 panel"
            }
        )


@router.get("/earthquakes/latest", response_class=HTMLResponse)
async def get_latest_earthquake(request: Request):
    """Get the most recent earthquake for large display"""
    try:
        earthquakes = fetch_phivolcs_earthquakes()
        
        if not earthquakes:
            return templates.TemplateResponse(
                "components/latest_earthquake.html",
                {"request": request, "earthquake": None}
            )
        
        # Get the most recent earthquake (first one)
        latest = earthquakes[0]
        
        return templates.TemplateResponse(
            "components/latest_earthquake.html",
            {"request": request, "earthquake": latest}
        )
    except requests.exceptions.ConnectionError:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "network",
                "title": "🔔 Connection Error",
                "message": "Cannot load latest earthquake data.",
                "component": "Latest Earthquake panel"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "general",
                "title": "🔔 Data Error",
                "message": "Unable to load latest earthquake.",
                "component": "Latest Earthquake panel"
            }
        )

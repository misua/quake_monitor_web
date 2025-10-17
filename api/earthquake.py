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
import time
from functools import lru_cache

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add parent directory to path
PARENT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PARENT_DIR))

from usgs_monitor import fetch_usgs_earthquakes
from utils.profiling import get_profiling_wrapper
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

EARTHQUAKE_URL = "https://earthquake.phivolcs.dost.gov.ph/"

# Cache for PHIVOLCS data (30 second TTL)
_phivolcs_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 30  # seconds - balance between freshness and performance


def fetch_phivolcs_earthquakes():
    """Fetch and parse earthquakes from PHIVOLCS with caching"""
    profiling_wrapper = get_profiling_wrapper()
    start_time = time.time()
    
    # Check cache first
    current_time = time.time()
    if _phivolcs_cache["data"] and (current_time - _phivolcs_cache["timestamp"]) < CACHE_TTL:
        logger.debug("✓ Using cached PHIVOLCS data")
        return _phivolcs_cache["data"]
    
    logger.info("🔄 Fetching fresh PHIVOLCS data...")
    try:
        # Profile the external API call with strict timeout
        # Use tuple timeout: (connect timeout, read timeout)
        timeout = (5, 10)  # 5s to connect, 10s to read - total max 15s
        
        if profiling_wrapper:
            with profiling_wrapper({"data_source": "phivolcs", "operation": "fetch_earthquakes"}):
                response = requests.get(EARTHQUAKE_URL, verify=False, timeout=timeout)
        else:
            response = requests.get(EARTHQUAKE_URL, verify=False, timeout=timeout)
        response.raise_for_status()
        
        # Check response size to prevent parsing huge/malformed HTML
        content_length = len(response.text)
        logger.info(f"📊 PHIVOLCS response size: {content_length:,} bytes ({content_length/1024/1024:.2f} MB)")
        
        if content_length > 10_000_000:  # 10MB limit (increased from 5MB)
            logger.error(f"🚨 PHIVOLCS response too large: {content_length:,} bytes - skipping parse")
            return _phivolcs_cache.get("data", [])
        
        logger.debug(f"Parsing PHIVOLCS HTML ({content_length} bytes)")
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
                duration = time.time() - start_time
                print(f"✓ PHIVOLCS: Found {len(events)} earthquakes")
                # Update cache
                _phivolcs_cache["data"] = events
                _phivolcs_cache["timestamp"] = current_time
                
                # Log performance
                if duration > 5.0:
                    logger.error(f"🚨 CRITICAL: PHIVOLCS fetch took {duration:.2f}s - POTENTIAL SEGFAULT RISK!")
                elif duration > 2.0:
                    logger.warning(f"⚠️  SLOW: PHIVOLCS fetch took {duration:.2f}s")
                else:
                    logger.info(f"✓ PHIVOLCS fetch completed in {duration:.2f}s")
                
                return events
        
        print("⚠ PHIVOLCS: No earthquake table found")
        return []
    except requests.exceptions.Timeout as e:
        duration = time.time() - start_time
        logger.error(f"🚨 TIMEOUT: PHIVOLCS request timed out after {duration:.2f}s - {e}")
        return _phivolcs_cache.get("data", [])  # Return cached data if available
    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time
        logger.warning(f"⚠ Network error fetching PHIVOLCS data after {duration:.2f}s: {e}")
        return _phivolcs_cache.get("data", [])  # Return cached data if available
    except Exception as e:
        print(f"⚠ Error fetching PHIVOLCS data: {e}")
        import traceback
        traceback.print_exc()
        return _phivolcs_cache.get("data", [])  # Return cached data if available


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
    """Get PHIVOLCS earthquake data (with USGS fallback for testing)"""
    profiling_wrapper = get_profiling_wrapper()
    
    try:
        # Profile the endpoint
        if profiling_wrapper:
            with profiling_wrapper({"endpoint": "phivolcs", "type": "earthquake_data"}):
                earthquakes = fetch_phivolcs_earthquakes()
        else:
            earthquakes = fetch_phivolcs_earthquakes()
        
        # TEMPORARY: Fallback to USGS if PHIVOLCS fails
        if not earthquakes:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("⚠️  PHIVOLCS failed, falling back to USGS data")
            earthquakes = fetch_usgs_earthquakes(feed='all_day', philippines_only=True)
            
            if earthquakes:
                # Add a note that this is USGS data
                for eq in earthquakes:
                    eq['source_note'] = 'USGS (PHIVOLCS unavailable)'
        
        if not earthquakes:
            return templates.TemplateResponse(
                "components/error.html",
                {
                    "request": request,
                    "error_type": "network",
                    "title": "🌍 Earthquake Data Unavailable",
                    "message": "Unable to connect to earthquake monitoring services. Both PHIVOLCS and USGS are unavailable.",
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
    profiling_wrapper = get_profiling_wrapper()
    
    try:
        # Try 4.5+ past day first
        if profiling_wrapper:
            with profiling_wrapper({"endpoint": "usgs", "type": "earthquake_data"}):
                earthquakes = fetch_usgs_earthquakes(feed='4.5_day', philippines_only=True)
        else:
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
    profiling_wrapper = get_profiling_wrapper()
    
    try:
        if profiling_wrapper:
            with profiling_wrapper({"endpoint": "top5", "type": "earthquake_clusters"}):
                top5 = get_top5_earthquakes()
        else:
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


@router.get("/earthquakes/compare")
async def compare_sources():
    """Compare PHIVOLCS vs USGS data (for testing)"""
    try:
        phivolcs_data = fetch_phivolcs_earthquakes()
        usgs_data = fetch_usgs_earthquakes(feed='all_day', philippines_only=True)
        
        return {
            "phivolcs": {
                "count": len(phivolcs_data),
                "earthquakes": phivolcs_data[:5] if phivolcs_data else []
            },
            "usgs": {
                "count": len(usgs_data),
                "earthquakes": usgs_data[:5] if usgs_data else []
            },
            "comparison": {
                "phivolcs_working": len(phivolcs_data) > 0,
                "usgs_working": len(usgs_data) > 0,
                "recommendation": "USGS" if len(usgs_data) > len(phivolcs_data) else "PHIVOLCS"
            }
        }
    except Exception as e:
        return {"error": str(e)}


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

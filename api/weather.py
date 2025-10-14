from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path
import requests

# Add parent directory to path
PARENT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PARENT_DIR))

from openmeteo_api import (
    fetch_weather_data,
    fetch_air_quality_data,
    get_weather_description,
    get_uv_index_level,
    get_aqi_level,
    get_pm25_level
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

LATITUDE = 7.190708
LONGITUDE = 125.455338
LOCATION_NAME = "Davao City, Philippines"


@router.get("/weather", response_class=HTMLResponse)
async def get_weather(request: Request):
    """Get weather data and render component"""
    try:
        # Import typhoon, rainfall, and tide functions
        from pagasa_monitor import get_typhoon_status, fetch_rainfall_data
        from tide_monitor import get_tide_status
        
        weather_data = fetch_weather_data()
        air_quality_data = fetch_air_quality_data()
        typhoon_data = get_typhoon_status()
        rainfall_data = fetch_rainfall_data()
        tide_data = get_tide_status()
        
        if not weather_data:
            return templates.TemplateResponse(
                "components/error.html",
                {
                    "request": request,
                    "error_type": "network",
                    "title": "☁️ Weather Data Unavailable",
                    "message": "Unable to connect to Open-Meteo weather service. Please check your internet connection.",
                    "component": "Weather panel"
                }
            )
        
        return templates.TemplateResponse(
            "components/weather.html",
            {
                "request": request,
                "weather": weather_data,
                "air_quality": air_quality_data,
                "typhoon": typhoon_data,
                "rainfall": rainfall_data,
                "tide": tide_data,
                "location": LOCATION_NAME
            }
        )
    except requests.exceptions.Timeout:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "timeout",
                "title": "☁️ Weather Service Timeout",
                "message": "The weather service is taking too long to respond. It may be experiencing high traffic.",
                "component": "Weather panel"
            }
        )
    except requests.exceptions.ConnectionError:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "network",
                "title": "☁️ No Internet Connection",
                "message": "Cannot reach the weather service. Please check your network connection and try again.",
                "component": "Weather panel"
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
                "title": "☁️ Weather Error",
                "message": "An unexpected error occurred while loading weather data.",
                "component": "Weather panel",
                "details": str(e),
                "show_details": False
            }
        )

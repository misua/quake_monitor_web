from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path

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
        weather_data = fetch_weather_data()
        air_quality_data = fetch_air_quality_data()
        
        if not weather_data:
            return '<div class="panel p-6"><h2 class="text-xl font-bold mb-4 text-yellow-500">WEATHER</h2><div class="text-center py-8">Unable to fetch weather data</div></div>'
        
        return templates.TemplateResponse(
            "components/weather.html",
            {
                "request": request,
                "weather": weather_data,
                "air_quality": air_quality_data,
                "location": LOCATION_NAME
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f'<div class="panel p-6"><h2 class="text-xl font-bold mb-4 text-yellow-500">WEATHER</h2><div class="error">Error: {str(e)}</div></div>'

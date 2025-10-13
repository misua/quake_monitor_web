from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path

# Add parent directory to path
PARENT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PARENT_DIR))

from sea_level_monitor import get_sea_level_status
from pagasa_monitor import get_typhoon_status, fetch_rainfall_data

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/sea-level", response_class=HTMLResponse)
async def get_sea_level(request: Request):
    """Get sea level monitoring data"""
    try:
        sea_level_data = get_sea_level_status()
        return templates.TemplateResponse(
            "components/sea_level.html",
            {"request": request, "sea_level": sea_level_data}
        )
    except Exception as e:
        return f'<div class="error">Error loading sea level data: {str(e)}</div>'


@router.get("/typhoon", response_class=HTMLResponse)
async def get_typhoon(request: Request):
    """Get typhoon tracking data"""
    try:
        typhoon_data = get_typhoon_status()
        return templates.TemplateResponse(
            "components/typhoon.html",
            {"request": request, "typhoon": typhoon_data}
        )
    except Exception as e:
        return f'<div class="error">Error loading typhoon data: {str(e)}</div>'


@router.get("/rainfall", response_class=HTMLResponse)
async def get_rainfall(request: Request):
    """Get rainfall monitoring data"""
    try:
        rainfall_data = fetch_rainfall_data()
        return templates.TemplateResponse(
            "components/rainfall.html",
            {"request": request, "rainfall": rainfall_data}
        )
    except Exception as e:
        return f'<div class="error">Error loading rainfall data: {str(e)}</div>'

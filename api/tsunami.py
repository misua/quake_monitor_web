from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


def fetch_tsunami_warnings():
    """Fetch tsunami warning information from PHIVOLCS"""
    try:
        url = "https://tsunami.phivolcs.dost.gov.ph/"
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tsunami_data = []
        
        # Look for earthquake/tsunami bulletin entries
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                cols = row.find_all(['td', 'th'])
                if len(cols) < 3:
                    continue
                
                col_texts = [col.get_text(strip=True) for col in cols]
                
                # Smart column detection
                magnitude = None
                location = None
                advisory = "No Advisory"
                
                # Find magnitude
                for col_text in col_texts:
                    mag_match = re.search(r'^(\d\.\d)$', col_text)
                    if mag_match:
                        mag_val = float(mag_match.group(1))
                        if 3.0 <= mag_val <= 9.9:
                            magnitude = mag_match.group(1)
                            break
                
                if not magnitude:
                    continue
                
                # Find date/time
                date_time = None
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                for col_text in col_texts:
                    if any(month in col_text for month in months):
                        date_time = col_text.strip()
                        break
                
                if not date_time:
                    date_time = "Unknown Date"
                
                # Find location
                for col_text in col_texts:
                    if any(month in col_text for month in months):
                        continue
                    if '°' in col_text or 'deg' in col_text.lower():
                        continue
                    if col_text == magnitude:
                        continue
                    if re.match(r'^\d+\.?\d*$', col_text):
                        continue
                    
                    if len(col_text) > 5 and any(c.isalpha() for c in col_text):
                        location = col_text.replace('°', '').replace('deg', '')
                        location = re.sub(r'\d+\.?\d*\s*[NSEW]*', '', location)
                        location = location.strip()
                        
                        if len(location) > 5:
                            break
                
                if not location:
                    location = "Unknown Location"
                
                # Find advisory link
                advisory_link = row.find('a', href=True)
                if advisory_link and 'advisory' in advisory_link.get('href', '').lower():
                    advisory_num = re.search(r'(\d+)', advisory_link.text)
                    if advisory_num:
                        advisory = f"Advisory #{advisory_num.group(1)}"
                    else:
                        advisory = "Advisory Available"
                
                tsunami_data.append({
                    'magnitude': magnitude,
                    'location': location,
                    'datetime': date_time,
                    'advisory': advisory
                })
                
                if len(tsunami_data) >= 5:
                    break
            
            if tsunami_data:
                break
        
        return tsunami_data if tsunami_data else [{"message": "No active tsunami warnings", "level": "normal"}]
        
    except Exception as e:
        print(f"Error fetching tsunami warnings: {e}")
        import traceback
        traceback.print_exc()
        return [{"message": "Unable to fetch tsunami data", "level": "error"}]


@router.get("/tsunami", response_class=HTMLResponse)
async def get_tsunami_warnings(request: Request):
    """Get tsunami warnings"""
    try:
        warnings = fetch_tsunami_warnings()
        return templates.TemplateResponse(
            "components/tsunami.html",
            {"request": request, "warnings": warnings}
        )
    except Exception as e:
        return f'<div class="error">Error loading tsunami data: {str(e)}</div>'


@router.get("/tsunami-sealevel", response_class=HTMLResponse)
async def get_tsunami_sealevel_combined(request: Request):
    """Get combined tsunami warnings and sea level data"""
    try:
        # Add parent directory to path
        PARENT_DIR = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(PARENT_DIR))
        
        from sea_level_monitor import get_sea_level_status
        
        warnings = fetch_tsunami_warnings()
        sea_level = get_sea_level_status()
        
        return templates.TemplateResponse(
            "components/tsunami_sealevel.html",
            {
                "request": request,
                "warnings": warnings,
                "sea_level": sea_level,
                "location": "Davao City"
            }
        )
    except requests.exceptions.Timeout:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "timeout",
                "title": "🌊 Service Timeout",
                "message": "Tsunami and sea level services are taking too long to respond. Retrying...",
                "component": "Tsunami & Sea Level panel"
            }
        )
    except requests.exceptions.ConnectionError:
        return templates.TemplateResponse(
            "components/error.html",
            {
                "request": request,
                "error_type": "network",
                "title": "🌊 No Internet Connection",
                "message": "Cannot reach tsunami monitoring services. Please check your network connection.",
                "component": "Tsunami & Sea Level panel"
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
                "title": "🌊 Data Error",
                "message": "Unable to load tsunami and sea level monitoring data.",
                "component": "Tsunami & Sea Level panel"
            }
        )

#!/usr/bin/env python3
"""
Tide Monitor Module
Scrapes tide data (high/low tide) from tide-forecast.com
"""

import requests
import json
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# Configuration
TIDE_FORECAST_URL = "https://www.tide-forecast.com/locations/Davao-Philippines/tides/latest"

# Cache settings - persistent JSON file
CACHE_FILE = Path(__file__).parent / '.tide_cache.json'
CACHE_DURATION = 6 * 3600  # Cache for 6 hours


def load_cache():
    """Load tide data from cache file"""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                cache_age = (datetime.now() - cache_time).total_seconds()
                
                if cache_age < CACHE_DURATION:
                    return cache_data['data']
    except Exception as e:
        print(f"Cache load error: {e}")
    return None


def save_cache(data):
    """Save tide data to cache file"""
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"Cache save error: {e}")


def fetch_tide_data():
    """
    Scrape tide data from tide-forecast.com
    Returns next high and low tides
    """
    # Check persistent cache first
    cached_data = load_cache()
    if cached_data:
        return cached_data
    
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(TIDE_FORECAST_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find tide table
        tide_table = soup.find('table', class_='tide-day-tides')
        if not tide_table:
            return {
                'error': 'Could not find tide table',
                'next_high': None,
                'next_low': None
            }
        
        tides = []
        now = datetime.now()
        
        # Parse tide rows - get all tides for today
        rows = tide_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            
            # Extract tide type, time, and height
            tide_type = cells[0].get_text(strip=True)
            time_cell = cells[1].find('b')
            height_cell = cells[2].find('b', class_='js-two-units-length-value__primary')
            
            if not time_cell or not height_cell:
                continue
            
            time_str = time_cell.get_text(strip=True)
            height_str = height_cell.get_text(strip=True)
            
            # Parse time (format: "12:34 AM" or "1:23 PM")
            try:
                tide_time = datetime.strptime(time_str, '%I:%M %p').replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                tides.append({
                    'type': tide_type,
                    'time': time_str,
                    'height': height_str,
                    'datetime': tide_time
                })
            except ValueError:
                continue
        
        # Find next high and low
        next_high = None
        next_low = None
        for tide in tides:
            if tide['datetime'] > now:
                if 'High' in tide['type'] and not next_high:
                    next_high = {
                        'time': tide['time'],
                        'height': tide['height']
                    }
                elif 'Low' in tide['type'] and not next_low:
                    next_low = {
                        'time': tide['time'],
                        'height': tide['height']
                    }
                if next_high and next_low:
                    break
        
        # Get all tides for display (remove datetime for JSON serialization)
        all_tides = [{'type': t['type'], 'time': t['time'], 'height': t['height']} for t in tides]
        
        result = {
            'next_high': next_high,
            'next_low': next_low,
            'all_tides': all_tides,
            'error': None
        }
        
        # Save to persistent cache
        save_cache(result)
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            'error': 'Timeout',
            'next_high': None,
            'next_low': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'next_high': None,
            'next_low': None
        }
    except Exception as e:
        return {
            'error': f'Unexpected error: {str(e)}',
            'next_high': None,
            'next_low': None
        }


def get_tide_status():
    """Get formatted tide status for display"""
    return fetch_tide_data()


if __name__ == "__main__":
    # Test the module
    import json
    print("Testing Tide Monitor...")
    status = get_tide_status()
    print(json.dumps(status, indent=2))

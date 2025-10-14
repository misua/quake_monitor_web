#!/usr/bin/env python3
"""
Tide Monitor Module
Fetches tide data (high/low tide) from Stormglass.io API
"""

import requests
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
STORMGLASS_API_KEY = os.getenv('STORMGLASS_API_KEY', '')
STORMGLASS_BASE_URL = "https://api.stormglass.io/v2/tide/extremes/point"

# Davao City coordinates
LATITUDE = float(os.getenv('LATITUDE', 7.190708))
LONGITUDE = float(os.getenv('LONGITUDE', 125.455338))

# Cache settings - persistent JSON file
CACHE_FILE = Path(__file__).parent / '.tide_cache.json'
CACHE_DURATION = 12 * 3600  # Cache for 12 hours (only 2 API calls per day)


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
    Fetch tide data from Stormglass.io
    Returns next high and low tides
    """
    # Check persistent cache first
    cached_data = load_cache()
    if cached_data:
        return cached_data
    
    if not STORMGLASS_API_KEY:
        return {
            'error': 'No API key configured',
            'next_high': None,
            'next_low': None
        }
    
    try:
        # Get tide data for next 24 hours
        start = datetime.utcnow()
        end = start + timedelta(days=1)
        
        params = {
            'lat': LATITUDE,
            'lng': LONGITUDE,
            'start': start.isoformat(),
            'end': end.isoformat()
        }
        
        headers = {
            'Authorization': STORMGLASS_API_KEY
        }
        
        response = requests.get(
            STORMGLASS_BASE_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' not in data:
            return {
                'error': 'Invalid response',
                'next_high': None,
                'next_low': None
            }
        
        # Parse tide extremes
        extremes = data['data']
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        next_high = None
        next_low = None
        
        for extreme in extremes:
            tide_time = datetime.fromisoformat(extreme['time'].replace('Z', '+00:00'))
            
            # Only consider future tides
            if tide_time > now:
                if extreme['type'] == 'high' and not next_high:
                    next_high = {
                        'time': tide_time.strftime('%I:%M %p'),
                        'height': f"{extreme['height']:.2f}m"
                    }
                elif extreme['type'] == 'low' and not next_low:
                    next_low = {
                        'time': tide_time.strftime('%I:%M %p'),
                        'height': f"{extreme['height']:.2f}m"
                    }
            
            # Stop when we have both
            if next_high and next_low:
                break
        
        result = {
            'next_high': next_high,
            'next_low': next_low,
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
    tide_data = fetch_tide_data()
    
    return {
        'next_high': tide_data.get('next_high'),
        'next_low': tide_data.get('next_low'),
        'error': tide_data.get('error')
    }


if __name__ == "__main__":
    # Test the module
    print("Testing Tide Monitor...")
    status = get_tide_status()
    print(f"Next High Tide: {status['next_high']}")
    print(f"Next Low Tide: {status['next_low']}")
    if status['error']:
        print(f"Error: {status['error']}")

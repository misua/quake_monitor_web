#!/usr/bin/env python3
"""
PAGASA Data Monitor
Fetches typhoon and rainfall data from PAGASA
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_typhoon_data():
    """
    Fetch active typhoon data from PAGASA
    Returns list of active typhoons with their information
    """
    try:
        # PAGASA Tropical Cyclone page
        url = "https://www.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        typhoons = []
        
        # Try to find typhoon information from the bulletin
        # PAGASA structure may vary, so we'll look for common patterns
        
        # Look for bulletin content
        content_div = soup.find('div', class_='article-content') or soup.find('div', class_='content')
        
        if content_div:
            text = content_div.get_text()
            
            # Check if there's an active typhoon
            if 'no tropical cyclone' in text.lower() or 'no active' in text.lower():
                return []
            
            # Try to extract typhoon name
            name_match = re.search(r'(?:Typhoon|Tropical Storm|Tropical Depression|Super Typhoon)\s+([A-Z]+)', text)
            
            if name_match:
                typhoon_name = name_match.group(1)
                
                # Try to extract location
                location_match = re.search(r'(?:located|estimated)\s+at\s+([^\.]+)', text, re.IGNORECASE)
                location = location_match.group(1) if location_match else "Unknown location"
                
                # Try to extract wind speed
                wind_match = re.search(r'(\d+)\s*km/h', text)
                wind_speed = wind_match.group(1) if wind_match else "N/A"
                
                # Try to extract movement
                movement_match = re.search(r'moving\s+([^\.]+)', text, re.IGNORECASE)
                movement = movement_match.group(1) if movement_match else "Unknown"
                
                # Determine category based on wind speed
                try:
                    wind = int(wind_speed)
                    if wind >= 220:
                        category = "Super Typhoon"
                    elif wind >= 185:
                        category = "Typhoon"
                    elif wind >= 118:
                        category = "Severe Tropical Storm"
                    elif wind >= 62:
                        category = "Tropical Storm"
                    else:
                        category = "Tropical Depression"
                except:
                    category = "Unknown"
                
                typhoons.append({
                    'name': typhoon_name,
                    'category': category,
                    'location': location.strip(),
                    'wind_speed': wind_speed,
                    'movement': movement.strip(),
                    'last_update': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        return typhoons
        
    except Exception as e:
        print(f"Error fetching typhoon data: {e}")
        return []


def fetch_rainfall_data(region="Region XI", city="Davao"):
    """
    Fetch rainfall monitoring data for specific region
    Default: Region XI (Davao Region)
    Returns rainfall information and flood risk
    """
    try:
        # Try multiple PAGASA sources for regional data
        
        # 1. Try regional weather forecast page
        regional_url = "https://www.pagasa.dost.gov.ph/regional-weather-forecast"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        rainfall_data = {
            'status': 'NORMAL',
            'intensity': 'Light',
            'accumulated_24h': 'N/A',
            'flood_risk': 'Low',
            'affected_areas': [],
            'region': region,
            'city': city,
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Try to get regional forecast
        try:
            response = requests.get(regional_url, headers=headers, timeout=15, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Region XI / Davao in the forecast
            page_text = soup.get_text().lower()
            
            # Check if our region is mentioned with rainfall
            if region.lower() in page_text or city.lower() in page_text:
                # Look for rainfall keywords near our region
                if 'heavy rain' in page_text or 'intense rain' in page_text:
                    rainfall_data['status'] = 'WARNING'
                    rainfall_data['intensity'] = 'Heavy'
                    rainfall_data['flood_risk'] = 'High'
                elif 'moderate rain' in page_text or 'scattered rainshowers' in page_text:
                    rainfall_data['status'] = 'ADVISORY'
                    rainfall_data['intensity'] = 'Moderate'
                    rainfall_data['flood_risk'] = 'Moderate'
                elif 'light rain' in page_text or 'isolated rainshowers' in page_text:
                    rainfall_data['intensity'] = 'Light'
                    rainfall_data['flood_risk'] = 'Low'
        except:
            pass
        
        # 2. Check main page for general advisories affecting our region
        try:
            main_url = "https://www.pagasa.dost.gov.ph/"
            response = requests.get(main_url, headers=headers, timeout=15, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for advisories
            advisories = soup.find_all('div', class_='advisory') or soup.find_all('div', class_='alert')
            
            for advisory in advisories:
                text = advisory.get_text().lower()
                
                # Check if our region is mentioned
                if region.lower() in text or city.lower() in text or 'mindanao' in text:
                    # Check for rainfall warnings
                    if 'heavy rain' in text or 'intense rain' in text:
                        rainfall_data['status'] = 'WARNING'
                        rainfall_data['intensity'] = 'Heavy'
                        rainfall_data['flood_risk'] = 'High'
                    elif 'moderate rain' in text:
                        rainfall_data['status'] = 'ADVISORY'
                        rainfall_data['intensity'] = 'Moderate'
                        rainfall_data['flood_risk'] = 'Moderate'
                    
                    # Check for flood warnings
                    if 'flood' in text:
                        rainfall_data['flood_risk'] = 'High'
                        rainfall_data['status'] = 'WARNING'
        except:
            pass
        
        return rainfall_data
        
    except Exception as e:
        print(f"Error fetching rainfall data: {e}")
        return {
            'status': 'NO_DATA',
            'intensity': 'N/A',
            'accumulated_24h': 'N/A',
            'flood_risk': 'Unknown',
            'affected_areas': [],
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M")
        }


def get_typhoon_status():
    """
    Get simplified typhoon status for display
    Returns: dict with status and active typhoon count
    """
    typhoons = fetch_typhoon_data()
    
    if not typhoons:
        return {
            'status': 'NONE',
            'count': 0,
            'message': 'No active typhoons',
            'typhoons': []
        }
    
    # Determine highest threat level
    categories = [t['category'] for t in typhoons]
    
    if any('Super' in c for c in categories):
        status = 'CRITICAL'
    elif any('Typhoon' in c for c in categories):
        status = 'WARNING'
    else:
        status = 'ADVISORY'
    
    return {
        'status': status,
        'count': len(typhoons),
        'message': f"{len(typhoons)} active typhoon(s)",
        'typhoons': typhoons
    }


if __name__ == "__main__":
    # Test the module
    print("Testing PAGASA Monitor...")
    print("\n=== Typhoon Data ===")
    typhoon_status = get_typhoon_status()
    print(f"Status: {typhoon_status['status']}")
    print(f"Message: {typhoon_status['message']}")
    for t in typhoon_status['typhoons']:
        print(f"\nName: {t['name']}")
        print(f"Category: {t['category']}")
        print(f"Location: {t['location']}")
        print(f"Wind Speed: {t['wind_speed']} km/h")
        print(f"Movement: {t['movement']}")
    
    print("\n=== Rainfall Data ===")
    rainfall = fetch_rainfall_data(region="Region XI", city="Davao")
    print(f"Region: {rainfall.get('region', 'N/A')}")
    print(f"City: {rainfall.get('city', 'N/A')}")
    print(f"Status: {rainfall['status']}")
    print(f"Intensity: {rainfall['intensity']}")
    print(f"Flood Risk: {rainfall['flood_risk']}")
    print(f"Last Update: {rainfall['last_update']}")

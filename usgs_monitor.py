#!/usr/bin/env python3
"""
USGS Earthquake Monitor Module
Fetches earthquake data from USGS GeoJSON API
Provides tsunami warnings, felt reports, alert levels, and depth information
"""

import requests
import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


# Philippines bounding box (approximate)
PHILIPPINES_BOUNDS = {
    'min_lat': 4.0,
    'max_lat': 21.0,
    'min_lon': 116.0,
    'max_lon': 127.0
}

# USGS API endpoints
USGS_FEEDS = {
    'all_hour': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson',
    'all_day': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson',
    '2.5_day': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson',
    '4.5_day': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson',
    '4.5_week': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson',
}


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance


def is_in_philippines(lat, lon):
    """Check if coordinates are within Philippines bounding box"""
    return (PHILIPPINES_BOUNDS['min_lat'] <= lat <= PHILIPPINES_BOUNDS['max_lat'] and
            PHILIPPINES_BOUNDS['min_lon'] <= lon <= PHILIPPINES_BOUNDS['max_lon'])


def fetch_usgs_earthquakes(feed='4.5_day', philippines_only=True):
    """
    Fetch earthquake data from USGS GeoJSON API
    
    Args:
        feed: Which feed to use (all_hour, all_day, 2.5_day, 4.5_day, 4.5_week)
        philippines_only: If True, filter for Philippines region only
    
    Returns:
        List of earthquake dictionaries with USGS data
    """
    try:
        url = USGS_FEEDS.get(feed, USGS_FEEDS['4.5_day'])
        
        print(f"Fetching USGS data from: {feed}")
        # Use tuple timeout: (3s connect, 7s read) = max 10s
        timeout = (3, 7)
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        earthquakes = []
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [0, 0, 0])
            
            # Extract coordinates
            lon, lat, depth = coords[0], coords[1], coords[2]
            
            # Filter for Philippines if requested
            if philippines_only and not is_in_philippines(lat, lon):
                continue
            
            # Parse timestamp
            timestamp = props.get('time', 0) / 1000  # Convert from milliseconds
            eq_datetime = datetime.fromtimestamp(timestamp)
            
            earthquake = {
                'id': feature.get('id', ''),
                'magnitude': props.get('mag', 0),
                'location': props.get('place', 'Unknown'),
                'datetime': eq_datetime.strftime("%d %B %Y - %I:%M %p"),
                'timestamp': timestamp,
                
                # USGS-specific data
                'latitude': lat,
                'longitude': lon,
                'depth': depth,  # in kilometers
                'tsunami': props.get('tsunami', 0),  # 0 or 1
                'felt': props.get('felt'),  # Number of felt reports
                'cdi': props.get('cdi'),  # Community Decimal Intensity
                'mmi': props.get('mmi'),  # Modified Mercalli Intensity
                'alert': props.get('alert'),  # green, yellow, orange, red
                'sig': props.get('sig', 0),  # Significance (0-1000)
                'url': props.get('url', ''),
                'type': props.get('type', 'earthquake'),
                'status': props.get('status', 'automatic'),
                
                # Source
                'source': 'USGS',
                'net': props.get('net', 'us')
            }
            
            earthquakes.append(earthquake)
        
        print(f"✓ USGS: Found {len(earthquakes)} earthquakes")
        if philippines_only:
            print(f"  (Filtered for Philippines region)")
        
        return earthquakes
        
    except Exception as e:
        print(f"✗ Error fetching USGS data: {e}")
        return []


def enrich_phivolcs_with_usgs(phivolcs_eq, usgs_earthquakes, max_distance_km=50, max_time_diff_minutes=30):
    """
    Enrich a PHIVOLCS earthquake with USGS data if a match is found
    
    Matching criteria:
    - Similar magnitude (within 0.5)
    - Similar location (within max_distance_km)
    - Similar time (within max_time_diff_minutes)
    
    Args:
        phivolcs_eq: PHIVOLCS earthquake dict
        usgs_earthquakes: List of USGS earthquake dicts
        max_distance_km: Maximum distance to consider a match
        max_time_diff_minutes: Maximum time difference to consider a match
    
    Returns:
        Enriched earthquake dict with USGS data added
    """
    enriched = phivolcs_eq.copy()
    
    # Try to find matching USGS earthquake
    for usgs_eq in usgs_earthquakes:
        # Check magnitude similarity
        mag_diff = abs(float(phivolcs_eq.get('magnitude', 0)) - float(usgs_eq.get('magnitude', 0)))
        if mag_diff > 0.5:
            continue
        
        # For time comparison, we'd need PHIVOLCS coordinates
        # Since PHIVOLCS doesn't provide exact coords in the current implementation,
        # we'll match by magnitude and location name similarity
        
        # Simple location name matching (can be improved)
        phivolcs_loc = phivolcs_eq.get('location', '').lower()
        usgs_loc = usgs_eq.get('location', '').lower()
        
        # Check if locations mention similar places
        if any(word in usgs_loc for word in phivolcs_loc.split() if len(word) > 3):
            # Found a potential match!
            enriched['usgs_match'] = True
            enriched['tsunami'] = usgs_eq.get('tsunami', 0)
            enriched['felt'] = usgs_eq.get('felt')
            enriched['alert'] = usgs_eq.get('alert')
            enriched['depth'] = usgs_eq.get('depth')
            enriched['cdi'] = usgs_eq.get('cdi')
            enriched['sig'] = usgs_eq.get('sig', 0)
            enriched['usgs_url'] = usgs_eq.get('url', '')
            
            print(f"  ✓ Matched: {phivolcs_loc[:40]} with USGS data")
            break
    
    return enriched


def get_alert_color(alert_level):
    """Get RGB color for USGS alert level"""
    colors = {
        'green': (0, 200, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'red': (255, 0, 0),
    }
    return colors.get(alert_level, (128, 128, 128))


def get_depth_category(depth_km):
    """Categorize earthquake depth"""
    if depth_km < 70:
        return "Shallow", (255, 100, 100)  # Red - more dangerous
    elif depth_km < 300:
        return "Intermediate", (255, 200, 100)  # Orange
    else:
        return "Deep", (100, 200, 100)  # Green - less dangerous


def format_felt_reports(felt_count):
    """Format felt reports for display"""
    if not felt_count or felt_count == 0:
        return "No reports"
    elif felt_count == 1:
        return "1 person"
    elif felt_count < 10:
        return f"{felt_count} people"
    elif felt_count < 100:
        return f"{felt_count} people"
    else:
        return f"{felt_count}+ people"


if __name__ == "__main__":
    # Test the module
    print("\n" + "="*70)
    print("USGS EARTHQUAKE MONITOR TEST")
    print("="*70)
    
    # Test 1: Fetch Philippines earthquakes (4.5+)
    print("\n--- Test 1: Philippines Earthquakes (4.5+ past day) ---")
    earthquakes = fetch_usgs_earthquakes(feed='4.5_day', philippines_only=True)
    
    for eq in earthquakes[:5]:
        print(f"\n[{eq['magnitude']}] {eq['location']}")
        print(f"  Time: {eq['datetime']}")
        print(f"  Depth: {eq['depth']}km - {get_depth_category(eq['depth'])[0]}")
        print(f"  Tsunami: {'⚠️ POSSIBLE' if eq['tsunami'] == 1 else '✓ No threat'}")
        if eq['felt']:
            print(f"  Felt by: {format_felt_reports(eq['felt'])}")
        if eq['alert']:
            print(f"  Alert: {eq['alert'].upper()}")
        print(f"  URL: {eq['url']}")
    
    # Test 2: Fetch all recent earthquakes (not filtered)
    print("\n--- Test 2: All Major Earthquakes Worldwide (4.5+ past day) ---")
    all_quakes = fetch_usgs_earthquakes(feed='4.5_day', philippines_only=False)
    print(f"\nTotal worldwide: {len(all_quakes)} earthquakes")
    
    # Show top 3 by magnitude
    sorted_quakes = sorted(all_quakes, key=lambda x: x['magnitude'], reverse=True)
    print("\nTop 3 by magnitude:")
    for eq in sorted_quakes[:3]:
        print(f"  [{eq['magnitude']}] {eq['location']}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

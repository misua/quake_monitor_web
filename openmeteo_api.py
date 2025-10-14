#!/usr/bin/env python3
"""
Open-Meteo API Module
Handles all Open-Meteo API calls for weather, air quality, marine data, etc.
Separates API logic from GUI display code.
"""

import requests
import json
from datetime import datetime

# Configuration
LATITUDE = 6.9214  # Davao City, Philippines
LONGITUDE = 125.9045
LOCATION_NAME = "Davao City, Philippines"

# API Endpoints
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
MARINE_API = "https://marine-api.open-meteo.com/v1/marine"
FLOOD_API = "https://flood-api.open-meteo.com/v1/flood"

# Weather code to icon and description mapping
WEATHER_CODES = {
    0: ("☀️", "Clear", "Clear Sky"),
    1: ("🌤️", "Mainly Clear", "Mainly Clear"),
    2: ("⛅", "Partly Cloudy", "Partly Cloudy"),
    3: ("☁️", "Cloudy", "Overcast"),
    45: ("🌫️", "Fog", "Foggy"),
    48: ("🌫️", "Fog", "Rime Fog"),
    51: ("🌦️", "Light Drizzle", "Light Drizzle"),
    53: ("🌦️", "Drizzle", "Moderate Drizzle"),
    55: ("🌧️", "Heavy Drizzle", "Dense Drizzle"),
    56: ("🌧️", "Freezing Drizzle", "Light Freezing Drizzle"),
    57: ("🌧️", "Freezing Drizzle", "Dense Freezing Drizzle"),
    61: ("🌧️", "Light Rain", "Slight Rain"),
    63: ("🌧️", "Rain", "Moderate Rain"),
    65: ("🌧️", "Heavy Rain", "Heavy Rain"),
    66: ("🌧️", "Freezing Rain", "Light Freezing Rain"),
    67: ("🌧️", "Heavy Freezing Rain", "Heavy Freezing Rain"),
    71: ("🌨️", "Light Snow", "Slight Snow"),
    73: ("🌨️", "Snow", "Moderate Snow"),
    75: ("🌨️", "Heavy Snow", "Heavy Snow"),
    77: ("🌨️", "Snow Grains", "Snow Grains"),
    80: ("🌦️", "Rain Showers", "Slight Rain Showers"),
    81: ("🌧️", "Rain Showers", "Moderate Rain Showers"),
    82: ("🌧️", "Heavy Rain Showers", "Violent Rain Showers"),
    85: ("🌨️", "Snow Showers", "Slight Snow Showers"),
    86: ("🌨️", "Heavy Snow Showers", "Heavy Snow Showers"),
    95: ("⛈️", "Thunderstorm", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm + Hail", "Thunderstorm with Slight Hail"),
    99: ("⛈️", "Severe Thunderstorm", "Thunderstorm with Heavy Hail"),
}


def fetch_weather_data():
    """
    Fetch comprehensive weather data from Open-Meteo
    Returns: dict with current, hourly, and daily weather data
    """
    try:
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "pressure_msl",
                "cloud_cover",
            ],
            "hourly": [
                "temperature_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
                "visibility",
                "uv_index",
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "weather_code",
                "uv_index_max",
                "sunrise",
                "sunset",
            ],
            "timezone": "Asia/Manila",
            "forecast_days": 7
        }
        
        response = requests.get(WEATHER_API, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching weather data: {e}")
        return None


def fetch_air_quality_data():
    """
    Fetch air quality data including UV index, PM2.5, etc.
    Returns: dict with air quality metrics
    """
    try:
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": [
                "pm2_5",
                "pm10",
                "carbon_monoxide",
                "nitrogen_dioxide",
                "sulphur_dioxide",
                "ozone",
                "dust",
                "uv_index",
                "european_aqi",
                "us_aqi",
            ],
            "hourly": [
                "pm2_5",
                "pm10",
                "uv_index",
                "european_aqi",
            ],
            "timezone": "Asia/Manila",
            "forecast_days": 3
        }
        
        response = requests.get(AIR_QUALITY_API, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching air quality data: {e}")
        return None


def fetch_marine_data():
    """
    Fetch marine weather data including tides, waves, currents
    Returns: dict with marine data
    """
    try:
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "hourly": [
                "wave_height",
                "wave_direction",
                "wave_period",
                "ocean_current_velocity",
                "ocean_current_direction",
            ],
            "daily": [
                "wave_height_max",
                "wave_direction_dominant",
            ],
            "timezone": "Asia/Manila",
            "forecast_days": 3
        }
        
        response = requests.get(MARINE_API, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching marine data: {e}")
        return None


def fetch_flood_data():
    """
    Fetch flood/river discharge data
    Returns: dict with river discharge data
    """
    try:
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "daily": "river_discharge",
            "timezone": "Asia/Manila",
            "forecast_days": 7
        }
        
        response = requests.get(FLOOD_API, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching flood data: {e}")
        return None


def get_weather_description(weather_code):
    """Get weather icon, short description, and full description"""
    return WEATHER_CODES.get(weather_code, ("❓", "Unknown", "Unknown Weather"))


def get_uv_index_level(uv_index):
    """
    Get UV index risk level and color
    Returns: (level_name, color_rgb)
    """
    if uv_index is None:
        return ("Unknown", (128, 128, 128))
    
    if uv_index < 3:
        return ("Low", (0, 150, 0))  # Darker green for visibility
    elif uv_index < 6:
        return ("Moderate", (180, 140, 0))  # Darker yellow/gold
    elif uv_index < 8:
        return ("High", (255, 140, 0))  # Orange
    elif uv_index < 11:
        return ("Very High", (220, 0, 0))  # Red
    else:
        return ("Extreme", (148, 0, 211))  # Purple


def get_aqi_level(aqi, system="european"):
    """
    Get Air Quality Index level and color
    system: 'european' or 'us'
    Returns: (level_name, color_rgb)
    """
    if aqi is None:
        return ("Unknown", (128, 128, 128))
    
    if system == "european":
        # European AQI: 0-20 Good, 20-40 Fair, 40-60 Moderate, 60-80 Poor, 80-100 Very Poor, >100 Extremely Poor
        if aqi <= 20:
            return ("Good", (0, 150, 0))  # Darker green for better visibility
        elif aqi <= 40:
            return ("Fair", (180, 140, 0))  # Darker yellow/gold for better contrast
        elif aqi <= 60:
            return ("Moderate", (255, 140, 0))  # Orange
        elif aqi <= 80:
            return ("Poor", (220, 0, 0))  # Red
        elif aqi <= 100:
            return ("Very Poor", (148, 0, 211))  # Purple
        else:
            return ("Extremely Poor", (128, 0, 0))  # Dark red
    else:  # US AQI
        # US AQI: 0-50 Good, 51-100 Moderate, 101-150 Unhealthy for Sensitive, 151-200 Unhealthy, 201-300 Very Unhealthy, >300 Hazardous
        if aqi <= 50:
            return ("Good", (0, 200, 0))
        elif aqi <= 100:
            return ("Moderate", (255, 255, 0))
        elif aqi <= 150:
            return ("Unhealthy (Sensitive)", (255, 165, 0))
        elif aqi <= 200:
            return ("Unhealthy", (255, 0, 0))
        elif aqi <= 300:
            return ("Very Unhealthy", (148, 0, 211))
        else:
            return ("Hazardous", (128, 0, 0))


def get_pm25_level(pm25):
    """
    Get PM2.5 level and color
    Returns: (level_name, color_rgb)
    """
    if pm25 is None:
        return ("Unknown", (128, 128, 128))
    
    if pm25 <= 12:
        return ("Good", (0, 200, 0))
    elif pm25 <= 35:
        return ("Moderate", (255, 255, 0))
    elif pm25 <= 55:
        return ("Unhealthy (Sensitive)", (255, 165, 0))
    elif pm25 <= 150:
        return ("Unhealthy", (255, 0, 0))
    elif pm25 <= 250:
        return ("Very Unhealthy", (148, 0, 211))
    else:
        return ("Hazardous", (128, 0, 0))


# For backward compatibility with existing code
def fetch_weather():
    """Legacy function - calls fetch_weather_data()"""
    return fetch_weather_data()


if __name__ == "__main__":
    """Test the API functions"""
    print("\n" + "="*80)
    print("Testing Open-Meteo API Module".center(80))
    print("="*80 + "\n")
    
    print("1. Fetching Weather Data...")
    weather = fetch_weather_data()
    if weather:
        current = weather.get('current', {})
        temp = current.get('temperature_2m', 'N/A')
        print(f"   ✓ Temperature: {temp}°C")
    
    print("\n2. Fetching Air Quality Data...")
    air_quality = fetch_air_quality_data()
    if air_quality:
        current = air_quality.get('current', {})
        aqi = current.get('european_aqi', 'N/A')
        pm25 = current.get('pm2_5', 'N/A')
        print(f"   ✓ AQI: {aqi}")
        print(f"   ✓ PM2.5: {pm25} μg/m³")
    
    print("\n3. Fetching Marine Data...")
    marine = fetch_marine_data()
    if marine:
        print(f"   ✓ Marine data available")
    
    print("\n4. Fetching Flood Data...")
    flood = fetch_flood_data()
    if flood:
        print(f"   ✓ Flood data available")
    
    print("\n" + "="*80 + "\n")

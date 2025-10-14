#!/usr/bin/env python3
"""
Sea Level Monitor Module
Fetches and analyzes real-time sea level data from IOC Sea Level Monitoring Station
Detects anomalies that could indicate tsunami activity
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from collections import deque

# Configuration
IOC_BASE_URL = "http://www.ioc-sealevelmonitoring.org/bgraph.php"
STATION_CODE = "davo"  # Davao, Philippines
HISTORY_SIZE = 30  # Keep last 30 readings (30 minutes)

# Anomaly thresholds (in meters)
WARNING_THRESHOLD = 0.3  # 30cm deviation
CRITICAL_THRESHOLD = 0.5  # 50cm deviation


class SeaLevelMonitor:
    """Monitor sea level data and detect anomalies"""
    
    def __init__(self, station_code=STATION_CODE):
        self.station_code = station_code
        self.history = deque(maxlen=HISTORY_SIZE)  # Rolling window of readings
        self.last_fetch_time = 0
        self.fetch_interval = 60  # Fetch every 60 seconds
        self.current_data = None
        
    def fetch_sea_level_data(self):
        """Fetch latest sea level data from IOC station"""
        try:
            # Fetch last 30 minutes of data
            url = f"{IOC_BASE_URL}?code={self.station_code}&output=tab&period=0.5"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML table
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                return None
            
            rows = table.find_all('tr')[1:]  # Skip header
            
            readings = []
            for row in rows[-30:]:  # Get last 30 readings
                cols = row.find_all('td')
                if len(cols) >= 4:
                    try:
                        time_str = cols[0].text.strip()
                        # Use rad (detided) measurement - best for tsunami detection
                        rad_value = cols[3].text.strip()
                        
                        if rad_value and rad_value != ' ':
                            reading = {
                                'time': time_str,
                                'level': float(rad_value),
                                'timestamp': time.time()
                            }
                            readings.append(reading)
                    except (ValueError, IndexError):
                        continue
            
            return readings
            
        except Exception as e:
            print(f"Error fetching sea level data: {e}")
            return None
    
    def update_history(self, readings):
        """Update historical data with new readings"""
        if readings:
            for reading in readings:
                self.history.append(reading)
    
    def calculate_average(self, window_size=None):
        """Calculate average sea level from history"""
        if not self.history:
            return None
        
        if window_size:
            data = list(self.history)[-window_size:]
        else:
            data = list(self.history)
        
        if not data:
            return None
        
        return sum(r['level'] for r in data) / len(data)
    
    def detect_anomaly(self, current_level):
        """Detect if current sea level is anomalous"""
        if len(self.history) < 10:  # Need at least 10 readings
            return "INSUFFICIENT_DATA", 0.0
        
        # Calculate baseline (average of older readings, excluding last 5)
        if len(self.history) >= 15:
            baseline = self.calculate_average(window_size=len(self.history) - 5)
        else:
            baseline = self.calculate_average()
        
        if baseline is None:
            return "NORMAL", 0.0
        
        # Calculate deviation
        deviation = abs(current_level - baseline)
        
        # Determine status
        if deviation >= CRITICAL_THRESHOLD:
            return "CRITICAL", deviation
        elif deviation >= WARNING_THRESHOLD:
            return "WARNING", deviation
        else:
            return "NORMAL", deviation
    
    def calculate_trend(self):
        """Calculate if sea level is rising, falling, or stable"""
        if len(self.history) < 5:
            return "UNKNOWN"
        
        recent = list(self.history)[-5:]
        first_avg = sum(r['level'] for r in recent[:2]) / 2
        last_avg = sum(r['level'] for r in recent[-2:]) / 2
        
        diff = last_avg - first_avg
        
        if diff > 0.05:  # Rising more than 5cm
            return "RISING"
        elif diff < -0.05:  # Falling more than 5cm
            return "FALLING"
        else:
            return "STABLE"
    
    def get_status(self):
        """Get current sea level status with anomaly detection"""
        current_time = time.time()
        
        # Fetch new data if interval has passed
        if current_time - self.last_fetch_time >= self.fetch_interval:
            readings = self.fetch_sea_level_data()
            if readings:
                self.update_history(readings)
                self.current_data = readings[-1] if readings else None
                self.last_fetch_time = current_time
        
        # Return status
        if not self.current_data or not self.history:
            return {
                'status': 'NO_DATA',
                'level': None,
                'trend': 'UNKNOWN',
                'deviation': 0.0,
                'last_update': 'Never',
                'alert': False
            }
        
        current_level = self.current_data['level']
        anomaly_status, deviation = self.detect_anomaly(current_level)
        trend = self.calculate_trend()
        
        # Format last update time (convert UTC to Philippine Time)
        try:
            last_update_utc = datetime.strptime(self.current_data['time'], "%Y-%m-%d %H:%M:%S")
            # Convert to Philippine Time (UTC+8)
            last_update_pht = last_update_utc + timedelta(hours=8)
            last_update_str = last_update_pht.strftime("%H:%M PHT")
        except:
            last_update_str = "Unknown"
        
        return {
            'status': anomaly_status,
            'level': round(current_level, 2),
            'trend': trend,
            'deviation': round(deviation, 2),
            'last_update': last_update_str,
            'alert': anomaly_status in ['WARNING', 'CRITICAL']
        }


# Global instance
_monitor = None

def get_sea_level_monitor():
    """Get or create global sea level monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = SeaLevelMonitor()
    return _monitor


def get_sea_level_status():
    """Convenience function to get current sea level status"""
    monitor = get_sea_level_monitor()
    return monitor.get_status()


if __name__ == "__main__":
    # Test the module
    print("Testing Sea Level Monitor...")
    monitor = SeaLevelMonitor()
    
    status = monitor.get_status()
    print(f"\nStatus: {status['status']}")
    print(f"Level: {status['level']}m")
    print(f"Trend: {status['trend']}")
    print(f"Deviation: {status['deviation']}m")
    print(f"Last Update: {status['last_update']}")
    print(f"Alert: {status['alert']}")

#!/usr/bin/env python3
"""
Test script to verify the setup is correct
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    errors = []
    
    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError as e:
        errors.append(f"✗ FastAPI: {e}")
    
    try:
        import uvicorn
        print("✓ Uvicorn")
    except ImportError as e:
        errors.append(f"✗ Uvicorn: {e}")
    
    try:
        import jinja2
        print("✓ Jinja2")
    except ImportError as e:
        errors.append(f"✗ Jinja2: {e}")
    
    try:
        import requests
        print("✓ Requests")
    except ImportError as e:
        errors.append(f"✗ Requests: {e}")
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup4")
    except ImportError as e:
        errors.append(f"✗ BeautifulSoup4: {e}")
    
    return errors


def test_parent_modules():
    """Test if parent directory modules are accessible"""
    print("\n🔍 Testing parent modules...")
    
    PARENT_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(PARENT_DIR))
    
    errors = []
    
    try:
        from openmeteo_api import fetch_weather_data
        print("✓ openmeteo_api")
    except ImportError as e:
        errors.append(f"✗ openmeteo_api: {e}")
    
    try:
        from usgs_monitor import fetch_usgs_earthquakes
        print("✓ usgs_monitor")
    except ImportError as e:
        errors.append(f"✗ usgs_monitor: {e}")
    
    try:
        from sea_level_monitor import get_sea_level_status
        print("✓ sea_level_monitor")
    except ImportError as e:
        errors.append(f"✗ sea_level_monitor: {e}")
    
    try:
        from pagasa_monitor import get_typhoon_status, fetch_rainfall_data
        print("✓ pagasa_monitor")
    except ImportError as e:
        errors.append(f"✗ pagasa_monitor: {e}")
    
    return errors


def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    base_dir = Path(__file__).parent
    
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "api/__init__.py",
        "api/weather.py",
        "api/earthquake.py",
        "api/tsunami.py",
        "api/monitoring.py",
        "templates/base.html",
        "templates/index.html",
        "templates/components/weather.html",
        "templates/components/phivolcs.html",
        "templates/components/usgs.html",
        "templates/components/top5.html",
        "templates/components/tsunami.html",
        "templates/components/sea_level.html",
        "templates/components/typhoon.html",
        "templates/components/rainfall.html",
        "static/css/styles.css",
        "static/js/theme.js",
    ]
    
    errors = []
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            errors.append(f"✗ Missing: {file_path}")
    
    return errors


def main():
    print("=" * 60)
    print("🌍 Earthquake & Weather Monitor - Setup Test")
    print("=" * 60)
    
    all_errors = []
    
    # Test imports
    errors = test_imports()
    all_errors.extend(errors)
    
    # Test parent modules
    errors = test_parent_modules()
    all_errors.extend(errors)
    
    # Test file structure
    errors = test_file_structure()
    all_errors.extend(errors)
    
    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print("❌ SETUP INCOMPLETE")
        print("=" * 60)
        print("\nErrors found:")
        for error in all_errors:
            print(f"  {error}")
        print("\nPlease fix the errors above before running the application.")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🚀 Your setup is complete!")
        print("\nTo start the application:")
        print("  ./start.sh")
        print("\nOr manually:")
        print("  python app.py")
        print("\nThen open: http://localhost:8000")
        sys.exit(0)


if __name__ == "__main__":
    main()

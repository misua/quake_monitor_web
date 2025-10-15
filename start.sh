#!/bin/bash
# Startup script for Earthquake & Weather Monitor

echo "🌍 Starting Earthquake & Weather Monitor..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
python -m pip install -q -r requirements.txt

# Start the application
echo "Starting web server on http://0.0.0.0:8000"
echo "Press Ctrl+C to stop"
python app.py

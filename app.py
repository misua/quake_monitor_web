#!/usr/bin/env python3
"""
Earthquake and Weather Monitor - Web Application
FastAPI + HTMX implementation
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import existing modules
SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PARENT_DIR))

# Import API routers
from api import weather, earthquake, tsunami, monitoring

# Import profiling utilities
from utils.profiling import init_profiling
from utils.performance_monitor import PerformanceMonitorMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
LATITUDE = 7.190708
LONGITUDE = 125.455338
LOCATION_NAME = "Davao City, Philippines"

# Initialize FastAPI app
app = FastAPI(title="Earthquake & Weather Monitor", version="2.0")

# Add performance monitoring middleware
app.add_middleware(PerformanceMonitorMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory=str(SCRIPT_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(SCRIPT_DIR / "templates"))

# Include routers
app.include_router(weather.router, prefix="/api", tags=["weather"])
app.include_router(earthquake.router, prefix="/api", tags=["earthquake"])
app.include_router(tsunami.router, prefix="/api", tags=["tsunami"])
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("🌍 Starting Earthquake & Weather Monitor...")
    
    # Initialize profiling (if enabled)
    profiling_initialized = init_profiling()
    if profiling_initialized:
        logger.info("📊 Continuous profiling enabled - data will be sent to Grafana Cloud")
    else:
        logger.info("📊 Continuous profiling disabled")
    
    logger.info("✓ Application startup complete")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "location": LOCATION_NAME,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

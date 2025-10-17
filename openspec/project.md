# Project Context

## Purpose

Real-time monitoring dashboard for earthquakes, weather, tsunamis, typhoons, and environmental data for Davao City, Philippines. Provides critical safety information through a responsive web interface with automatic day/night themes.

## Tech Stack

- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Frontend**: HTMX, TailwindCSS, Jinja2 templates
- **Data Sources**: PHIVOLCS, USGS, Open-Meteo, PAGASA, IOC Sea Level Monitoring
- **HTTP Clients**: requests, httpx, BeautifulSoup4, lxml
- **Scheduling**: APScheduler for background data fetching

## Project Conventions

### Code Style
- Python PEP 8 style guidelines
- Async/await for FastAPI endpoints
- Type hints where applicable
- Descriptive variable names for data sources and locations

### Architecture Patterns
- FastAPI router-based modular architecture (`api/` directory)
- Template-based rendering with HTMX for dynamic updates
- Stateless API endpoints with external data fetching
- No database - real-time data fetching only

### Testing Strategy
- Manual testing via web interface
- Health check endpoint for monitoring
- Test setup script (`test_setup.py`) for validating data sources

### Git Workflow
- Main branch for production-ready code
- Feature branches for new capabilities
- Direct commits for small fixes and documentation

## Domain Context

- **Location**: Davao City, Philippines (7.190708°N, 125.455338°E)
- **Critical Data**: Earthquake monitoring (PHIVOLCS for local, USGS for global M4.5+)
- **Update Intervals**: Weather (30s), Earthquakes (60s), Tsunami/Typhoon (5min)
- **User Base**: Local residents monitoring natural disaster risks
- **Operational Issue**: Intermittent segmentation faults with no error logs

## Important Constraints

- **No database**: All data fetched in real-time from external APIs
- **External API reliability**: Dependent on PHIVOLCS, USGS, PAGASA uptime
- **Network connectivity**: Requires stable internet for data fetching
- **Free tier services**: Must use free/public APIs only
- **Minimal infrastructure**: Single-instance deployment, no complex orchestration

## External Dependencies

- **PHIVOLCS**: Philippine earthquake data (https://earthquake.phivolcs.dost.gov.ph/)
- **USGS**: Global earthquake data (M4.5+)
- **Open-Meteo**: Weather, UV index, air quality data
- **PAGASA**: Typhoon tracking and rainfall monitoring
- **IOC**: Sea level monitoring and tsunami warnings
- **Grafana Cloud**: Continuous profiling (Pyroscope) - free tier

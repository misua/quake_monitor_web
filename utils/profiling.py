"""
Grafana Cloud Profiles (Pyroscope) Integration
Continuous profiling for debugging segmentation faults and performance issues
"""

import os
import logging

logger = logging.getLogger(__name__)


def init_profiling():
    """
    Initialize Pyroscope profiler if enabled via environment variables.
    
    Environment Variables:
        PROFILING_ENABLED: Set to 'true' to enable profiling (default: false)
        PYROSCOPE_SERVER_URL: Grafana Cloud Profiles URL
        PYROSCOPE_USERNAME: Grafana Cloud username
        PYROSCOPE_API_KEY: Grafana Cloud API key
        ENVIRONMENT: Environment name for tagging (default: production)
    
    Returns:
        bool: True if profiling was initialized, False otherwise
    """
    # Check if profiling is enabled
    profiling_enabled = os.getenv("PROFILING_ENABLED", "false").lower() == "true"
    
    if not profiling_enabled:
        logger.info("Profiling is disabled (PROFILING_ENABLED=false)")
        return False
    
    # Validate required environment variables
    server_url = os.getenv("PYROSCOPE_SERVER_URL")
    username = os.getenv("PYROSCOPE_USERNAME")
    api_key = os.getenv("PYROSCOPE_API_KEY")
    
    if not all([server_url, username, api_key]):
        logger.warning(
            "Profiling is enabled but credentials are missing. "
            "Required: PYROSCOPE_SERVER_URL, PYROSCOPE_USERNAME, PYROSCOPE_API_KEY"
        )
        return False
    
    try:
        import pyroscope
        
        # Configure Pyroscope
        pyroscope.configure(
            application_name="quake-monitor-web",
            server_address=server_url,
            basic_auth_username=username,
            basic_auth_password=api_key,
            sample_rate=100,  # 100Hz sampling (default)
            detect_subprocesses=False,  # Single process app
            oncpu=True,  # CPU profiling only
            gil_only=True,  # Focus on GIL-holding threads
            enable_logging=True,  # Enable profiling logs
            tags={
                "environment": os.getenv("ENVIRONMENT", "production"),
                "version": "2.0",
                "region": "davao-city",
                "app": "earthquake-weather-monitor"
            }
        )
        
        logger.info(
            f"✓ Pyroscope profiler initialized successfully\n"
            f"  Server: {server_url}\n"
            f"  Application: quake-monitor-web\n"
            f"  Sample Rate: 100Hz\n"
            f"  Environment: {os.getenv('ENVIRONMENT', 'production')}"
        )
        return True
        
    except ImportError:
        logger.error(
            "Profiling is enabled but pyroscope-io is not installed. "
            "Install it with: pip install pyroscope-io"
        )
        return False
        
    except Exception as e:
        logger.error(f"Failed to initialize Pyroscope profiler: {e}")
        return False


def get_profiling_wrapper():
    """
    Get the Pyroscope tag_wrapper for adding labels to specific code sections.
    
    Returns:
        callable or None: tag_wrapper function if profiling is enabled, None otherwise
    
    Example:
        wrapper = get_profiling_wrapper()
        if wrapper:
            with wrapper({"endpoint": "phivolcs", "data_source": "external_api"}):
                # Your code here
                pass
    """
    profiling_enabled = os.getenv("PROFILING_ENABLED", "false").lower() == "true"
    
    if not profiling_enabled:
        return None
    
    try:
        from pyroscope import tag_wrapper
        return tag_wrapper
    except ImportError:
        return None

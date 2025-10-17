"""
Performance Monitoring Middleware
Automatically logs slow requests and resource-heavy operations
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Thresholds for alerting
SLOW_REQUEST_THRESHOLD = 2.0  # seconds
VERY_SLOW_REQUEST_THRESHOLD = 5.0  # seconds


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor request performance and log slow operations.
    
    This helps identify which endpoints are consuming excessive resources
    and potentially causing segfaults.
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log based on severity
        endpoint = f"{request.method} {request.url.path}"
        
        if duration > VERY_SLOW_REQUEST_THRESHOLD:
            logger.error(
                f"🚨 VERY SLOW REQUEST: {endpoint} took {duration:.2f}s "
                f"(threshold: {VERY_SLOW_REQUEST_THRESHOLD}s) - POTENTIAL SEGFAULT RISK!"
            )
        elif duration > SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"⚠️  SLOW REQUEST: {endpoint} took {duration:.2f}s "
                f"(threshold: {SLOW_REQUEST_THRESHOLD}s)"
            )
        else:
            logger.debug(f"✓ {endpoint} completed in {duration:.3f}s")
        
        # Add performance header to response
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response


def log_operation_time(operation_name: str):
    """
    Decorator to log execution time of specific functions.
    
    Usage:
        @log_operation_time("fetch_phivolcs_earthquakes")
        def fetch_phivolcs_earthquakes():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > VERY_SLOW_REQUEST_THRESHOLD:
                    logger.error(
                        f"🚨 CRITICAL: {operation_name} took {duration:.2f}s - "
                        f"This may cause segfaults!"
                    )
                elif duration > SLOW_REQUEST_THRESHOLD:
                    logger.warning(
                        f"⚠️  SLOW: {operation_name} took {duration:.2f}s"
                    )
                else:
                    logger.info(f"✓ {operation_name} completed in {duration:.3f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"❌ ERROR in {operation_name} after {duration:.2f}s: {e}"
                )
                raise
        return wrapper
    return decorator


def get_performance_summary():
    """
    Generate a summary of performance issues to check in logs.
    
    Returns:
        str: Performance monitoring guide
    """
    return """
    🔍 PERFORMANCE MONITORING GUIDE
    
    Look for these patterns in logs:
    
    🚨 CRITICAL ISSUES (Potential Segfault Causes):
       - "VERY SLOW REQUEST" (>5s)
       - Repeated errors in same endpoint
       - Memory allocation warnings
       - SSL/TLS errors
       - uvloop/asyncio errors
    
    ⚠️  WARNING SIGNS:
       - "SLOW REQUEST" (>2s)
       - Increasing response times
       - Cache misses
       - Network timeouts
    
    ✓ HEALTHY:
       - Most requests <2s
       - Cache hits
       - No repeated errors
    
    📊 Check Grafana Cloud Profiles for:
       - CPU spikes before crashes
       - Memory allocation patterns
       - Hot paths in flame graphs
    """

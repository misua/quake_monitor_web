# Fix HTTP Timeout Issues to Prevent Segfaults

## Problem Statement

Monitoring revealed that HTTP requests are taking 77+ seconds before timing out, causing segmentation faults every 2 days. The issue exists across multiple external API calls throughout the codebase.

### Evidence

- Performance monitoring logs show: `GET /api/earthquakes/phivolcs took 76.97s`
- Similar issues observed in `/api/earthquakes/usgs` endpoint
- Grafana Cloud Profiles flame graphs show excessive time in HTML parsing and network calls
- Application experiences segfaults every ~48 hours

### Root Cause

1. **Inconsistent timeout configuration** - Some use single value (30s), others use tuple format
2. **Timeouts too long** - 30-second timeouts allow hanging requests
3. **No response size limits** - Large/malformed HTML can cause parser crashes
4. **Scattered timeout logic** - Each file implements its own timeout strategy

## Proposed Solution: Option 1 (Recommended)

**Centralized HTTP Client Utility** - Create `utils/http_client.py` with strict timeouts and size limits.

### Benefits
- Single source of truth for timeout configuration
- Easy to tune globally
- Consistent error handling
- Better observability

### Implementation
1. Create `utils/http_client.py` with safe_get(), safe_get_json(), safe_get_html()
2. Update 7 files to use centralized client
3. Test and monitor for 48 hours

**Estimated time**: 2.5 hours + 48h monitoring

## Alternative: Option 3 (Quick Fix)

**Fix Critical Files Only** - Update just the HTML scrapers that cause segfaults.

### Benefits
- Faster implementation
- Lower risk
- Addresses immediate segfault causes

### Implementation
1. Fix `api/tsunami.py` (timeout=30s → tuple format)
2. Fix `pagasa_monitor.py` (add size limits)
3. Fix `usgs_monitor.py` (tuple format)

**Estimated time**: 1 hour + 48h monitoring

## Recommendation

**Start with Option 3 (Quick Fix)**, then implement Option 1 (Centralized Client) as a follow-up.

### Rationale
- Gets immediate fix deployed faster
- Reduces segfault risk today
- Allows time to design proper centralized solution
- Lower risk of breaking changes

## Success Criteria

- ✅ No HTTP requests exceed 15 seconds
- ✅ No segfaults for 7+ days
- ✅ Performance monitoring shows no CRITICAL timeout alerts

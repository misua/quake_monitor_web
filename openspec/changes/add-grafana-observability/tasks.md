## 1. Setup and Configuration

- [x] 1.1 Add `pyroscope-io` to `requirements.txt`
- [x] 1.2 Add Grafana Cloud environment variables to `.env.example`
- [x] 1.3 Create profiling configuration module (`utils/profiling.py`)

## 2. Application Instrumentation

- [x] 2.1 Initialize Pyroscope profiler in `app.py` startup
- [x] 2.2 Add conditional profiling based on environment variable
- [x] 2.3 Add profiling labels to critical API endpoints (earthquake, weather, monitoring)
- [x] 2.4 Configure profiling tags for application metadata (version, environment)

## 3. Documentation

- [x] 3.1 Update `README.md` with Grafana Cloud setup instructions
- [x] 3.2 Document how to obtain Grafana Cloud credentials
- [x] 3.3 Add troubleshooting section for profiling
- [x] 3.4 Document how to view profiles in Grafana Cloud UI

## 4. Testing and Validation

- [ ] 4.1 Test profiling with local Pyroscope server (optional)
- [ ] 4.2 Verify data appears in Grafana Cloud Profiles
- [ ] 4.3 Validate profiling overhead is minimal (<5% CPU)
- [ ] 4.4 Test application behavior with profiling disabled
- [ ] 4.5 Verify segfault debugging capability with flame graphs

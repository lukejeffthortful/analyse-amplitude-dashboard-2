# Amplitude Dashboard Analyzer - Project Notes

## Project Overview
Analytics tool that fetches data from Amplitude dashboard charts and generates weekly executive summaries for business reporting. The project has optional GA4 integration for comparative analysis between Amplitude and Google Analytics 4.

## Tech Stack
- **Language**: Python 3.10+
- **Dependencies**: 
  - requests (API calls)
  - python-dotenv (environment management)
  - google-analytics-data (GA4 integration)
  - google-auth (GA4 authentication)
  - tenacity (retry logic)

## Core Architecture

### Main Components
1. **amplitude_analyzer.py** - Main entry point and orchestrator
2. **amplitude_data_handler.py** - Handles Amplitude API interactions
3. **ga4_data_handler.py** - Handles GA4 API interactions
4. **unified_analyzer.py** - Combines both data sources for comparative analysis

### Key Features
- Fetches weekly metrics from Amplitude charts
- Calculates Year-over-Year (YoY) comparisons
- Breaks down metrics by platform (Apps, Web, Combined)
- Optional GA4 integration for variance analysis
- Automated weekly reports via GitHub Actions
- Slack notifications support

## Data Flow
1. Fetches data from 7 configured Amplitude charts
2. Processes CSV data with platform segmentation
3. Calculates YoY changes for sessions, conversion rates
4. Optionally fetches GA4 data for comparison
5. Generates executive summary and JSON analysis
6. Sends results to Slack (if configured)

## Configuration

### Environment Variables
```
AMPLITUDE_API_KEY       # Amplitude API authentication
AMPLITUDE_SECRET_KEY    # Amplitude API authentication
SLACK_WEBHOOK_URL      # Optional Slack notifications
GA4_ENABLED            # Enable GA4 integration (true/false)
GA4_WEB_PROPERTY_ID    # GA4 web property
GA4_APP_PROPERTY_ID    # GA4 app property
GA4_SERVICE_ACCOUNT_PATH # Path to GA4 service account JSON
```

### Amplitude Chart IDs
- Sessions (Current Year): `y0ivh3am`
- Sessions (Previous Year): `5vbaz782`
- Sessions per user (Current Year): `pc9c0crz`
- Sessions per user (Previous Year): `3d400y6n`
- Session Conversion % (Current Year): `42c5gcv4`
- Session Conversion % (Previous Year): `3t0wgn4i`
- User Conversion %: `4j2gp4ph`

## Key Business Logic

### Week Calculations
- Uses ISO week numbers (1-53)
- Week runs Monday to Sunday
- Automatically analyzes previous week if no target specified

### YoY Comparisons
- Compares same ISO week across years
- Percentage changes for sessions
- Percentage point changes for conversion rates
- Platform-specific breakdowns (Apps, Web, Combined)

### Executive Summary Format
Generates concise summaries like:
```
Week 29 Analysis (2025-07-14 to 2025-07-20):

Sessions down 11% YoY, but session conversion 2 ppts better YoY. 
Web session conversion was up 3 ppts YoY & user conversion up 5ppt YoY...
```

## Automation
- GitHub Actions workflow runs weekly (Mondays at 7:00 AM)
- Automatically commits analysis results
- Can be manually triggered via workflow_dispatch

## API Integration Notes

### Amplitude API
- Uses CSV endpoint: `/api/3/chart/{chart_id}/csv`
- HTTP Basic Auth with API/Secret keys
- Returns JSON with CSV data in 'data' field
- 2-second delay between calls to avoid rate limits
- Cost-based rate limiting (108,000 cost/hour max)

### GA4 API
- Uses Google Analytics Data API
- Service account authentication
- Fetches sessions, conversions, revenue metrics
- Handles both web and app properties

## File Structure
```
/
├── amplitude_analyzer.py      # Main orchestrator
├── amplitude_data_handler.py  # Amplitude API handler
├── ga4_data_handler.py       # GA4 API handler
├── unified_analyzer.py       # Combined analysis
├── requirements.txt          # Python dependencies
├── plan.md                   # Business requirements
├── .github/workflows/        # GitHub Actions
│   └── weekly-report.yml     # Weekly automation
└── ga4_service_account/      # GA4 credentials (gitignored)
```

## Common Operations

### Manual Analysis
```bash
python3 amplitude_analyzer.py
```

### Test Specific Week
```python
# Modify amplitude_analyzer.py to set target_week
target_week = 29  # Analyze week 29
```

### Enable/Disable GA4
Set `GA4_ENABLED=true` in environment or `.env` file

## Troubleshooting
- API errors: Check credentials in `.env`
- Rate limits: Increase delays between API calls
- Missing data: Verify chart IDs and date ranges
- GA4 errors: Check service account permissions
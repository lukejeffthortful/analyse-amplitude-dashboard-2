# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical: Safe Development Approach

**ALWAYS follow the safe development workflow documented in SAFE_DEVELOPMENT_GUIDE.md**

### Key Rules:
1. **NEVER modify the `main` branch directly** - it has working production code
2. **ALWAYS use `development-iteration` branch** for any changes
3. **NEVER push to remote** without explicit user permission
4. **ALWAYS test locally first** using `test_local.py`

## Common Development Commands

### Build and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Check current branch (should be development-iteration)
git branch --show-current

# Create backup before major changes
cp amplitude_analyzer.py backups/amplitude_analyzer_$(date +%Y%m%d_%H%M%S).py
```

### Running and Testing
```bash
# Main execution
python3 amplitude_analyzer.py

# Test changes locally without side effects
python3 test_local.py

# Run specific test files
python3 test_appsflyer.py
python3 test_example_dates.py
python3 test_last_week_data.py

# Validate syntax before committing
python3 -m py_compile *.py
```

### Development Testing
- Use `.env.development` for local testing
- Set `SLACK_WEBHOOK_URL=''` to prevent notifications
- Test with old weeks to avoid interfering with current data

## High-Level Architecture

### Core Components and Data Flow
```
amplitude_analyzer.py (Main Orchestrator)
    ├── amplitude_data_handler.py (Amplitude API)
    │   └── Fetches from 7 configured charts
    ├── ga4_data_handler.py (Google Analytics 4 API)
    │   └── Optional comparative analysis
    ├── appsflyer_data_handler.py (AppsFlyer API)
    │   └── Partners report for attribution data
    └── unified_analyzer.py (Cross-platform analysis)
        └── Generates executive summaries
```

### Key Business Logic
1. **Week Calculations**: ISO weeks (Monday-Sunday), analyzes previous week by default
2. **YoY Comparisons**: Same ISO week across years, percentage/point changes
3. **Platform Segmentation**: Apps Only, Web Only, App + Web combined
4. **Metrics**: Sessions, Sessions per User, Session Conversion %, User Conversion %

### Production Environment
- GitHub Actions runs every Monday at 7:00 AM on `main` branch
- Workflow: `.github/workflows/weekly-report.yml`
- Sends reports to Slack webhook
- Automatically commits analysis results

## AppsFlyer Integration Notes

### API Access Limitations
- **IMPORTANT**: Our account does NOT have access to the Master API
- We only have Partner API access via: `/api/agg-data/export/app/{app_id}/partners_report/v5`
- Partner API has a limit of 10 API calls per day

### Key Difference: UI Export vs API Access
- **UI CSV Exports**: Shows ALL media sources including Google Ads (googleadwords_int)
  - Manual exports allowed by media source privacy policies
  - Can be downloaded from AppsFlyer dashboard
- **Partner API**: Restricted by media source data-sharing policies
  - Google Ads, Meta, etc. block programmatic API access
  - Only returns data for sources allowing third-party API access

### Available Data Sources
- **Via API**: Organic, website-thortful, Facebook Ads, QR_code, transactional_postmark
- **Missing from API**: Google Ads (googleadwords_int), potentially other restricted sources
- **Available via UI Export**: All sources including Google Ads

### Recommended Workflow
1. Use Partner API for available sources (automated)
2. Export CSV from UI weekly for complete data (manual)
3. Process CSV to capture Google Ads and other restricted sources

### Working Configuration
- Endpoint: `https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/partners_report/v5`
- Authentication: Bearer token in header
- CSV Column for media source: "Media Source (pid)" (not "Media Source")

## Configuration Reference

### Required Environment Variables
```
AMPLITUDE_API_KEY       # Amplitude API authentication
AMPLITUDE_SECRET_KEY    # Amplitude API authentication
SLACK_WEBHOOK_URL      # Optional Slack notifications (empty for local testing)
GA4_ENABLED            # Enable GA4 integration (true/false)
GA4_WEB_PROPERTY_ID    # GA4 web property (if enabled)
GA4_APP_PROPERTY_ID    # GA4 app property (if enabled)
GA4_SERVICE_ACCOUNT_PATH # Path to GA4 service account JSON (if enabled)
APPSFLYER_API_TOKEN    # AppsFlyer authentication
APPSFLYER_APP_ID       # AppsFlyer app identifier
```

### Chart IDs (Configured in amplitude_analyzer.py)
- Sessions (Current/Previous Year): `y0ivh3am` / `5vbaz782`
- Sessions per user (Current/Previous Year): `pc9c0crz` / `3d400y6n`
- Session Conversion % (Current/Previous Year): `42c5gcv4` / `3t0wgn4i`
- User Conversion %: `4j2gp4ph`

See PROJECT_NOTES.md for detailed technical information.
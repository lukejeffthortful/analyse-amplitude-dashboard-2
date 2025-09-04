# AppsFlyer Integration Guide

## Overview
This integration adds AppsFlyer install data to the analytics dashboard, providing insights into app installs by media source and campaign.

## Setup

### 1. Environment Variables
Add these to your `.env` file:
```
APPSFLYER_API_TOKEN=your_api_token_here
APPSFLYER_APP_ID=your_app_id_here
```

### 2. Getting Your API Credentials
- **API Token**: Found in AppsFlyer Dashboard → Integration → API Access
- **App ID**: Your app identifier (e.g., `com.company.app` for Android or `id123456789` for iOS)

## Testing the Integration

### Run the Proof of Concept
```bash
python test_appsflyer.py
```

This will:
1. Fetch last week's install data
2. Group installs by media source and campaign
3. Generate summary reports
4. Save data to JSON files for inspection

### Expected Output Files
- `test_appsflyer_weekly_data.json` - Raw weekly data
- `test_appsflyer_summary.txt` - Formatted summary
- `test_appsflyer_7day_data.json` - Last 7 days data

## API Details

### Important API Limitations

**Our AppsFlyer account does NOT have access to the Master API.** This creates significant limitations:

#### Master API vs Partner API Access
- **Master API** (NOT available to us):
  - Would provide aggregated analytics and campaign performance KPIs
  - Would show data for ALL media sources including Google Ads (google_int)
  - Equivalent to what you see in the AppsFlyer dashboard UI
  - Requires higher-tier pricing plan

- **Partner API** (what we have):
  - Subject to data-sharing policies of each media source
  - Google, Meta, and other major networks restrict API access
  - Can only access data for sources that allow third-party API sharing

#### UI Export vs API Access
- **UI CSV Exports**: Can include ALL media sources (including Google Ads)
  - Considered manual, user-initiated action
  - Media sources allow manual exports as part of privacy policies
  
- **API Access**: Restricted by media source policies
  - Automated/programmatic access more tightly controlled
  - Google Ads (google_int) and similar sources block API access

### Current Endpoint (Partner API)
```
https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/partners_report/v5
```

### Key Parameters
- CSV format required
- Date range in YYYY-MM-DD format
- Limited to 10 API calls per day

### Data Structure
The handler returns data in this format:
```json
{
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-01-07"
  },
  "total_installs": 1234,
  "by_media_source": {
    "Facebook Ads": 500,
    "Google Ads": 300,
    "Organic": 434
  },
  "by_campaign": {
    "Summer Sale": 200,
    "Brand Awareness": 150
  },
  "top_sources": [...],
  "top_campaigns": [...]
}
```

## Integration with Main Analyzer

To integrate AppsFlyer data into the weekly reports:

1. Import the handler in `amplitude_analyzer.py`
2. Add AppsFlyer section to the weekly analysis
3. Include install metrics in the executive summary

Example integration:
```python
from appsflyer_data_handler import AppsFlyerDataHandler

# In your analysis function
appsflyer = AppsFlyerDataHandler()
install_data = appsflyer.get_week_install_summary(target_week)
```

## Rate Limits
- Partner API limited to 10 calls per day
- Plan API calls carefully to avoid hitting limits
- Consider manual CSV export workflow for comprehensive data

## Troubleshooting

### Common Issues
1. **403 Forbidden**: Check API token is valid
2. **No data returned**: Verify app_id and date range
3. **Empty results**: Ensure the app has installs in the date range

### Debug Mode
Set environment variable for verbose logging:
```
export DEBUG=true
```

## Recommended Workflow

Given our API limitations:

### Option 1: API + Manual Process (Hybrid)
1. Use Partner API for available sources (Organic, Facebook, etc.)
2. Manually export CSV from UI for complete data including Google Ads
3. Process CSV files to supplement API data

### Option 2: Fully Manual Process
1. Schedule weekly CSV exports from AppsFlyer UI
2. Process CSV files programmatically
3. Integrate processed data into reports

## CSV Processing

When processing manually exported CSVs:
- Media source column: "Media Source (pid)"
- Key sources: googleadwords_int, Facebook Ads, Organic, etc.
- Files can be processed using `appsflyer_csv_merger.py` or similar tools

## Next Steps
1. Decide between hybrid or fully manual workflow
2. Set up CSV export schedule if using manual process
3. Test CSV processing scripts with exported data
4. Update main analyzer to handle both API and CSV data sources
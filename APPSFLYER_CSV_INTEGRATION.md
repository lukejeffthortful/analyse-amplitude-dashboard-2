# AppsFlyer CSV Integration Guide

## Overview
Due to API limitations (no access to master_report, missing Google Ads data), we now use manually exported CSV files from AppsFlyer that include all media sources.

## Setup Instructions

### 1. Export Data from AppsFlyer
1. Log into AppsFlyer Dashboard
2. Navigate to your reports section
3. Export data with these settings:
   - Include all media sources (especially Google Ads)
   - Export as CSV format
   - Select your desired date range

### 2. Save CSV Files
Save exported files in the `appsflyer-report-exports/` directory with this naming format:
```
YYYY-MM-DD__YYYY-MM-DD.csv
```

Example:
```
appsflyer-report-exports/2025-01-01__2025-01-31.csv
```

### 3. CSV Format Expected
The handler expects these columns:
- `media-source` - The traffic source (e.g., googleadwords_int, Facebook Ads, organic)
- `campaign` - Campaign name
- `installs appsflyer` - Number of installs

## Usage Example

```python
from appsflyer_csv_handler import AppsFlyerCSVHandler

# Initialize handler
handler = AppsFlyerCSVHandler()

# Get data for a specific week
data = handler.get_week_install_summary(target_week=3, year=2025)

# Or get data for a date range
from datetime import datetime
start = datetime(2025, 1, 13)
end = datetime(2025, 1, 19)
data = handler.get_installs_by_source_and_campaign(start, end)

# Format and display
if data:
    print(handler.format_install_summary(data))
```

## Integration with Main Analyzer

To integrate into `amplitude_analyzer.py`:

```python
# Import the CSV handler instead of API handler
from appsflyer_csv_handler import AppsFlyerCSVHandler

# In your analysis function
appsflyer = AppsFlyerCSVHandler()
install_data = appsflyer.get_week_install_summary(target_week)

if install_data:
    # Process the data
    total_installs = install_data['total_installs']
    google_ads_installs = install_data['by_media_source'].get('googleadwords_int', 0)
    # ... rest of your analysis
else:
    # Handle missing data
    print("⚠️  AppsFlyer data not available - please export CSV for this date range")
```

## Benefits of CSV Approach

✅ **Includes Google Ads data** - Unlike the API, CSV exports include googleadwords_int
✅ **No API limits** - No daily call restrictions
✅ **Historical data** - Can analyze any date range you have exported
✅ **Reliable** - Not dependent on API availability or permissions

## Limitations

⚠️ **Manual process** - Requires periodic manual exports
⚠️ **Data freshness** - Data is only as current as your last export
⚠️ **Storage** - Need to manage CSV files locally

## Troubleshooting

### Missing Date Range
If you see: "No CSV export found for date range..."
- Export the required date range from AppsFlyer
- Save with correct filename format
- Place in `appsflyer-report-exports/` directory

### Wrong Data Format
If installs aren't being counted:
- Verify CSV has `installs appsflyer` column
- Check that media sources are in `media-source` column
- Ensure CSV is comma-separated (not tab-separated)

## Maintenance

1. **Weekly exports**: Export data weekly to keep reports current
2. **Archive old files**: Move old CSV files to an archive folder periodically
3. **Naming consistency**: Always use YYYY-MM-DD__YYYY-MM-DD.csv format
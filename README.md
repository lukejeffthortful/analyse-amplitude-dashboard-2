# Amplitude Dashboard Analyzer

## Overview
This project fetches data from Amplitude dashboard charts and generates weekly executive summaries for business reporting.

## Amplitude API Integration Guide

### API Endpoint Format
```
GET https://amplitude.com/api/3/chart/{chart_id}/csv
```

### Authentication
- Uses HTTP Basic Authentication
- Username: API Key
- Password: Secret Key
- Set in `.env` file:
  ```
  AMPLITUDE_API_KEY=your_api_key_here
  AMPLITUDE_SECRET_KEY=your_secret_key_here
  ```

### Response Format
The API returns JSON with a `data` field containing CSV content:
```json
{
  "data": "\"Chart Title\"\r\n\r\n\"Metric Name\"\r\n\r\n\"Segment\",\"Date1\",\"Date2\"...\r\n\"Platform1\",\"Value1\",\"Value2\"...\r\n"
}
```

### CSV Structure Example
```
"	Sessions (Current Year)"

"	Total Sessions"

"	Segment","	2025-05-26T00:00:00","	2025-06-02T00:00:00","	2025-06-09T00:00:00"
"	Apps Only","74285","113276","170737"
"	Web Only","287345","469086","723636"
"	App + Web","361630","582362","894373"
```

### Key Findings:
1. **Chart IDs**: Found in dashboard URLs (e.g., `y0ivh3am` from the dashboard URL)
2. **Data Segmentation**: Charts include platform breakdowns (Apps Only, Web Only, App + Web)
3. **Date Format**: Weekly data with ISO date format (`2025-05-26T00:00:00`)
4. **Multi-line Headers**: CSV starts with chart title and metric name on separate lines
5. **Tab-separated Values**: Fields are separated by tabs, enclosed in quotes

### Chart Configuration
From `plan.md`, the following charts are configured:
- Sessions (Current Year): `y0ivh3am`
- Sessions (Previous Year): `5vbaz782`
- Sessions per user (Current Year): `pc9c0crz`
- Sessions per user (Previous Year): `3d400y6n`
- Session Conversion % (Current Year): `42c5gcv4`
- Session Conversion % (Previous Year): `3t0wgn4i`
- User Conversion %: `4j2gp4ph` (single chart with built-in comparison)

## Usage

### Basic Usage
```bash
python3 amplitude_analyzer.py
```

### Output
- Console: Executive summary for the previous week
- File: `weekly_analysis.json` with detailed metrics

### Expected Executive Summary Format
```
Week 29 Analysis (2025-07-14 to 2025-07-20):

Sessions down 11% YoY, but session conversion 2 ppts better YoY. Web session conversion was up 3 ppts YoY & user conversion up 5ppt YoY (to be expected with lower sessions), while App was down by -1ppt on session CVR and -1ppt on user CVR.
```

## Data Processing Notes

### Platform Segmentation
The API returns data broken down by:
- **Apps Only**: Mobile app sessions
- **Web Only**: Web platform sessions  
- **App + Web**: Combined total across platforms

### Week Calculation
- Uses ISO week numbers (Week 1-53)
- Week runs Monday to Sunday
- Automatically calculates previous week if no target specified

### YoY Comparisons
- Compares same ISO week across years
- Calculates percentage changes for sessions
- Calculates percentage point changes for conversion rates
- Handles division by zero errors

## Development Notes

### Dependencies
- `requests`: HTTP API calls
- `python-dotenv`: Environment variable management
- `json`: Data serialization
- `datetime`: Date/time calculations

### Error Handling
- API connection failures
- Missing/malformed CSV data
- Division by zero in calculations
- Invalid date ranges

### Platform Segmentation ✅ IMPLEMENTED
The analyzer now provides complete breakdowns for all three platform segments:

**Supported Segments:**
- **Apps Only**: Mobile app sessions and metrics
- **Web Only**: Web platform sessions and metrics  
- **App + Web Combined**: Total across all platforms

**Enhanced Sample Output:**
```
Week 29 Analysis (2025-07-14 to 2025-07-20):

Sessions down 92.2% YoY, but session conversion 3.5 ppts up YoY. Web session conversion up 2.1 ppts YoY & App session conversion down 1.5 ppts YoY.

Platform Breakdowns:
Web: sessions down 92.7% YoY
Apps: sessions down 90.1% YoY

Sessions per user down 16.3% YoY (1.23 vs 1.46) (Web down 16.8% YoY)

User conversion platform breakdown:
Combined: 0.205, Web: 0.201, App: 0.218
```

**Complete Platform Data Structure:**
```json
{
  "metrics": {
    "sessions": {
      "apps": {"current": 4074.0, "previous": 41014.0, "yoy_change": -90.1},
      "web": {"current": 12808.0, "previous": 174835.0, "yoy_change": -92.7},
      "combined": {"current": 16882.0, "previous": 215849.0, "yoy_change": -92.2}
    },
    "sessions_per_user": {
      "apps": {"current": 0, "previous": 0, "yoy_change": null},
      "web": {"current": 1.16, "previous": 1.39, "yoy_change": -16.8},
      "combined": {"current": 1.23, "previous": 1.46, "yoy_change": -16.3}
    },
    "session_conversion": {
      "apps": {"current": 0.218, "previous": 0.203, "yoy_change": 1.5},
      "web": {"current": 0.201, "previous": 0.180, "yoy_change": 2.1},
      "combined": {"current": 0.206, "previous": 0.199, "yoy_change": 3.5}
    },
    "user_conversion": {
      "apps": 0.218,
      "web": 0.201,
      "combined": 0.206
    }
  }
}
```

### API Rate Limiting
- Added 2-second delays between API calls to avoid 429 rate limit errors
- Amplitude API has cost-based rate limiting (up to 108,000 cost per hour)
- Charts have different costs (1120-3360 per request)

### Future Enhancements
1. **Trend Analysis**: Multi-week trend identification
2. **Automated Reporting**: Schedule regular report generation  
3. **Error Recovery**: Retry logic for rate-limited requests
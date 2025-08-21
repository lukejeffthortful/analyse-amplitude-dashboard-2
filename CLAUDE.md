# Claude Memory - Amplitude Dashboard Analyzer Project

## Critical: Safe Development Approach

**ALWAYS follow the safe development workflow documented in SAFE_DEVELOPMENT_GUIDE.md**

### Key Rules:
1. **NEVER modify the `main` branch directly** - it has working production code
2. **ALWAYS use `development-iteration` branch** for any changes
3. **NEVER push to remote** without explicit user permission
4. **ALWAYS test locally first** using `test_local.py`

### Quick Reference:
```bash
# Check current branch (should be development-iteration)
git branch --show-current

# Test changes locally without side effects
python test_local.py

# Create backups before major changes
cp amplitude_analyzer.py backups/amplitude_analyzer_$(date +%Y%m%d_%H%M%S).py
```

### Production Environment:
- GitHub Actions runs every Monday at 7:00 AM on `main` branch
- Sends reports to Slack webhook
- DO NOT break this working automation

### Testing:
- Use `.env.development` for local testing
- Set `SLACK_WEBHOOK_URL=''` to prevent notifications
- Test with old weeks to avoid interfering with current data

**Remember: The remote `main` branch is sacred - it contains proven, working code that runs in production.**

## Project Context

This is an analytics tool that:
- Fetches weekly data from Amplitude dashboard charts
- Calculates Year-over-Year (YoY) comparisons
- Generates executive summaries for business reporting
- Optionally integrates GA4 for comparative analysis
- Runs automatically via GitHub Actions

See PROJECT_NOTES.md for detailed technical information.

## AppsFlyer Integration Notes

### API Access Limitations
- **IMPORTANT**: Our account does NOT have access to the master_report API endpoint
- We must use the aggregated partners report endpoint: `/api/agg-data/export/app/{app_id}/partners_report/v5`
- This endpoint has a limit of 10 API calls per day

### Current Issues with AppsFlyer Data
- The aggregated partners report is NOT returning Google Ads data (googleadwords_int)
- We're successfully getting data for: Organic, website-thortful, Facebook Ads, QR_code, transactional_postmark
- The expected Google Ads data shown in example files is not appearing in actual API responses

### Working Configuration
- Endpoint: `https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/partners_report/v5`
- Authentication: Bearer token in header
- CSV Column for media source: "Media Source (pid)" (not "Media Source")
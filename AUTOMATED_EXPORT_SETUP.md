# AppsFlyer Automated CSV Export Setup

This guide explains how to automate CSV exports from AppsFlyer to avoid manual processes and human error.

## Overview

Since the Partner API doesn't provide Google Ads data, we need to automate the UI export process. This solution uses browser automation to:
1. Log into AppsFlyer
2. Navigate to the Partners report
3. Set the date range
4. Export the CSV file
5. Save it with a meaningful filename

## Option 1: Playwright (Recommended)

### Installation
```bash
pip install playwright
playwright install chromium
```

### Setup
1. Add credentials to `.env`:
```
APPSFLYER_USERNAME=your_email@company.com
APPSFLYER_PASSWORD=your_password
```

2. Run the automated export:
```bash
python appsflyer_automated_export.py
```

### Features
- Headless operation (runs in background)
- Better performance than Selenium
- Built-in wait strategies
- Screenshot on error for debugging

## Option 2: Selenium

### Installation
```bash
pip install selenium
# Also need ChromeDriver: https://chromedriver.chromium.org/
```

### Setup
Same as Playwright - add credentials to `.env` and run:
```bash
python appsflyer_selenium_export.py
```

## GitHub Actions Integration

Add this to your weekly workflow to automate exports:

```yaml
name: Weekly Report with Automated Export

on:
  schedule:
    - cron: '0 7 * * 1'  # Every Monday at 7 AM
  workflow_dispatch:

jobs:
  export-and-analyze:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install playwright
        playwright install chromium
        playwright install-deps
    
    - name: Export AppsFlyer CSV
      env:
        APPSFLYER_USERNAME: ${{ secrets.APPSFLYER_USERNAME }}
        APPSFLYER_PASSWORD: ${{ secrets.APPSFLYER_PASSWORD }}
      run: |
        python appsflyer_automated_export.py
    
    - name: Process CSV and Run Analysis
      env:
        AMPLITUDE_API_KEY: ${{ secrets.AMPLITUDE_API_KEY }}
        AMPLITUDE_SECRET_KEY: ${{ secrets.AMPLITUDE_SECRET_KEY }}
        # ... other secrets
      run: |
        python amplitude_analyzer.py
```

## Security Considerations

1. **Never commit credentials** - Always use environment variables
2. **Use GitHub Secrets** for production workflows
3. **Consider using a service account** specifically for automation
4. **Enable 2FA bypass** for automation accounts (if supported)
5. **Monitor for UI changes** - AppsFlyer may update their interface

## Integrating with Main Analyzer

Update `amplitude_analyzer.py` to use the exported CSV:

```python
# Check for recent CSV export
csv_files = sorted(Path("./appsflyer_exports").glob("appsflyer_partners_*.csv"), 
                  key=os.path.getmtime, reverse=True)

if csv_files:
    latest_csv = csv_files[0]
    # Process CSV to get Google Ads data
    google_ads_data = process_appsflyer_csv(latest_csv)
    
    # Merge with API data
    api_data = appsflyer_handler.get_data()
    complete_data = merge_data_sources(api_data, google_ads_data)
```

## Troubleshooting

### Common Issues

1. **Login fails**: Check credentials and 2FA settings
2. **Elements not found**: AppsFlyer may have updated their UI
3. **Download timeout**: Increase wait time for large reports
4. **Headless mode issues**: Try running with `headless=False` for debugging

### Debugging Tips

1. Take screenshots at each step:
```python
await page.screenshot(path="step1_login.png")
```

2. Use verbose logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

3. Run in non-headless mode to watch the automation:
```python
browser = await p.chromium.launch(headless=False)
```

## Maintenance

- Test the automation weekly to ensure it's working
- Monitor for AppsFlyer UI changes
- Update selectors if elements change
- Keep browser drivers updated

## Alternative: RPA Tools

For teams already using RPA (Robotic Process Automation) tools:
- **UiPath**: Enterprise RPA solution
- **Power Automate**: Microsoft's automation platform
- **Zapier/Make**: No-code automation platforms (if they support AppsFlyer)

These tools can provide more robust error handling and scheduling but require additional licensing.
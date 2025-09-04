#!/usr/bin/env python3
"""Test the AppsFlyer CSV handler with manual exports"""

from appsflyer_csv_handler import AppsFlyerCSVHandler
from datetime import datetime
import json

# Initialize handler
handler = AppsFlyerCSVHandler()

# Test 1: Check available date ranges
print("📊 Checking available CSV exports...")
available_ranges = handler.get_available_date_ranges()
if available_ranges:
    print(f"\nFound {len(available_ranges)} CSV export(s):")
    for start, end in available_ranges:
        print(f"  • {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
else:
    print("No CSV exports found")

# Test 2: Try to get data for a specific week (Week 3 of 2025)
print("\n" + "="*60)
print("Testing Week 3 of 2025 (Jan 13-19)")
start_date = datetime(2025, 1, 13)
end_date = datetime(2025, 1, 19)

result = handler.get_installs_by_source_and_campaign(start_date, end_date)

if result:
    print("\n" + handler.format_install_summary(result))
    
    # Save detailed results
    with open('test_csv_handler_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\n📁 Detailed results saved to: test_csv_handler_results.json")
    
    # Verify Google Ads data
    print("\n🔍 Google Ads Verification:")
    google_sources = {
        'googleadwords_int': 'Google Ads',
        'google_organic_seo': 'Google Organic SEO'
    }
    
    for key, name in google_sources.items():
        if key in result['by_media_source']:
            installs = result['by_media_source'][key]
            print(f"✅ {name}: {installs:,} installs")
        else:
            print(f"❌ {name}: Not found")

# Test 3: Try a date range that might not exist
print("\n" + "="*60)
print("Testing a future date range (should show helpful message)")
future_start = datetime(2026, 1, 1)
future_end = datetime(2026, 1, 7)
handler.get_installs_by_source_and_campaign(future_start, future_end)
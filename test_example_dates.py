#!/usr/bin/env python3
"""Test AppsFlyer API with example dates from the CSV file"""

from appsflyer_final_handler import AppsFlyerHandler
from datetime import datetime
import json

# Use exact dates from the example file
start_date = datetime(2025, 7, 14)
end_date = datetime(2025, 7, 20)

print(f"Testing AppsFlyer API with example dates")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print()

# Create handler and fetch data
handler = AppsFlyerHandler()
result = handler.get_installs_by_source_and_campaign(start_date, end_date)

if result:
    print("\n" + handler.format_install_summary(result))
    
    # Check specifically for Google Ads data
    print("\n🔍 Looking for Google Ads data:")
    google_sources = ['googleadwords_int', 'google_organic_seo', 'Google Ads']
    found_any = False
    
    for source in google_sources:
        if source in result['by_media_source']:
            print(f"✅ Found {source}: {result['by_media_source'][source]} installs")
            found_any = True
    
    if not found_any:
        print("❌ No Google Ads data found in response")
        print("\nAll media sources found:")
        for source in sorted(result['by_media_source'].keys()):
            print(f"  • {source}")
    
    # Save detailed results
    with open('example_dates_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\n📁 Detailed results saved to: example_dates_results.json")
else:
    print("❌ Failed to fetch data")
#!/usr/bin/env python3
"""Test AppsFlyer API with last week's data"""

from appsflyer_final_handler import AppsFlyerHandler
from datetime import datetime, timedelta
import json

# Calculate last week's dates
today = datetime.now()
last_monday = today - timedelta(days=today.weekday() + 7)
last_sunday = last_monday + timedelta(days=6)

print(f"Testing AppsFlyer API with last week's data")
print(f"Date range: {last_monday.strftime('%Y-%m-%d')} to {last_sunday.strftime('%Y-%m-%d')}")
print()

# Create handler and fetch data
handler = AppsFlyerHandler()
result = handler.get_installs_by_source_and_campaign(last_monday, last_sunday)

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
    with open('last_week_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\n📁 Detailed results saved to: last_week_results.json")
else:
    print("❌ Failed to fetch data")
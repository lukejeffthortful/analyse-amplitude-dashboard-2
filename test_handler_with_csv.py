#!/usr/bin/env python3
"""Test the AppsFlyer handler with the existing CSV data"""

from appsflyer_final_handler import AppsFlyerHandler
from datetime import datetime

# Read the existing CSV data
with open('appsflyer_partners_aggregated.csv', 'r') as f:
    csv_text = f.read()

# Create handler and test the CSV processing method
handler = AppsFlyerHandler()

# Process the CSV data (simulate API response)
print("Testing AppsFlyer handler with actual CSV data...\n")
start_date = datetime(2025, 1, 13)
end_date = datetime(2025, 1, 19)

result = handler._process_aggregated_csv(csv_text, start_date, end_date)

if result:
    print("\n" + handler.format_install_summary(result))
    
    # Verify we're getting correct media sources
    print("\n🔍 Verification:")
    if 'Facebook Ads' in result['by_media_source']:
        print("✅ Facebook Ads found:", result['by_media_source']['Facebook Ads'], "installs")
    if 'Organic' in result['by_media_source']:
        print("✅ Organic found:", result['by_media_source']['Organic'], "installs")
    if 'website-thortful' in result['by_media_source']:
        print("✅ website-thortful found:", result['by_media_source']['website-thortful'], "installs")
else:
    print("❌ Failed to process data")
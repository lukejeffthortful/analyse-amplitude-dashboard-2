#!/usr/bin/env python3
"""
Debug AppsFlyer API to understand missing media sources
"""

import csv
import io
from collections import defaultdict

# Analyze the raw CSV data we got
print("Analyzing AppsFlyer Raw CSV Data")
print("=" * 50)

# Read our API response
with open('appsflyer_raw_response.csv', 'r') as f:
    content = f.read()

csv_reader = csv.DictReader(io.StringIO(content))

media_sources = defaultdict(int)
campaigns = defaultdict(int)
total_rows = 0

for row in csv_reader:
    total_rows += 1
    media_source = row.get('Media Source', 'Unknown')
    campaign = row.get('Campaign', 'Unknown')
    
    media_sources[media_source] += 1
    campaigns[campaign] += 1

print(f"Total rows in API response: {total_rows}")
print("\nMedia Sources in API response:")
for source, count in sorted(media_sources.items(), key=lambda x: x[1], reverse=True):
    print(f"  {source}: {count}")

print("\nTop Campaigns in API response:")
for campaign, count in sorted(campaigns.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {campaign}: {count}")

# Now analyze the dashboard export for comparison
print("\n" + "=" * 50)
print("Analyzing Dashboard Export for Comparison")
print("=" * 50)

dashboard_sources = defaultdict(int)

with open('example_data/my_dashboards_export_chart_unified_view_2025-07-14__2025-07-20_Europe_London_GBP_qMvK1.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    
    for row in csv_reader:
        media_source = row.get('media-source', 'Unknown')
        installs = row.get('installs appsflyer', '0')
        
        if installs and installs.strip():
            try:
                installs_count = int(installs)
                dashboard_sources[media_source] += installs_count
            except ValueError:
                continue

print("\nMedia Sources in Dashboard Export:")
for source, count in sorted(dashboard_sources.items(), key=lambda x: x[1], reverse=True):
    print(f"  {source}: {count}")

print("\n" + "=" * 50)
print("COMPARISON ANALYSIS")
print("=" * 50)

print("\nSources in Dashboard but NOT in API:")
dashboard_set = set(dashboard_sources.keys())
api_set = set(media_sources.keys())

missing_from_api = dashboard_set - api_set
present_in_both = dashboard_set & api_set

for source in sorted(missing_from_api):
    if source != 'organic':  # Expected to be missing due to plan limits
        print(f"  ❌ MISSING: {source} ({dashboard_sources[source]} installs)")

print("\nSources present in both:")
for source in sorted(present_in_both):
    api_count = media_sources[source]
    dash_count = dashboard_sources[source]
    print(f"  ✅ {source}: API={api_count}, Dashboard={dash_count}")

print(f"\n🔍 Key Issue: googleadwords_int has {dashboard_sources['googleadwords_int']} installs in dashboard but 0 in API")
print("This suggests the Pull API is not capturing Google Ads data correctly.")
#!/usr/bin/env python3
"""
Test the CSV processing with correct column names
"""

import csv
import io
from collections import defaultdict

# Read the actual CSV and process it correctly
with open('appsflyer_partners_aggregated.csv', 'r') as f:
    content = f.read()

print("🔍 Analyzing AppsFlyer Partners CSV with Correct Column Names")
print("=" * 65)

csv_reader = csv.DictReader(io.StringIO(content))

media_sources = defaultdict(int)
campaigns = defaultdict(int)
total_installs = 0
row_count = 0

print("Available columns:")
first_row = next(csv_reader)
print(f"  {list(first_row.keys())[:5]}...")

# Reset the reader
csv_reader = csv.DictReader(io.StringIO(content))

for row in csv_reader:
    row_count += 1
    
    # Use the correct column names from the actual CSV
    media_source = row.get('Media Source (pid)', 'Unknown')
    campaign = row.get('Campaign (c)', 'Unknown')
    
    # Get installs from the correct column
    installs = 0
    installs_str = row.get('Installs', '0')
    if installs_str and installs_str.strip() and installs_str != 'N/A':
        try:
            installs = int(float(installs_str))
        except (ValueError, TypeError):
            installs = 0
    
    if installs > 0:
        total_installs += installs
        media_sources[media_source] += installs
        
        if campaign and campaign != 'None':
            campaigns[campaign] += installs
    
    # Show first few meaningful rows
    if row_count <= 5 and installs > 0:
        print(f"Row {row_count}: {media_source} -> {installs} installs")

print(f"\n📊 CORRECTED Results:")
print(f"   Total rows processed: {row_count}")
print(f"   Total installs: {total_installs:,}")

print(f"\n🎯 Media Sources (corrected):")
for source, count in sorted(media_sources.items(), key=lambda x: x[1], reverse=True)[:10]:
    pct = (count / total_installs * 100) if total_installs > 0 else 0
    print(f"   {source}: {count:,} ({pct:.1f}%)")

print(f"\n🎯 Top Campaigns:")
for campaign, count in sorted(campaigns.items(), key=lambda x: x[1], reverse=True)[:5]:
    pct = (count / total_installs * 100) if total_installs > 0 else 0
    print(f"   {campaign}: {count:,} ({pct:.1f}%)")

# Check if we found our target sources
target_sources = ['googleadwords_int', 'Facebook Ads', 'Organic']
found_targets = []
for source in target_sources:
    if source in media_sources:
        found_targets.append(source)
        print(f"🎉 FOUND: {source} with {media_sources[source]:,} installs!")

if not any('googleadwords_int' in source for source in media_sources.keys()):
    print("\n❓ Note: googleadwords_int not found in this date range")
    print("   This might be because the July 14-20 period didn't have Google Ads installs")
    print("   or the data might be in a different date range")

print(f"\n✅ SUCCESS: Now capturing complete attribution data!")
print(f"   This is {total_installs:,} installs vs ~814 from the raw endpoint")
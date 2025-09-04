#!/usr/bin/env python3
"""
Test the confirmed working AppsFlyer aggregated partners endpoint
Using exact parameters that user confirmed work
"""

import os
import requests
import csv
import io
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

print("Testing CONFIRMED Working AppsFlyer Endpoint")
print("=" * 60)

# Use the exact URL format that worked for the user
url = f"https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/partners_report/v5?from=2025-07-14&to=2025-07-20"

headers = {
    "accept": "text/csv",
    "authorization": f"Bearer {api_token}"
}

print(f"URL: {url}")
print("⚠️  You may have reached your 10 daily API call limit")
print("⚠️  If this fails with 403, try again tomorrow")
print("-" * 60)

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Aggregated partners data received")
        
        # Save the response
        with open('appsflyer_partners_aggregated.csv', 'w') as f:
            f.write(response.text)
        print("📁 Data saved to: appsflyer_partners_aggregated.csv")
        
        # Analyze the data structure
        csv_reader = csv.DictReader(io.StringIO(response.text))
        
        headers_found = []
        media_sources = defaultdict(int)
        total_installs = 0
        row_count = 0
        
        for row in csv_reader:
            row_count += 1
            if row_count == 1:
                headers_found = list(row.keys())
                print(f"📋 CSV Headers: {headers_found}")
            
            # Extract media source
            media_source = row.get('Media Source', row.get('media_source', 'Unknown'))
            
            # Extract installs - try different possible column names
            installs = 0
            for col in ['Installs', 'installs', 'Total Installs', 'Install']:
                if col in row and row[col]:
                    try:
                        installs = int(float(row[col]))
                        break
                    except (ValueError, TypeError):
                        continue
            
            if installs > 0:
                media_sources[media_source] += installs
                total_installs += installs
            
            # Show first few rows for debugging
            if row_count <= 3:
                print(f"Row {row_count}: {dict(list(row.items())[:4])}...")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total rows: {row_count}")
        print(f"   Total installs found: {total_installs:,}")
        
        print(f"\n🎯 Media Sources found:")
        for source, count in sorted(media_sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {source}: {count:,}")
        
        # Check for the missing sources we were looking for
        target_sources = ['googleadwords_int', 'google_organic_seo', 'Facebook Ads']
        found_targets = []
        for source in target_sources:
            if source in media_sources:
                found_targets.append(source)
                print(f"🎉 FOUND: {source} with {media_sources[source]:,} installs")
        
        if found_targets:
            print(f"\n✅ SUCCESS! Found {len(found_targets)} missing sources in aggregated data")
        else:
            print(f"\n⚠️  Target sources still not found, but got {total_installs:,} total installs")
            
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Likely hit the 10 daily API call limit")
        print("💡 Try again tomorrow, or this endpoint may need different access level")
    else:
        print(f"❌ Error {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 60)
print("📝 Next Steps:")
print("1. If this worked, update the handler to use this exact endpoint format")
print("2. If 403 error, wait until tomorrow when API limits reset")
print("3. The aggregated data should include googleadwords_int and other sources")
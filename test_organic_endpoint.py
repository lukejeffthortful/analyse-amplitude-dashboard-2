#!/usr/bin/env python3
"""
Test AppsFlyer Organic Installs endpoint to see if it captures missing sources
"""

import os
import requests
import csv
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

print("Testing AppsFlyer Organic Installs Endpoint")
print("=" * 60)

# Test the organic endpoint
url = f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/organic_installs_report/v5"

# Use same date range as our previous test
params = {
    'from': '2025-07-14',
    'to': '2025-07-20'
}

headers = {
    'Authorization': f'Bearer {api_token}',
    'Accept': 'text/csv'
}

print(f"URL: {url}")
print(f"Date Range: {params['from']} to {params['to']}")
print("⚠️  This will use 1 more of your daily API calls")
print("-" * 60)

try:
    response = requests.get(url, params=params, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Organic endpoint accessible!")
        
        # Save raw response
        with open('appsflyer_organic_response.csv', 'w') as f:
            f.write(response.text)
        print("📁 Raw organic response saved to: appsflyer_organic_response.csv")
        
        # Analyze the organic data
        csv_reader = csv.DictReader(io.StringIO(response.text))
        
        organic_sources = defaultdict(int)
        total_organic_rows = 0
        
        print("\nAnalyzing organic installs data...")
        for row in csv_reader:
            total_organic_rows += 1
            media_source = row.get('Media Source', 'Unknown')
            organic_sources[media_source] += 1
            
            # Print first few rows to understand structure
            if total_organic_rows <= 3:
                print(f"Row {total_organic_rows} sample: Media Source='{media_source}', columns={list(row.keys())[:5]}...")
        
        print(f"\nTotal organic install rows: {total_organic_rows}")
        print("\nOrganic Media Sources found:")
        for source, count in sorted(organic_sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {source}: {count}")
        
        # Check if we found the missing sources
        missing_sources = ['googleadwords_int', 'google_organic_seo', 'Facebook Ads']
        found_missing = []
        
        for source in missing_sources:
            if source in organic_sources:
                found_missing.append(source)
                print(f"🎯 FOUND: {source} in organic endpoint ({organic_sources[source]} installs)")
        
        if not found_missing:
            print("❌ Missing sources (googleadwords_int, google_organic_seo, Facebook Ads) not found in organic endpoint either")
        
        # Compare organic vs non-organic totals
        print(f"\n📊 Data Summary:")
        print(f"   Non-organic installs (previous test): 814")
        print(f"   Organic installs (this test): {total_organic_rows}")
        print(f"   Dashboard total: ~4,000+ installs")
        print(f"   Combined API total: {814 + total_organic_rows}")
        
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - Your plan may not include organic data access")
        print("Response:", response.text[:200])
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Access denied to organic endpoint")
        print("Response:", response.text[:200])
    else:
        print(f"❌ Error {response.status_code}")
        print("Response:", response.text[:500])
        
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 60)
print("ANALYSIS:")
print("If the organic endpoint returns googleadwords_int data, it suggests")
print("that AppsFlyer classifies Google Ads as 'organic' rather than 'non-organic'")
print("which would explain why it's missing from the installs_report endpoint.")
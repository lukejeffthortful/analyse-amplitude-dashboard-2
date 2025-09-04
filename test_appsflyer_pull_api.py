#!/usr/bin/env python3
"""
Test AppsFlyer Pull API (Aggregate Performance Report)
"""

import os
import requests
from dotenv import load_dotenv
import csv
import io

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

print("Testing AppsFlyer Pull API - Aggregate Performance Report")
print("=" * 60)

# Pull API endpoint for aggregate performance report
url = f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/aggregate_report/v5"

# Parameters for the request
params = {
    'from': '2024-08-01',
    'to': '2024-08-07',
    'groupings': 'install_time:date,media_source,campaign',
    'kpis': 'installs',
    'format': 'csv'
}

headers = {
    'Authorization': f'Bearer {api_token}',
    'Accept': 'text/csv'
}

print(f"App ID: {app_id}")
print(f"Date Range: {params['from']} to {params['to']}")
print(f"URL: {url}")
print("-" * 60)

try:
    response = requests.get(url, params=params, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success! Data received")
        
        # Parse CSV response
        csv_data = csv.DictReader(io.StringIO(response.text))
        
        total_installs = 0
        media_sources = {}
        campaigns = {}
        
        for row in csv_data:
            installs = int(float(row.get('Installs', 0)))
            media_source = row.get('Media Source', 'Unknown')
            campaign = row.get('Campaign', 'Unknown')
            
            total_installs += installs
            
            if media_source not in media_sources:
                media_sources[media_source] = 0
            media_sources[media_source] += installs
            
            if campaign not in campaigns:
                campaigns[campaign] = 0
            campaigns[campaign] += installs
        
        print(f"\nTotal Installs: {total_installs:,}")
        
        print("\nTop Media Sources:")
        for source, count in sorted(media_sources.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {source}: {count:,}")
        
        print("\nTop Campaigns:")
        for campaign, count in sorted(campaigns.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {campaign}: {count:,}")
        
        # Save raw response for inspection
        with open('test_appsflyer_raw_response.csv', 'w') as f:
            f.write(response.text)
        print("\n📁 Raw response saved to: test_appsflyer_raw_response.csv")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}...")
        
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {str(e)}")

# Also try the partners API endpoint
print("\n" + "=" * 60)
print("Testing Partners API endpoint...")

partners_url = "https://hq1.appsflyer.com/api/raw-data/export/app/{app-id}/partners_report/v5"
partners_url = partners_url.replace("{app-id}", app_id)

try:
    response = requests.get(partners_url, params=params, headers=headers, timeout=30)
    print(f"Partners API Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {type(e).__name__}")

print("\n\nAPI Token format check:")
print(f"Token starts with: {api_token[:10]}")
print(f"Token length: {len(api_token)}")
print("Token appears to be a JWT token" if api_token.startswith('eyJ') else "Token format unknown")
#!/usr/bin/env python3
"""Test AppsFlyer daily_report/v5 endpoint"""

import os
import requests
import csv
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

# Test with the example dates
start_date = "2025-01-13"
end_date = "2025-01-19"

# Try the daily report endpoint
url = f"https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/daily_report/v5?from={start_date}&to={end_date}"

headers = {
    'accept': 'text/csv',
    'authorization': f'Bearer {api_token}'
}

print(f"Testing AppsFlyer daily_report/v5 endpoint")
print(f"Date range: {start_date} to {end_date}")
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        # Save raw response
        with open('appsflyer_daily_report_response.csv', 'w') as f:
            f.write(response.text)
        print("✅ Saved raw response to: appsflyer_daily_report_response.csv")
        
        # Parse and analyze the CSV
        csv_reader = csv.DictReader(io.StringIO(response.text))
        
        media_sources = set()
        total_installs = 0
        by_source = {}
        
        print("\nAnalyzing response...")
        for row in csv_reader:
            # Try different possible column names
            media_source = None
            for col in ['Media Source (pid)', 'Media Source', 'media_source', 'Partner']:
                if col in row:
                    media_source = row[col]
                    break
            
            if media_source:
                media_sources.add(media_source)
                
                # Get install count
                installs = 0
                for col in ['Installs', 'installs', 'Total Installs', 'Install', 'Conversions']:
                    if col in row and row[col]:
                        try:
                            installs = int(float(row[col]))
                            break
                        except:
                            continue
                
                if installs > 0:
                    total_installs += installs
                    if media_source not in by_source:
                        by_source[media_source] = 0
                    by_source[media_source] += installs
        
        print(f"\nFound {len(media_sources)} unique media sources")
        print(f"Total installs: {total_installs:,}")
        
        print("\nTop Media Sources:")
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {source}: {count:,} installs")
        
        # Check for Google Ads
        print("\n🔍 Checking for Google Ads data:")
        google_sources = ['googleadwords_int', 'google_organic_seo', 'Google Ads', 'google']
        found_google = False
        for source in media_sources:
            if any(gs.lower() in source.lower() for gs in google_sources):
                print(f"✅ Found Google-related source: {source}")
                found_google = True
        
        if not found_google:
            print("❌ No Google Ads data found")
            
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Check API access or daily limit")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}...")

except Exception as e:
    print(f"❌ Error: {e}")
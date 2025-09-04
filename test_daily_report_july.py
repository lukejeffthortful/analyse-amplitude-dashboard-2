#!/usr/bin/env python3
"""Test AppsFlyer daily_report/v5 endpoint with July dates"""

import os
import requests
import csv
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

# Test with the exact dates from the example file
start_date = "2025-07-14"
end_date = "2025-07-20"

# Try the daily report endpoint
url = f"https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/daily_report/v5?from={start_date}&to={end_date}"

headers = {
    'accept': 'text/csv',
    'authorization': f'Bearer {api_token}'
}

print(f"Testing AppsFlyer daily_report/v5 endpoint with July dates")
print(f"Date range: {start_date} to {end_date}")
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        # Save raw response
        with open('appsflyer_daily_report_july.csv', 'w') as f:
            f.write(response.text)
        print("✅ Saved raw response to: appsflyer_daily_report_july.csv")
        
        # Parse and analyze the CSV
        csv_reader = csv.DictReader(io.StringIO(response.text))
        
        media_sources = set()
        total_installs = 0
        by_source = {}
        google_found = False
        
        print("\nAnalyzing response...")
        for row in csv_reader:
            media_source = row.get('Media Source (pid)', 'Unknown')
            
            if media_source:
                media_sources.add(media_source)
                
                # Check for Google
                if 'google' in media_source.lower():
                    google_found = True
                    print(f"🎯 Found Google source: {media_source}")
                
                # Get install count
                installs = 0
                if 'Installs' in row and row['Installs']:
                    try:
                        installs = int(float(row['Installs']))
                    except:
                        pass
                
                if installs > 0:
                    total_installs += installs
                    if media_source not in by_source:
                        by_source[media_source] = 0
                    by_source[media_source] += installs
        
        print(f"\nTotal installs: {total_installs:,}")
        
        print("\nTop 10 Media Sources:")
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {source}: {count:,} installs")
        
        if not google_found:
            print("\n❌ Still no Google Ads data found even with July dates")
            
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
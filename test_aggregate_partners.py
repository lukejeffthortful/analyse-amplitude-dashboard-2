#!/usr/bin/env python3
"""
Test AppsFlyer aggregate partners report (not raw data)
This should be available with Pull API access
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

print("Testing AppsFlyer Aggregate Partners Report")
print("=" * 60)

# Try different aggregate endpoints that should be available with Pull API
endpoints_to_test = [
    ("Partners Report v5", f"https://hq1.appsflyer.com/export/{app_id}/partners_report/v5"),
    ("Partners by Date v5", f"https://hq1.appsflyer.com/export/{app_id}/partners_by_date_report/v5"),
    ("Daily Report v5", f"https://hq1.appsflyer.com/export/{app_id}/daily_report/v5"),
    ("Geo Report v5", f"https://hq1.appsflyer.com/export/{app_id}/geo_by_date_report/v5"),
]

# Test parameters
params = {
    'api_token': api_token,  # Use api_token parameter instead of Bearer for these endpoints
    'from': '2025-07-14',
    'to': '2025-07-20',
    'timezone': 'UTC'
}

headers = {
    'Accept': 'text/csv'
}

for name, url in endpoints_to_test:
    print(f"\n📊 Testing {name}")
    print(f"URL: {url}")
    print("-" * 40)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            
            # Save response for analysis
            filename = f"appsflyer_{name.lower().replace(' ', '_')}_response.csv"
            with open(filename, 'w') as f:
                f.write(response.text)
            print(f"📁 Saved to: {filename}")
            
            # Quick analysis
            try:
                csv_reader = csv.DictReader(io.StringIO(response.text))
                headers_found = []
                media_sources = set()
                row_count = 0
                
                for row in csv_reader:
                    row_count += 1
                    if row_count == 1:
                        headers_found = list(row.keys())
                    
                    # Look for media source data
                    for key in row.keys():
                        if 'media' in key.lower() or 'source' in key.lower():
                            media_sources.add(row.get(key, ''))
                
                print(f"   Rows: {row_count}")
                print(f"   Headers: {headers_found[:5]}...")
                if media_sources:
                    sources_list = [s for s in media_sources if s and s != 'Unknown'][:5]
                    print(f"   Media Sources found: {sources_list}...")
                
                # Check for googleadwords_int specifically
                if any('googleadwords_int' in str(row.values()) for row in csv.DictReader(io.StringIO(response.text))):
                    print("🎯 FOUND googleadwords_int in this endpoint!")
                    
            except Exception as e:
                print(f"   Analysis error: {e}")
            
            # Only test the first successful endpoint to save API calls
            print("\n✅ Found working endpoint, stopping here to preserve API calls")
            break
            
        elif response.status_code == 401:
            print("❌ 401 Unauthorized")
        elif response.status_code == 403:
            print("❌ 403 Forbidden")
        elif response.status_code == 400:
            print("❌ 400 Bad Request")
            print(f"   Response: {response.text[:200]}...")
        else:
            print(f"❌ {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {str(e)}")

print(f"\n📊 API Calls used: 1-4 of your 10 daily limit")
print("🎯 Goal: Find aggregate endpoint that includes googleadwords_int data")
#!/usr/bin/env python3
"""
Simple AppsFlyer API connectivity test
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Test different endpoints
endpoints = [
    "https://hq1.appsflyer.com/export/master_report/v4",
    "https://hq.appsflyer.com/export/master_report/v4",
    "https://api2.appsflyer.com/inappevent",
    "https://hq1.appsflyer.com/api/master-agg-data/v4"
]

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

print("Testing AppsFlyer API endpoints...")
print(f"App ID: {app_id}")
print(f"Token: {api_token[:20]}...{api_token[-10:]}")
print("-" * 50)

for endpoint in endpoints:
    print(f"\nTesting: {endpoint}")
    try:
        # Try a simple request
        if "master_report" in endpoint:
            params = {
                'api_token': api_token,
                'app_id': app_id,
                'from': '2024-08-01',
                'to': '2024-08-07',
                'groupings': 'pid',
                'kpis': 'installs'
            }
            response = requests.get(endpoint, params=params, timeout=10)
        else:
            # For other endpoints, just test connectivity
            response = requests.get(endpoint, timeout=10)
        
        print(f"  Status: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text[:200]}...")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {str(e)[:100]}...")

# Also test with curl command format
print("\n\nCURL command for manual testing:")
print(f"curl -X GET 'https://hq1.appsflyer.com/export/master_report/v4?api_token={api_token[:10]}...&app_id={app_id}&from=2024-08-01&to=2024-08-07&groupings=pid&kpis=installs'")
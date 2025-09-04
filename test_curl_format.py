#!/usr/bin/env python3
"""
Test AppsFlyer API using exact curl format from documentation
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

# Using exact format from documentation
url = f"https://hq1.appsflyer.com/api/master-report/export/app/{app_id}"

# Date range - let's use recent dates
params = {
    'from': '2024-08-01',
    'to': '2024-08-18',
    'groupings': 'pid,c',
    'kpis': 'installs',
    'format': 'json'
}

headers = {
    'Authorization': f'Bearer {api_token}'
}

print("Testing AppsFlyer Master Report API")
print("=" * 50)
print(f"URL: {url}")
print(f"Params: {params}")
print(f"App ID: {app_id}")
print("-" * 50)

try:
    response = requests.get(url, params=params, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Data received:")
        print(f"Response type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            
        # Save to file for inspection
        import json
        with open('test_curl_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("\n📁 Response saved to: test_curl_response.json")
        
    else:
        print(f"\n❌ Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}: {str(e)}")

# Also generate the exact curl command for manual testing
print("\n\nEquivalent curl command:")
curl_cmd = f'''curl -G "https://hq1.appsflyer.com/api/master-report/export/app/{app_id}" \\
  -H "Authorization: Bearer {api_token[:20]}..." \\
  --data-urlencode "from=2024-08-01" \\
  --data-urlencode "to=2024-08-18" \\
  --data-urlencode "groupings=pid,c" \\
  --data-urlencode "kpis=installs" \\
  --data-urlencode "format=json"'''
print(curl_cmd)
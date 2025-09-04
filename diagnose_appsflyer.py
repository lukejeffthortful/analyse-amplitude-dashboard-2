#!/usr/bin/env python3
"""
Diagnose AppsFlyer API Access Issues
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('APPSFLYER_API_TOKEN')
app_id = os.getenv('APPSFLYER_APP_ID')

print("AppsFlyer API Diagnostics")
print("=" * 60)

# 1. Check token format
print("\n1. API Token Analysis:")
print(f"   - Token length: {len(api_token)}")
print(f"   - Starts with 'eyJ': {api_token.startswith('eyJ')}")

# Try to decode JWT (without verification)
try:
    # JWT tokens have 3 parts separated by dots
    parts = api_token.split('.')
    print(f"   - JWT parts: {len(parts)}")
    
    if len(parts) == 3:
        # Try to decode header (first part)
        import base64
        header = parts[0]
        # Add padding if needed
        header += '=' * (4 - len(header) % 4)
        decoded_header = base64.b64decode(header)
        print(f"   - JWT header: {decoded_header}")
except Exception as e:
    print(f"   - JWT decode error: {e}")

# 2. App ID format
print(f"\n2. App ID: {app_id}")
print(f"   - iOS format (starts with 'id'): {app_id.startswith('id')}")
print(f"   - Numeric part: {app_id[2:] if app_id.startswith('id') else 'N/A'}")

# 3. Test different API versions and endpoints
print("\n3. Testing API Endpoints:")

test_endpoints = [
    # V5 endpoints
    ("V5 Master Report", f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/aggregate_report/v5"),
    ("V5 Partners Report", f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/partners_report/v5"),
    
    # Master report endpoints
    ("Master Report (with app)", f"https://hq1.appsflyer.com/api/master-report/export/app/{app_id}"),
    ("Master Report (no app)", "https://hq1.appsflyer.com/api/master-report/export"),
    
    # Legacy endpoints
    ("Legacy V4", f"https://hq1.appsflyer.com/export/master_report/v4"),
    ("Legacy V3", f"https://hq1.appsflyer.com/export/{app_id}/partners_report/v3"),
]

for name, url in test_endpoints:
    print(f"\n   Testing {name}:")
    print(f"   URL: {url}")
    
    try:
        # Test with Bearer token
        headers = {'Authorization': f'Bearer {api_token}'}
        params = {
            'from': '2024-08-01',
            'to': '2024-08-07',
            'groupings': 'pid,c',
            'kpis': 'installs'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        print(f"   Bearer Auth: {response.status_code}")
        
        # If 401, try api_token parameter
        if response.status_code == 401:
            params['api_token'] = api_token
            response = requests.get(url, params=params, timeout=5)
            print(f"   Token Param: {response.status_code}")
            
        if response.status_code not in [200, 404, 401, 403]:
            print(f"   Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"   Error: {type(e).__name__}")

# 4. Suggestions
print("\n\n4. Troubleshooting Suggestions:")
print("   - Verify the API token is from AppsFlyer Dashboard > Integration > API Access")
print("   - Check if your account has access to the Master API")
print("   - Ensure the app ID matches exactly what's in AppsFlyer")
print("   - The JWT token format suggests you might need to use a different API")
print("\n   Documentation: https://support.appsflyer.com/hc/en-us/articles/207034346")
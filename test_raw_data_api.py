#!/usr/bin/env python3
"""
Test AppsFlyer Raw Data Export API
Tests various date ranges to understand API limitations
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def test_raw_data_api(from_date: str, to_date: str, description: str):
    """Test the raw data API with a specific date range"""
    
    api_token = os.getenv('APPSFLYER_API_TOKEN')
    app_id = os.getenv('APPSFLYER_APP_ID')
    
    if not api_token or not app_id:
        print("❌ Missing APPSFLYER_API_TOKEN or APPSFLYER_APP_ID")
        return
    
    # Raw data API endpoint
    url = f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/installs_report/v5"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'text/csv'
    }
    
    params = {
        'from': from_date,
        'to': to_date,
        'timezone': 'UTC'
    }
    
    print(f"\n🧪 Testing: {description}")
    print(f"   Date range: {from_date} to {to_date}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check response size
            content_length = len(response.content)
            print(f"   ✅ Success! Response size: {content_length:,} bytes")
            
            # Save first few lines for inspection
            lines = response.text.split('\n')[:5]
            print(f"   First few lines:")
            for line in lines:
                if line.strip():
                    print(f"      {line[:100]}...")
            
            # Save to file for further inspection
            filename = f"raw_data_test_{from_date}_to_{to_date}.csv"
            with open(filename, 'w') as f:
                f.write(response.text[:10000])  # Save first 10KB
            print(f"   📁 Sample saved to: {filename}")
            
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def main():
    """Test various date ranges"""
    
    print("🔍 Testing AppsFlyer Raw Data Export API")
    print("=" * 50)
    
    today = datetime.now().date()
    
    # Test 1: Last 7 days (should work)
    test_raw_data_api(
        (today - timedelta(days=7)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 7 days"
    )
    
    # Test 2: Last 30 days (should work)
    test_raw_data_api(
        (today - timedelta(days=30)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 30 days"
    )
    
    # Test 3: Last 90 days (testing the supposed limit)
    test_raw_data_api(
        (today - timedelta(days=90)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 90 days"
    )
    
    # Test 4: Last 180 days (beyond supposed limit)
    test_raw_data_api(
        (today - timedelta(days=180)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 180 days"
    )
    
    # Test 5: Last 365 days (full year)
    test_raw_data_api(
        (today - timedelta(days=365)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 365 days (full year)"
    )
    
    # Test 6: Specific week from last year (for YoY comparison)
    last_year_week = today - timedelta(days=365)
    week_start = last_year_week - timedelta(days=last_year_week.weekday())
    week_end = week_start + timedelta(days=6)
    test_raw_data_api(
        week_start.strftime('%Y-%m-%d'),
        week_end.strftime('%Y-%m-%d'),
        "Specific week from last year"
    )
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
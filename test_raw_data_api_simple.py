#!/usr/bin/env python3
"""
Test AppsFlyer Raw Data Export API
Tests various date ranges to understand API limitations
"""

import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

def load_env():
    """Simple .env loader"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    except FileNotFoundError:
        print("❌ .env file not found")
    return env_vars

def test_raw_data_api(from_date: str, to_date: str, description: str, env_vars: dict):
    """Test the raw data API with a specific date range"""
    
    api_token = env_vars.get('APPSFLYER_API_TOKEN')
    app_id = env_vars.get('APPSFLYER_APP_ID')
    
    if not api_token or not app_id:
        print("❌ Missing APPSFLYER_API_TOKEN or APPSFLYER_APP_ID in .env")
        return
    
    # Raw data API endpoint
    url = f"https://hq1.appsflyer.com/api/raw-data/export/app/{app_id}/installs_report/v5"
    
    params = {
        'from': from_date,
        'to': to_date,
        'timezone': 'UTC'
    }
    
    # Build URL with parameters
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    print(f"\n🧪 Testing: {description}")
    print(f"   Date range: {from_date} to {to_date}")
    print(f"   URL: {url}")
    
    try:
        # Create request with headers
        req = urllib.request.Request(full_url)
        req.add_header('Authorization', f'Bearer {api_token}')
        req.add_header('Accept', 'text/csv')
        
        # Make request
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.getcode()
            print(f"   Status: {status}")
            
            if status == 200:
                content = response.read()
                content_length = len(content)
                print(f"   ✅ Success! Response size: {content_length:,} bytes")
                
                # Decode and show first few lines
                text = content.decode('utf-8', errors='ignore')
                lines = text.split('\n')[:5]
                print(f"   First few lines:")
                for line in lines:
                    if line.strip():
                        print(f"      {line[:100]}...")
                
                # Save to file for further inspection
                filename = f"raw_data_test_{from_date}_to_{to_date}.csv"
                with open(filename, 'w') as f:
                    f.write(text[:10000])  # Save first 10KB
                print(f"   📁 Sample saved to: {filename}")
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code}")
        try:
            error_content = e.read().decode('utf-8')
            print(f"   Response: {error_content[:500]}")
        except:
            print(f"   Could not read error response")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def main():
    """Test various date ranges"""
    
    print("🔍 Testing AppsFlyer Raw Data Export API")
    print("=" * 50)
    
    # Load environment variables
    env_vars = load_env()
    if not env_vars:
        print("❌ Failed to load environment variables")
        return
    
    today = datetime.now().date()
    
    # Test 1: Last 7 days (should work)
    test_raw_data_api(
        (today - timedelta(days=7)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 7 days",
        env_vars
    )
    
    # Test 2: Last 30 days (should work)
    test_raw_data_api(
        (today - timedelta(days=30)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 30 days",
        env_vars
    )
    
    # Test 3: Last 90 days (testing the supposed limit)
    test_raw_data_api(
        (today - timedelta(days=90)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 90 days",
        env_vars
    )
    
    # Test 4: Last 180 days (beyond supposed limit)
    test_raw_data_api(
        (today - timedelta(days=180)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 180 days",
        env_vars
    )
    
    # Test 5: Last 365 days (full year)
    test_raw_data_api(
        (today - timedelta(days=365)).strftime('%Y-%m-%d'),
        today.strftime('%Y-%m-%d'),
        "Last 365 days (full year)",
        env_vars
    )
    
    # Test 6: Specific week from last year (for YoY comparison)
    last_year_week = today - timedelta(days=365)
    week_start = last_year_week - timedelta(days=last_year_week.weekday())
    week_end = week_start + timedelta(days=6)
    test_raw_data_api(
        week_start.strftime('%Y-%m-%d'),
        week_end.strftime('%Y-%m-%d'),
        "Specific week from last year",
        env_vars
    )
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
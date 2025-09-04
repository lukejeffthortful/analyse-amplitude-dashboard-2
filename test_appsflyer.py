#!/usr/bin/env python3
"""
AppsFlyer API Test Script
Proof of concept for fetching install data by media source and campaign
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from appsflyer_data_handler import AppsFlyerDataHandler


def test_appsflyer_integration():
    """Test AppsFlyer API integration"""
    print("🚀 AppsFlyer Integration Test")
    print("=" * 50)
    
    try:
        # Initialize handler
        print("\n1️⃣ Initializing AppsFlyer handler...")
        handler = AppsFlyerDataHandler()
        print("   ✅ Handler initialized successfully")
        
        # Test 1: Fetch last week's data
        print("\n2️⃣ Fetching last week's install data...")
        # Use a week from 2024 instead of current week to avoid future date issues
        weekly_data = handler.get_week_install_summary(target_week=33, year=2024)
        
        if weekly_data:
            print("   ✅ Data fetched successfully!")
            
            # Save raw data for inspection
            with open('test_appsflyer_weekly_data.json', 'w') as f:
                json.dump(weekly_data, f, indent=2)
            print("   📁 Raw data saved to: test_appsflyer_weekly_data.json")
            
            # Display summary
            print("\n3️⃣ Install Summary:")
            print("-" * 50)
            summary = handler.format_install_summary(weekly_data)
            print(summary)
            print("-" * 50)
            
            # Save summary
            with open('test_appsflyer_summary.txt', 'w') as f:
                f.write(summary)
            print("\n   📁 Summary saved to: test_appsflyer_summary.txt")
            
        else:
            print("   ❌ Failed to fetch data")
            return False
        
        # Test 2: Fetch specific date range (last 7 days)
        print("\n4️⃣ Testing custom date range (last 7 days)...")
        end_date = datetime.now() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=6)  # 7 days ago
        
        custom_data = handler.get_installs_by_source_and_campaign(start_date, end_date)
        
        if custom_data:
            print("   ✅ Custom date range data fetched successfully!")
            print(f"   📊 Total installs (7 days): {custom_data['total_installs']:,}")
            
            # Save custom range data
            with open('test_appsflyer_7day_data.json', 'w') as f:
                json.dump(custom_data, f, indent=2)
            print("   📁 7-day data saved to: test_appsflyer_7day_data.json")
        else:
            print("   ❌ Failed to fetch custom date range data")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_configuration():
    """Check if AppsFlyer is properly configured"""
    print("\n🔧 Configuration Check:")
    print("-" * 30)
    
    api_token = os.getenv('APPSFLYER_API_TOKEN')
    app_id = os.getenv('APPSFLYER_APP_ID')
    
    config_ok = True
    
    if api_token:
        print("✅ APPSFLYER_API_TOKEN is set")
    else:
        print("❌ APPSFLYER_API_TOKEN is missing")
        config_ok = False
    
    if app_id:
        print(f"✅ APPSFLYER_APP_ID is set: {app_id}")
    else:
        print("❌ APPSFLYER_APP_ID is missing")
        config_ok = False
    
    if not config_ok:
        print("\n⚠️  Please add the missing values to your .env file:")
        print("   APPSFLYER_API_TOKEN=your_api_token_here")
        print("   APPSFLYER_APP_ID=your_app_id_here")
    
    return config_ok


def main():
    """Main test runner"""
    print("🧪 AppsFlyer Integration - Proof of Concept")
    print("=" * 50)
    
    # Check configuration first
    if not check_configuration():
        print("\n❌ Configuration incomplete. Please update your .env file.")
        sys.exit(1)
    
    # Run tests
    if test_appsflyer_integration():
        print("\n🎉 AppsFlyer integration is working!")
        print("\n📋 Next steps:")
        print("1. Review the generated JSON files to understand the data structure")
        print("2. Integrate into the main amplitude_analyzer.py workflow")
        print("3. Add AppsFlyer data to the weekly executive summary")
    else:
        print("\n❌ AppsFlyer integration test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
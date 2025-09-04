#!/usr/bin/env python3
"""
Test AppsFlyer Pull API Integration (Plan-Compatible Version)
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

from appsflyer_pull_api_handler import AppsFlyerPullAPIHandler


def test_appsflyer_pull_api():
    """Test AppsFlyer Pull API integration"""
    print("🚀 AppsFlyer Pull API Integration Test")
    print("=" * 50)
    
    try:
        # Initialize handler
        print("\n1️⃣ Initializing AppsFlyer Pull API handler...")
        handler = AppsFlyerPullAPIHandler()
        print("   ✅ Handler initialized successfully")
        
        # Test with recent data (last 30 days to be safe)
        print("\n2️⃣ Fetching recent install data...")
        # Get data from 30 days ago to ensure it's within the 90-day limit
        from datetime import datetime, timedelta
        end_date = datetime.now() - timedelta(days=30)
        start_date = end_date - timedelta(days=6)  # 7-day period
        weekly_data = handler.get_installs_by_source_and_campaign(start_date, end_date)
        
        if weekly_data:
            print("   ✅ Data fetched successfully!")
            
            # Save raw data for inspection
            with open('test_pull_api_weekly_data.json', 'w') as f:
                json.dump(weekly_data, f, indent=2)
            print("   📁 Raw data saved to: test_pull_api_weekly_data.json")
            
            # Display summary
            print("\n3️⃣ Install Summary:")
            print("-" * 50)
            summary = handler.format_install_summary(weekly_data)
            print(summary)
            print("-" * 50)
            
            # Save summary
            with open('test_pull_api_summary.txt', 'w') as f:
                f.write(summary)
            print("\n   📁 Summary saved to: test_pull_api_summary.txt")
            
        else:
            print("   ❌ Failed to fetch data")
            return False
        
        print("\n✅ Pull API test completed successfully!")
        print("\n📋 Key Points:")
        print("   • Using Pull API (compatible with your plan)")
        print("   • Limited to 10 API calls per day")
        print("   • Shows non-organic installs only")
        print("   • Data grouped by media source and campaign")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print("🧪 AppsFlyer Pull API - Plan-Compatible Integration")
    print("=" * 60)
    print("⚠️  This will use 1 of your 10 daily API calls")
    
    # Auto-confirm for testing
    print("\nProceeding with API test...")
    # response = input("\nProceed with API test? (y/N): ")
    # if response.lower() != 'y':
    #     print("Test cancelled.")
    #     return
    
    # Run test
    if test_appsflyer_pull_api():
        print("\n🎉 AppsFlyer Pull API integration is working!")
        print("\n📋 Next steps:")
        print("1. Review the generated files to understand the data structure")
        print("2. Integrate into the main analytics workflow")
        print("3. Add AppsFlyer data to weekly reports")
        print("4. Monitor daily API call usage (10 per day limit)")
    else:
        print("\n❌ AppsFlyer Pull API integration test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
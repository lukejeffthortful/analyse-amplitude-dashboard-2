#!/usr/bin/env python3
"""
Local testing script for Amplitude Analyzer
Runs analysis without side effects (no Slack notifications)
"""

import os
import sys
from datetime import datetime, timedelta

# Set test environment before imports
print("🧪 Running in TEST MODE - No external notifications will be sent")
os.environ['SLACK_WEBHOOK_URL'] = ''  # Disable Slack notifications
os.environ['TEST_MODE'] = 'true'

# Import after setting environment
from amplitude_analyzer import AmplitudeAnalyzer

def test_specific_week(week_number=None):
    """Test analysis for a specific week"""
    analyzer = AmplitudeAnalyzer()
    
    if week_number:
        print(f"\n📊 Testing analysis for Week {week_number}")
        # You would need to modify the analyzer to accept target_week parameter
        # For now, it will analyze the previous week
    else:
        # Calculate previous week
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        iso_year, iso_week = analyzer.get_iso_week_info(last_monday)
        print(f"\n📊 Testing analysis for Week {iso_week} of {iso_year}")
    
    try:
        # Run the analysis
        print("\n🔄 Fetching data from Amplitude...")
        analyzer.run_weekly_analysis()
        
        print("\n✅ Test completed successfully!")
        print("📁 Check these output files:")
        print("   - weekly_analysis.json")
        print("   - weekly_summary.txt")
        
        # Display summary
        if os.path.exists('weekly_summary.txt'):
            print("\n📋 Generated Summary:")
            print("-" * 50)
            with open('weekly_summary.txt', 'r') as f:
                print(f.read())
            print("-" * 50)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_dry_run():
    """Test without making any API calls"""
    print("\n🏃 Dry run test - Checking configuration...")
    
    analyzer = AmplitudeAnalyzer()
    
    # Check configuration
    config_ok = True
    
    if not analyzer.api_key or not analyzer.secret_key:
        print("❌ Amplitude credentials not configured")
        config_ok = False
    else:
        print("✅ Amplitude credentials configured")
    
    if analyzer.use_unified:
        print("✅ GA4 integration enabled")
    else:
        print("ℹ️  GA4 integration disabled")
    
    print(f"\n📊 Configured charts:")
    for name, chart_id in analyzer.charts.items():
        print(f"   - {name}: {chart_id}")
    
    return config_ok

def main():
    """Main test runner"""
    print("🚀 Amplitude Analyzer - Local Test Suite")
    print("=" * 50)
    
    # Check if specific test requested
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dry-run':
            test_dry_run()
        elif sys.argv[1] == '--week' and len(sys.argv) > 2:
            week_num = int(sys.argv[2])
            test_specific_week(week_num)
        else:
            print("Usage:")
            print("  python test_local.py              # Test previous week")
            print("  python test_local.py --dry-run    # Check configuration only")
            print("  python test_local.py --week 29    # Test specific week")
    else:
        # Default: test previous week
        test_specific_week()

if __name__ == "__main__":
    main()
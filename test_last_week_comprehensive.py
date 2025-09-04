#!/usr/bin/env python3
"""Test comprehensive summary with last week's dates (Aug 4-10, 2025)"""

from datetime import datetime
from appsflyer_csv_handler import AppsFlyerCSVHandler

# Last week's dates
start_date = datetime(2025, 8, 4)
end_date = datetime(2025, 8, 10)
week_num = 32  # Week 32 of 2025

print("=" * 80)
print(f"TESTING COMPREHENSIVE SUMMARY - Week {week_num}, 2025")
print(f"Period: {start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}")
print("=" * 80)

# Test AppsFlyer data availability
print("\n📱 TESTING APPSFLYER DATA AVAILABILITY")
print("-" * 60)

handler = AppsFlyerCSVHandler()

# Check if we have data for this date range
csv_file = handler.find_csv_for_date_range(start_date, end_date)

if csv_file:
    print(f"✅ Found CSV file: {csv_file}")
    
    # Get the install data
    install_data = handler.get_installs_by_source_and_campaign(start_date, end_date)
    
    if install_data:
        print(f"\n📊 AppsFlyer Data Summary:")
        print(f"Total Installs: {install_data['total_installs']:,}")
        
        print("\nTop 5 Install Sources:")
        for i, source in enumerate(install_data['top_sources'][:5], 1):
            print(f"  {i}. {source['source']}: {source['installs']:,} installs")
        
        # Check for Google Ads
        if 'googleadwords_int' in install_data['by_media_source']:
            print(f"\n✅ Google Ads data present: {install_data['by_media_source']['googleadwords_int']:,} installs")
        else:
            print("\n❌ No Google Ads data found")
            
        # Show the formatted summary
        print("\n" + "="*60)
        print("FORMATTED SUMMARY:")
        print("="*60)
        print(handler.format_install_summary(install_data))
        
else:
    print(f"❌ No CSV file found for date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Show available ranges
    available_ranges = handler.get_available_date_ranges()
    if available_ranges:
        print("\n📊 Available date ranges in CSV exports:")
        for start, end in available_ranges:
            print(f"   • {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
            
            # Check if our requested dates fall within this range
            if start <= start_date and end >= end_date:
                print(f"     ✅ This file SHOULD contain Aug 4-10 data!")

print("\n" + "="*80)
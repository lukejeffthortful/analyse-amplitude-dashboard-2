#!/usr/bin/env python3
"""Test comprehensive summary with August 4-10 dates using merged data"""

from datetime import datetime
from appsflyer_csv_handler import AppsFlyerCSVHandler

# August 4-10, 2025 (Week 32)
start_date = datetime(2025, 8, 4)
end_date = datetime(2025, 8, 10)
week_num = 32

print("=" * 80)
print(f"TESTING WITH MERGED DATA - Week {week_num}, 2025")
print(f"Period: {start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}")
print("=" * 80)

# Initialize handler (will auto-merge if needed)
handler = AppsFlyerCSVHandler()

# Get install data for the week
print("\n📱 APPSFLYER INSTALL METRICS")
print("-" * 60)

install_data = handler.get_installs_by_source_and_campaign(start_date, end_date)

if install_data:
    # Display summary
    print(handler.format_install_summary(install_data))
    
    # Verify we have data from both date ranges
    print("\n🔍 Data Verification:")
    print(f"CSV File Used: {install_data.get('csv_file', 'Unknown')}")
    print(f"Total Installs: {install_data['total_installs']:,}")
    
    # Check for key sources
    key_sources = {
        'googleadwords_int': 'Google Ads',
        'organic': 'Organic',
        'website-thortful': 'Website',
        'Facebook Ads': 'Facebook',
        'google_organic_seo': 'Google SEO'
    }
    
    print("\n📊 Install Sources Breakdown:")
    for source_key, display_name in key_sources.items():
        if source_key in install_data['by_media_source']:
            installs = install_data['by_media_source'][source_key]
            pct = (installs / install_data['total_installs'] * 100)
            print(f"  • {display_name}: {installs:,} ({pct:.1f}%)")
    
    # Show top campaigns
    print("\n🏆 Top 5 Campaigns:")
    for i, campaign in enumerate(install_data['top_campaigns'][:5], 1):
        if campaign['campaign'] != 'None':
            print(f"  {i}. {campaign['campaign']}: {campaign['installs']:,}")
    
    print("\n✅ Successfully retrieved data for August 4-10!")
    
else:
    print("❌ Failed to retrieve data")

print("\n" + "="*80)
#!/usr/bin/env python3
"""Test AppsFlyer CSV data integration for ISO Week 34 (August 19-25, 2025)"""

from datetime import datetime
from appsflyer_csv_handler import AppsFlyerCSVHandler

def test_week_34_appsflyer():
    """Test AppsFlyer data for Week 34, 2025"""
    
    # ISO Week 34, 2025 = August 19-25, 2025
    week_num = 34
    year = 2025
    
    # Calculate exact dates for Week 34
    # Week 34 starts on Monday August 18, 2025 and ends Sunday August 24, 2025
    start_date = datetime(2025, 8, 18)  # Monday 
    end_date = datetime(2025, 8, 24)    # Sunday
    
    print("=" * 80)
    print(f"APPSFLYER CSV TEST - Week {week_num}, {year}")
    print(f"Period: {start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}")
    print("=" * 80)
    
    # Initialize AppsFlyer CSV handler
    handler = AppsFlyerCSVHandler()
    
    print("\n📂 CSV Files Available:")
    available_ranges = handler.get_available_date_ranges()
    for i, (start, end) in enumerate(available_ranges, 1):
        print(f"  {i}. {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    
    # Test using week-based method
    print(f"\n📅 Testing Week {week_num} Method:")
    week_data = handler.get_week_install_summary(target_week=week_num, year=year)
    
    if week_data:
        print("✅ Week method successful!")
        print(f"Total Installs: {week_data['total_installs']:,}")
        print(f"CSV File Used: {week_data.get('csv_file', 'Unknown')}")
    else:
        print("❌ Week method failed")
    
    # Test using date range method
    print(f"\n📅 Testing Date Range Method ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}):")
    range_data = handler.get_installs_by_source_and_campaign(start_date, end_date)
    
    if range_data:
        print("✅ Date range method successful!")
        print(f"Total Installs: {range_data['total_installs']:,}")
        print(f"CSV File Used: {range_data.get('csv_file', 'Unknown')}")
        
        # Display formatted summary
        print("\n" + "="*60)
        print("FORMATTED INSTALL SUMMARY")
        print("="*60)
        print(handler.format_install_summary(range_data))
        
        # Show key metrics for integration
        print("\n" + "="*60)
        print("KEY INTEGRATION METRICS")
        print("="*60)
        
        # Check for key sources that would be included in reports
        key_sources = {
            'organic': 'Organic Traffic',
            'googleadwords_int': 'Google Ads', 
            'google_organic_seo': 'Google SEO',
            'website-thortful': 'Website Direct',
            'Facebook Ads': 'Facebook Ads',
            'Apple Search Ads': 'Apple Search'
        }
        
        print("Install Sources Breakdown:")
        for source_key, display_name in key_sources.items():
            if source_key in range_data['by_media_source']:
                count = range_data['by_media_source'][source_key]
                pct = (count / range_data['total_installs'] * 100)
                print(f"  • {display_name}: {count:,} ({pct:.1f}%)")
        
        # Show top campaigns
        print("\nTop 5 Campaigns:")
        for i, campaign in enumerate(range_data['top_campaigns'][:5], 1):
            if campaign['campaign'] != 'None':
                pct = (campaign['installs'] / range_data['total_installs'] * 100)
                print(f"  {i}. {campaign['campaign']}: {campaign['installs']:,} ({pct:.1f}%)")
        
        # Check data quality
        print("\n" + "="*60)
        print("DATA QUALITY CHECK")
        print("="*60)
        
        # Verify we have key expected sources
        has_google_ads = 'googleadwords_int' in range_data['by_media_source']
        has_organic = 'organic' in range_data['by_media_source'] 
        has_website = 'website-thortful' in range_data['by_media_source']
        
        print(f"Google Ads data present: {'✅ Yes' if has_google_ads else '❌ No'}")
        print(f"Organic data present: {'✅ Yes' if has_organic else '❌ No'}")
        print(f"Website data present: {'✅ Yes' if has_website else '❌ No'}")
        
        if has_google_ads:
            google_ads_installs = range_data['by_media_source']['googleadwords_int']
            print(f"Google Ads installs: {google_ads_installs:,}")
        
        # Check if date range is covered by available data
        file_dates = None
        for start_avail, end_avail in available_ranges:
            if start_avail <= start_date and end_avail >= end_date:
                file_dates = (start_avail, end_avail)
                break
        
        if file_dates:
            print(f"✅ Date range fully covered by CSV: {file_dates[0].strftime('%Y-%m-%d')} to {file_dates[1].strftime('%Y-%m-%d')}")
        else:
            print("⚠️  Date range may not be fully covered by available CSV files")
            
    else:
        print("❌ Date range method failed")
        print("\n💡 Possible reasons:")
        print("  1. No CSV file covers the August 18-24, 2025 date range")
        print("  2. CSV files need to be exported from AppsFlyer dashboard")
        print("  3. File naming doesn't match expected format (YYYY-MM-DD__YYYY-MM-DD.csv)")

def show_integration_example():
    """Show how AppsFlyer data would be integrated into main analyzer"""
    
    print("\n" + "="*80)
    print("INTEGRATION EXAMPLE FOR AMPLITUDE ANALYZER")
    print("="*80)
    
    integration_code = '''
# In amplitude_analyzer.py, add AppsFlyer integration:

from appsflyer_csv_handler import AppsFlyerCSVHandler

class AmplitudeAnalyzer:
    def __init__(self):
        # ... existing initialization ...
        
        # Initialize AppsFlyer handler
        self.appsflyer_handler = AppsFlyerCSVHandler()
    
    def analyze_weekly_data(self, target_week=None, target_year=None):
        # ... existing Amplitude analysis ...
        
        # Add AppsFlyer install data
        appsflyer_data = self.appsflyer_handler.get_week_install_summary(
            target_week=target_week, 
            year=target_year
        )
        
        return {
            'week_info': week_info,
            'metrics': metrics,
            'appsflyer_installs': appsflyer_data  # NEW: AppsFlyer data
        }
    
    def generate_executive_summary(self, analysis_data):
        # ... existing summary generation ...
        
        # Add AppsFlyer section
        if analysis_data.get('appsflyer_installs'):
            installs = analysis_data['appsflyer_installs']
            summary += f"\\n\\nApp Install Analysis:\\n"
            summary += f"Total Installs: {installs['total_installs']:,}\\n"
            
            # Key sources
            for source in installs['top_sources'][:3]:
                pct = source['installs'] / installs['total_installs'] * 100
                summary += f"• {source['source']}: {source['installs']:,} ({pct:.1f}%)\\n"
        
        return summary
'''
    
    print(integration_code)
    
    print("\n💡 Key Benefits of This Integration:")
    print("  ✅ Includes Google Ads data (missing from API)")
    print("  ✅ No API rate limits")
    print("  ✅ Historical data available")
    print("  ✅ Campaign-level detail")
    print("  ✅ Integrates with existing weekly reporting")
    
    print("\n⚠️  Requirements:")
    print("  • Manual CSV export from AppsFlyer dashboard")
    print("  • Files saved in appsflyer-report-exports/ directory")
    print("  • Correct naming: YYYY-MM-DD__YYYY-MM-DD.csv")

if __name__ == "__main__":
    test_week_34_appsflyer()
    show_integration_example()
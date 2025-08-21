#!/usr/bin/env python3
"""Test script for ISO week 34 with comprehensive summary including AppsFlyer data"""

import os
import sys
from datetime import datetime, timedelta
import json

# Set test environment
print("🧪 Running Week 34 Comprehensive Test - No Slack notifications")
os.environ['SLACK_WEBHOOK_URL'] = ''
os.environ['TEST_MODE'] = 'true'

# Import required modules
from amplitude_analyzer import AmplitudeAnalyzer
from appsflyer_csv_handler import AppsFlyerCSVHandler

def test_week_34():
    """Generate comprehensive summary for ISO week 34"""
    
    # Week 34 details
    week_num = 34
    year = 2025
    
    # Calculate date range for week 34
    # Week 34 of 2025: August 18-24 (Monday to Sunday)
    start_date = datetime(2025, 8, 18)
    end_date = datetime(2025, 8, 24)
    
    print("="*80)
    print(f"COMPREHENSIVE WEEKLY PERFORMANCE REPORT - Week {week_num}, {year}")
    print(f"Period: {start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}")
    print("="*80)
    
    # 1. AMPLITUDE DATA
    print("\n🔄 Fetching Amplitude data for Week 34...")
    
    # Initialize analyzer
    analyzer = AmplitudeAnalyzer()
    
    # Modify target week to week 34
    # Calculate the Monday of week 34
    jan1 = datetime(year, 1, 1)
    jan1_weekday = jan1.weekday()
    days_to_week1_monday = (7 - jan1_weekday) % 7
    if jan1_weekday <= 3:  # Thursday or earlier
        days_to_week1_monday = -jan1_weekday
    week1_monday = jan1 + timedelta(days=days_to_week1_monday)
    target_monday = week1_monday + timedelta(weeks=week_num-1)
    
    # Override the analyzer's week calculation
    analyzer.target_monday = target_monday
    analyzer.target_sunday = target_monday + timedelta(days=6)
    
    # Fetch Amplitude data
    try:
        # Get data for each chart
        amplitude_data = {}
        
        for chart_name, chart_id in analyzer.charts.items():
            print(f"  Fetching {chart_name}...")
            
            # Current week data
            current_data = analyzer.fetch_chart_data(
                chart_id,
                analyzer.target_monday,
                analyzer.target_sunday
            )
            
            # Previous year data
            prev_year_monday = analyzer.target_monday.replace(year=analyzer.target_monday.year - 1)
            prev_year_sunday = analyzer.target_sunday.replace(year=analyzer.target_sunday.year - 1)
            prev_data = analyzer.fetch_chart_data(
                chart_id,
                prev_year_monday,
                prev_year_sunday
            )
            
            amplitude_data[chart_name] = {
                'current': current_data,
                'previous': prev_data,
                'current_week': week_num,
                'current_year': year
            }
        
        # Process and display Amplitude metrics
        print("\n📊 AMPLITUDE METRICS - YoY Analysis")
        print("-" * 60)
        
        # Sessions
        if 'Sessions' in amplitude_data:
            current_sessions = amplitude_data['Sessions']['current']['value']
            prev_sessions = amplitude_data['Sessions']['previous']['value']
            yoy_change = ((current_sessions - prev_sessions) / prev_sessions * 100) if prev_sessions > 0 else 0
            print(f"Sessions: {current_sessions:,} vs {prev_sessions:,} ({yoy_change:+.1f}% YoY)")
        
        # Active Users
        if 'Active Users' in amplitude_data:
            current_users = amplitude_data['Active Users']['current']['value']
            prev_users = amplitude_data['Active Users']['previous']['value']
            yoy_change = ((current_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
            print(f"Active Users: {current_users:,} vs {prev_users:,} ({yoy_change:+.1f}% YoY)")
        
        # Conversion rates
        if 'Session Conversion' in amplitude_data:
            current_conv = amplitude_data['Session Conversion']['current']['value']
            prev_conv = amplitude_data['Session Conversion']['previous']['value']
            conv_change = current_conv - prev_conv
            print(f"Session Conversion: {current_conv:.1f}% vs {prev_conv:.1f}% ({conv_change:+.1f} ppts YoY)")
        
        # Platform breakdown
        if 'Sessions by Platform' in amplitude_data:
            platform_data = amplitude_data['Sessions by Platform']['current']
            print("\nPlatform Breakdown:")
            if 'series' in platform_data:
                for platform in platform_data['series']:
                    name = platform['seriesName']
                    value = platform['value']
                    pct = platform.get('percentage', 0)
                    print(f"• {name}: {value:,} sessions ({pct:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error fetching Amplitude data: {e}")
        amplitude_data = None
    
    # 2. APPSFLYER DATA
    print("\n📱 APPSFLYER INSTALL METRICS")
    print("-" * 60)
    
    handler = AppsFlyerCSVHandler()
    install_data = handler.get_week_install_summary(target_week=week_num, year=year)
    
    if install_data:
        total_installs = install_data['total_installs']
        
        print(f"Total App Installs: {total_installs:,}")
        
        # Check data coverage
        if 'date_range' in install_data:
            print(f"Data Coverage: {install_data['date_range']['start']} to {install_data['date_range']['end']}")
            if install_data['date_range']['end'] < '2025-08-24':
                print("⚠️  WARNING: Incomplete week data (missing days after Aug 19)")
        
        # Install Sources
        print("\nInstall Sources:")
        sources = [
            ('organic', 'Organic'),
            ('googleadwords_int', 'Google Ads'),
            ('website-thortful', 'Website'),
            ('Facebook Ads', 'Facebook Ads'),
            ('google_organic_seo', 'Google SEO'),
            ('Apple Search Ads', 'Apple Search')
        ]
        
        for source_key, display_name in sources:
            if source_key in install_data['by_media_source']:
                count = install_data['by_media_source'][source_key]
                pct = (count / total_installs * 100) if total_installs > 0 else 0
                print(f"• {display_name}: {count:,} ({pct:.1f}%)")
        
        # Top Campaigns
        print("\nTop Performing Campaigns:")
        campaign_count = 0
        for item in install_data['top_campaigns'][:5]:
            if item['campaign'] != 'None':
                campaign_count += 1
                print(f"{campaign_count}. {item['campaign']}: {item['installs']:,} installs")
    else:
        print("❌ No AppsFlyer data available for Week 34")
    
    # 3. INTEGRATED PERFORMANCE METRICS
    print("\n🎯 INTEGRATED PERFORMANCE METRICS")
    print("-" * 60)
    
    if amplitude_data and install_data:
        # Funnel metrics
        print("Acquisition Funnel:")
        print(f"• Installs: {total_installs:,}")
        if 'Active Users' in amplitude_data:
            active_users = amplitude_data['Active Users']['current']['value']
            print(f"• Active Users (Amplitude): {active_users:,}")
            print(f"• Install → Active Rate: {(active_users/total_installs*100):.1f}%")
        
        # Channel ROI
        print("\nChannel Performance:")
        organic_installs = install_data['by_media_source'].get('organic', 0) + \
                          install_data['by_media_source'].get('google_organic_seo', 0)
        paid_installs = install_data['by_media_source'].get('googleadwords_int', 0) + \
                       install_data['by_media_source'].get('Facebook Ads', 0)
        
        print(f"• Organic: {organic_installs:,} installs ({organic_installs/total_installs*100:.1f}%)")
        print(f"• Paid: {paid_installs:,} installs ({paid_installs/total_installs*100:.1f}%)")
    
    # 4. EXECUTIVE SUMMARY
    print("\n📋 EXECUTIVE SUMMARY")
    print("-" * 60)
    print("Performance Highlights:")
    
    if amplitude_data:
        if 'Sessions' in amplitude_data:
            current = amplitude_data['Sessions']['current']['value']
            prev = amplitude_data['Sessions']['previous']['value']
            yoy = ((current - prev) / prev * 100) if prev > 0 else 0
            print(f"✅ Sessions: {current:,} ({yoy:+.1f}% YoY)")
    
    if install_data:
        print(f"✅ App Installs: {total_installs:,} total")
        organic_pct = (install_data['by_media_source'].get('organic', 0) / total_installs * 100) if total_installs > 0 else 0
        print(f"✅ Organic Share: {organic_pct:.1f}% of installs")
    
    print("\n" + "="*80)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Save results
    results = {
        'week': week_num,
        'year': year,
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'amplitude_data': amplitude_data if amplitude_data else {},
        'appsflyer_data': install_data if install_data else {},
        'generated_at': datetime.now().isoformat()
    }
    
    with open('week_34_comprehensive_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n📁 Results saved to: week_34_comprehensive_results.json")

if __name__ == "__main__":
    test_week_34()
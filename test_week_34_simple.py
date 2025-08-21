#!/usr/bin/env python3
"""Simple test script for ISO week 34 with AppsFlyer integration"""

import os
import sys
from datetime import datetime
import json

# Set test environment
print("🧪 Running Week 34 Test - No Slack notifications")
os.environ['SLACK_WEBHOOK_URL'] = ''
os.environ['TEST_MODE'] = 'true'

# Import required modules
from amplitude_analyzer import AmplitudeAnalyzer
from appsflyer_csv_handler import AppsFlyerCSVHandler

def generate_comprehensive_summary_week_34():
    """Generate comprehensive summary for ISO week 34"""
    
    # Week 34 details
    week_num = 34
    year = 2025
    
    print("="*80)
    print(f"COMPREHENSIVE WEEKLY PERFORMANCE REPORT - Week {week_num}, {year}")
    print("Period: August 18-24, 2025")
    print("="*80)
    
    # 1. AMPLITUDE DATA
    print("\n🔄 Fetching Amplitude data for Week 34...")
    
    analyzer = AmplitudeAnalyzer()
    
    try:
        # Analyze week 34 data
        amplitude_analysis = analyzer.analyze_weekly_data(target_week=week_num, target_year=year)
        
        # Generate executive summary
        amplitude_summary = analyzer.generate_executive_summary(amplitude_analysis)
        
        print("\n📊 AMPLITUDE METRICS - YoY Analysis")
        print("-" * 60)
        print(amplitude_summary)
        
        # Save amplitude data
        with open('week_34_amplitude_data.json', 'w') as f:
            json.dump(amplitude_analysis, f, indent=2, default=str)
        
    except Exception as e:
        print(f"❌ Error with Amplitude data: {e}")
        amplitude_analysis = None
        amplitude_summary = None
    
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
    
    # 3. INTEGRATED METRICS (if both data sources available)
    if amplitude_analysis and install_data:
        print("\n🎯 INTEGRATED PERFORMANCE METRICS")
        print("-" * 60)
        
        # Extract active users if available
        active_users = None
        if 'metrics' in amplitude_analysis and 'sessions' in amplitude_analysis['metrics']:
            sessions_data = amplitude_analysis['metrics']['sessions']
            if 'current_week' in sessions_data and 'total' in sessions_data['current_week']:
                # Estimate active users from sessions (rough estimate)
                total_sessions = sessions_data['current_week']['total']
                sessions_per_user = 3.5  # Default estimate
                if 'sessions_per_user' in amplitude_analysis['metrics']:
                    spu_data = amplitude_analysis['metrics']['sessions_per_user']
                    if 'current_week' in spu_data and 'total' in spu_data['current_week']:
                        sessions_per_user = spu_data['current_week']['total']
                active_users = int(total_sessions / sessions_per_user)
        
        if active_users:
            print("Acquisition Funnel:")
            print(f"• Installs: {total_installs:,}")
            print(f"• Active Users (est.): {active_users:,}")
            print(f"• Install → Active Rate: {(active_users/total_installs*100):.1f}%")
        
        # Channel Performance
        print("\nChannel Performance:")
        organic_installs = install_data['by_media_source'].get('organic', 0) + \
                          install_data['by_media_source'].get('google_organic_seo', 0)
        paid_installs = install_data['by_media_source'].get('googleadwords_int', 0) + \
                       install_data['by_media_source'].get('Facebook Ads', 0)
        
        print(f"• Organic: {organic_installs:,} installs ({organic_installs/total_installs*100:.1f}%)")
        print(f"• Paid: {paid_installs:,} installs ({paid_installs/total_installs*100:.1f}%)")
        print(f"• Website: {install_data['by_media_source'].get('website-thortful', 0):,} installs")
    
    # 4. SLACK-STYLE SUMMARY
    print("\n" + "="*80)
    print("SLACK VERSION (Week 34)")
    print("="*80 + "\n")
    
    slack_summary = []
    slack_summary.append(f"📊 *Weekly Performance Report - Week {week_num}, {year}*")
    slack_summary.append("_August 18-24, 2025_\n")
    
    # Add Amplitude metrics if available
    if amplitude_summary:
        slack_summary.append("*📈 Amplitude Metrics (YoY)*")
        # Extract key metrics from the summary
        summary_lines = amplitude_summary.split('\n')
        for line in summary_lines[:5]:  # First few lines usually have key metrics
            if line.strip():
                slack_summary.append(f"• {line.strip()}")
        slack_summary.append("")
    
    # Add AppsFlyer metrics
    if install_data:
        slack_summary.append("*📱 App Install Metrics (AppsFlyer)*")
        slack_summary.append("```")
        slack_summary.append(f"Total Installs:  {total_installs:,}")
        slack_summary.append(f"Organic:         {install_data['by_media_source'].get('organic', 0):,} ({install_data['by_media_source'].get('organic', 0)/total_installs*100:.1f}%)")
        slack_summary.append(f"Google Ads:      {install_data['by_media_source'].get('googleadwords_int', 0):,} ({install_data['by_media_source'].get('googleadwords_int', 0)/total_installs*100:.1f}%)")
        slack_summary.append(f"Website:         {install_data['by_media_source'].get('website-thortful', 0):,} ({install_data['by_media_source'].get('website-thortful', 0)/total_installs*100:.1f}%)")
        slack_summary.append("```")
    
    # Key insights
    slack_summary.append("\n*🎯 Key Insights*")
    if amplitude_analysis:
        slack_summary.append("• Amplitude data processed for Week 34")
    if install_data:
        organic_pct = (install_data['by_media_source'].get('organic', 0) / total_installs * 100) if total_installs > 0 else 0
        slack_summary.append(f"• Strong organic acquisition at {organic_pct:.1f}%")
        if install_data['by_media_source'].get('googleadwords_int', 0) > 100000:
            slack_summary.append("• Google Ads performing well with 100K+ installs")
    
    slack_text = "\n".join(slack_summary)
    print(slack_text)
    
    # Save Slack summary
    with open('week_34_slack_summary.txt', 'w') as f:
        f.write(slack_text)
    
    print("\n" + "="*80)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📁 Files saved:")
    print("   - week_34_amplitude_data.json")
    print("   - week_34_slack_summary.txt")
    print("="*80)

if __name__ == "__main__":
    generate_comprehensive_summary_week_34()
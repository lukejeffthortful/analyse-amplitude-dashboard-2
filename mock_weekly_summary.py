#!/usr/bin/env python3
"""Mock weekly performance summary integrating AppsFlyer data"""

from datetime import datetime
from appsflyer_csv_handler import AppsFlyerCSVHandler

def generate_mock_weekly_summary():
    """Generate a mock weekly summary combining Amplitude and AppsFlyer data"""
    
    # Week 3, 2025 (Jan 13-19)
    week_num = 3
    year = 2025
    
    print("=" * 70)
    print(f"WEEKLY PERFORMANCE SUMMARY - Week {week_num}, {year}")
    print(f"Period: January 13-19, 2025")
    print("=" * 70)
    
    # AMPLITUDE DATA (Mock)
    print("\n📊 USER ENGAGEMENT METRICS (Amplitude)")
    print("-" * 50)
    
    # Current week metrics
    print("This Week:")
    print("  • Daily Active Users (DAU): 45,230 avg")
    print("  • Weekly Active Users (WAU): 156,892")
    print("  • Sessions: 412,567")
    print("  • Avg Session Duration: 4m 32s")
    print("  • Cards Sent: 89,234")
    print("  • Revenue: £145,678")
    
    # YoY comparison
    print("\nYear-over-Year Comparison:")
    print("  • DAU: +23.5% (vs 36,654 in Week 3, 2024)")
    print("  • WAU: +18.2% (vs 132,678 in Week 3, 2024)")
    print("  • Revenue: +31.4% (vs £110,892 in Week 3, 2024)")
    
    # APPSFLYER DATA (Real from CSV)
    print("\n📱 APP INSTALL METRICS (AppsFlyer)")
    print("-" * 50)
    
    handler = AppsFlyerCSVHandler()
    install_data = handler.get_week_install_summary(target_week=week_num, year=year)
    
    if install_data:
        total_installs = install_data['total_installs']
        
        print(f"Total Installs: {total_installs:,}")
        
        # Key sources breakdown
        print("\nInstall Sources:")
        sources_of_interest = [
            ('organic', 'Organic'),
            ('googleadwords_int', 'Google Ads'),
            ('website-thortful', 'Website'),
            ('Facebook Ads', 'Facebook Ads'),
            ('google_organic_seo', 'Google SEO')
        ]
        
        for source_key, display_name in sources_of_interest:
            if source_key in install_data['by_media_source']:
                count = install_data['by_media_source'][source_key]
                pct = (count / total_installs * 100) if total_installs > 0 else 0
                print(f"  • {display_name}: {count:,} ({pct:.1f}%)")
        
        # Top performing campaigns
        print("\nTop Performing Campaigns:")
        campaign_count = 0
        for item in install_data['top_campaigns'][:5]:
            if item['campaign'] != 'None':
                campaign_count += 1
                print(f"  {campaign_count}. {item['campaign']}: {item['installs']:,} installs")
    
    # INTEGRATED INSIGHTS
    print("\n🎯 INTEGRATED INSIGHTS")
    print("-" * 50)
    
    # Calculate conversion metrics
    if install_data:
        # Conversion from install to active user (mock calculation)
        install_to_active_rate = (156892 / total_installs * 100) if total_installs > 0 else 0
        
        print(f"• Install to Active User Rate: {install_to_active_rate:.1f}%")
        print(f"• Cost per Install (Paid): £{(25000 / (total_installs * 0.3)):.2f}") # Mock: assume 30% paid
        print(f"• Revenue per User: £{(145678 / 156892):.2f}")
        print(f"• LTV/CAC Ratio: 3.2:1")
    
    # Channel performance
    print("\n📈 CHANNEL PERFORMANCE ANALYSIS")
    print("-" * 50)
    
    print("Organic Channels:")
    if install_data:
        organic_total = install_data['by_media_source'].get('organic', 0) + \
                       install_data['by_media_source'].get('google_organic_seo', 0)
        print(f"  • Total Organic Installs: {organic_total:,} ({organic_total/total_installs*100:.1f}%)")
        print(f"  • Organic User Quality: High (4.8m avg session)")
    
    print("\nPaid Channels:")
    if install_data:
        paid_total = install_data['by_media_source'].get('googleadwords_int', 0) + \
                    install_data['by_media_source'].get('Facebook Ads', 0)
        print(f"  • Total Paid Installs: {paid_total:,} ({paid_total/total_installs*100:.1f}%)")
        print(f"  • Paid User Quality: Medium (3.2m avg session)")
        print(f"  • ROAS: 2.8x")
    
    print("\nWebsite Referrals:")
    if install_data:
        web_installs = install_data['by_media_source'].get('website-thortful', 0)
        print(f"  • Website-driven Installs: {web_installs:,} ({web_installs/total_installs*100:.1f}%)")
        print(f"  • Conversion Rate: 2.3%")
    
    # EXECUTIVE SUMMARY
    print("\n📋 EXECUTIVE SUMMARY")
    print("-" * 50)
    print("✅ Strong YoY growth: Revenue +31.4%, DAU +23.5%")
    print("✅ Healthy channel mix: 47% organic, 30% paid, 22% website")
    print("✅ Google Ads performing well with 119K installs")
    print("⚠️  Facebook Ads underperforming - only 5.6% of installs")
    print("📈 Recommendation: Increase Google Ads budget, optimize Facebook campaigns")
    
    # ALERTS
    print("\n🚨 ALERTS & ACTIONS")
    print("-" * 50)
    print("• Monitor: Install-to-active conversion trending down 2% WoW")
    print("• Action: Review onboarding flow for friction points")
    print("• Opportunity: Website referrals up 15% - consider promotional banner test")
    
    print("\n" + "=" * 70)
    print("Report generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

if __name__ == "__main__":
    generate_mock_weekly_summary()
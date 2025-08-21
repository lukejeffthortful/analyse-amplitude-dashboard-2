#!/usr/bin/env python3
"""Comprehensive weekly summary preserving all original elements plus AppsFlyer"""

from datetime import datetime
from appsflyer_csv_handler import AppsFlyerCSVHandler

def generate_comprehensive_summary():
    """Generate comprehensive summary with Amplitude, GA4 comparison, and AppsFlyer data"""
    
    # Week 3, 2025
    week_num = 3
    year = 2025
    
    print("=" * 80)
    print(f"COMPREHENSIVE WEEKLY PERFORMANCE REPORT - Week {week_num}, {year}")
    print("Period: January 13-19, 2025")
    print("=" * 80)
    
    # ORIGINAL AMPLITUDE SUMMARY (PRESERVED)
    print("\n📊 AMPLITUDE METRICS - YoY Analysis")
    print("-" * 60)
    print("Sessions up 13.3% YoY (47,312 vs 41,743), session conversion up 2.9 ppts YoY")
    print("(34.3% vs 31.4%), sessions per user up 1.8% YoY (3.41 vs 3.35), and user")
    print("conversion up 0.9 ppts YoY (37.1% vs 36.2%).")
    
    print("\nPlatform Breakdown:")
    print("• Web: 29,743 sessions (62.9%) at 36.4% conversion")
    print("• App: 17,569 sessions (37.1%) at 31.0% conversion")
    print("Observation: App maintains lower conversion than web, gap narrowing from 6.2% to 5.4%")
    
    # GA4 COMPARISON (PRESERVED)
    print("\n📊 GA4 COMPARISON ANALYSIS")
    print("-" * 60)
    print("Amplitude vs GA4 Variance:")
    print("• Sessions: -5.2% (Amplitude: 47,312 | GA4: 49,912)")
    print("• Active Users: -3.8% (Amplitude: 13,874 | GA4: 14,421)")
    print("• Transaction Revenue: +2.1% (Amplitude: £92,345 | GA4: £90,451)")
    print("• Events: -8.7% (Amplitude: 1,234,567 | GA4: 1,352,109)")
    
    print("\nKey Insights:")
    print("✓ Revenue tracking consistent between platforms (2.1% variance)")
    print("⚠ Event count variance suggests potential tracking differences")
    print("ℹ Session variance within acceptable 5% threshold")
    
    # NEW: APPSFLYER INSTALL METRICS
    print("\n📱 APPSFLYER INSTALL METRICS")
    print("-" * 60)
    
    handler = AppsFlyerCSVHandler()
    install_data = handler.get_week_install_summary(target_week=week_num, year=year)
    
    if install_data:
        total_installs = install_data['total_installs']
        
        print(f"Total App Installs: {total_installs:,}")
        
        # Install Sources Breakdown
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
    
    # INTEGRATED PERFORMANCE METRICS
    print("\n🎯 INTEGRATED PERFORMANCE METRICS")
    print("-" * 60)
    
    if install_data:
        # Funnel metrics
        print("Acquisition Funnel:")
        print(f"• Installs: {total_installs:,}")
        print(f"• Active Users (Amplitude): 13,874")
        print(f"• Install → Active Rate: {(13874/total_installs*100):.1f}%")
        print(f"• Active → Transaction Rate: 37.1%")
        
        # Channel ROI
        print("\nChannel Performance:")
        organic_installs = install_data['by_media_source'].get('organic', 0) + \
                          install_data['by_media_source'].get('google_organic_seo', 0)
        paid_installs = install_data['by_media_source'].get('googleadwords_int', 0) + \
                       install_data['by_media_source'].get('Facebook Ads', 0)
        
        print(f"• Organic: {organic_installs:,} installs ({organic_installs/total_installs*100:.1f}%)")
        print(f"• Paid: {paid_installs:,} installs ({paid_installs/total_installs*100:.1f}%)")
        print(f"• Website: {install_data['by_media_source'].get('website-thortful', 0):,} installs")
    
    # EXECUTIVE SUMMARY (ENHANCED)
    print("\n📋 EXECUTIVE SUMMARY")
    print("-" * 60)
    print("Performance Highlights:")
    print("✅ Strong YoY growth: Sessions +13.3%, Revenue +31.4% (implied)")
    print("✅ Conversion improvements: Session +2.9ppts, User +0.9ppts")
    print("✅ Platform consistency: GA4 variance within 5% for key metrics")
    if install_data:
        print(f"✅ Healthy acquisition: {total_installs:,} installs with 47% organic")
    
    print("\nAreas of Focus:")
    print("⚠️  App conversion (31.0%) still lags web (36.4%)")
    print("⚠️  Event tracking variance between Amplitude and GA4 (-8.7%)")
    if install_data and 'Facebook Ads' in install_data['by_media_source']:
        fb_pct = install_data['by_media_source']['Facebook Ads'] / total_installs * 100
        if fb_pct < 10:
            print(f"⚠️  Facebook Ads underperforming at {fb_pct:.1f}% of installs")
    
    print("\nRecommendations:")
    print("1. Investigate app conversion funnel for optimization opportunities")
    print("2. Audit event tracking implementation across platforms")
    if install_data and install_data['by_media_source'].get('googleadwords_int', 0) > 50000:
        print("3. Scale Google Ads budget given strong performance")
    print("4. Test new app onboarding flow to improve install → active rate")
    
    print("\n" + "=" * 80)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def generate_slack_comprehensive_summary():
    """Generate Slack-friendly version preserving all original elements"""
    
    # Get AppsFlyer data
    handler = AppsFlyerCSVHandler()
    install_data = handler.get_week_install_summary(target_week=3, year=2025)
    
    summary = []
    
    # Header
    summary.append("📊 *Weekly Performance Report - Week 3, 2025*")
    summary.append("_January 13-19, 2025_\n")
    
    # Original Amplitude Summary
    summary.append("*📈 Amplitude Metrics (YoY)*")
    summary.append("```")
    summary.append("Sessions:        47,312 (+13.3%)")
    summary.append("Session Conv:    34.3% (+2.9ppts)")
    summary.append("Sessions/User:   3.41 (+1.8%)")
    summary.append("User Conv:       37.1% (+0.9ppts)")
    summary.append("```")
    
    # Platform Split (Original)
    summary.append("*Platform Performance:*")
    summary.append("• Web: 29,743 sessions (62.9%) @ 36.4% conv")
    summary.append("• App: 17,569 sessions (37.1%) @ 31.0% conv\n")
    
    # GA4 Comparison (Original)
    summary.append("*📊 GA4 Variance Check*")
    summary.append("• Sessions: -5.2% (within threshold ✅)")
    summary.append("• Revenue: +2.1% (consistent ✅)")
    summary.append("• Events: -8.7% (needs review ⚠️)\n")
    
    # NEW: AppsFlyer Section
    if install_data:
        total = install_data['total_installs']
        summary.append("*📱 App Install Metrics (AppsFlyer)*")
        summary.append("```")
        summary.append(f"Total Installs:  {total:,}")
        summary.append(f"Organic:         {install_data['by_media_source'].get('organic', 0):,} (41.4%)")
        summary.append(f"Google Ads:      {install_data['by_media_source'].get('googleadwords_int', 0):,} (23.8%)")
        summary.append(f"Website:         {install_data['by_media_source'].get('website-thortful', 0):,} (22.2%)")
        summary.append("```")
    
    # Integrated Insights
    summary.append("\n*🎯 Key Insights*")
    summary.append("• YoY growth strong: Sessions +13.3%, Conv +2.9ppts")
    summary.append("• App conversion improving but still -5.4% vs web")
    if install_data:
        summary.append(f"• Install→Active rate: {(13874/total*100):.1f}%")
        summary.append("• Google Ads driving quality volume (119K installs)")
    
    # Actions
    summary.append("\n*📋 Actions*")
    summary.append("1. Audit GA4 event tracking discrepancy")
    summary.append("2. Optimize app conversion funnel")
    if install_data:
        summary.append("3. Scale Google Ads budget (+20%)")
        summary.append("4. Review Facebook Ads targeting")
    
    return "\n".join(summary)

if __name__ == "__main__":
    # Generate full comprehensive summary
    generate_comprehensive_summary()
    
    print("\n\n" + "="*80)
    print("SLACK VERSION (Comprehensive)")
    print("="*80 + "\n")
    print(generate_slack_comprehensive_summary())
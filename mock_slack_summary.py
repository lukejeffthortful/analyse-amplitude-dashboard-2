#!/usr/bin/env python3
"""Mock Slack-friendly weekly summary with AppsFlyer integration"""

from datetime import datetime
from appsflyer_csv_handler import AppsFlyerCSVHandler

def generate_slack_summary():
    """Generate a concise Slack-friendly summary"""
    
    # Week 3, 2025
    week_num = 3
    year = 2025
    
    # Get AppsFlyer data
    handler = AppsFlyerCSVHandler()
    install_data = handler.get_week_install_summary(target_week=week_num, year=year)
    
    # Format the summary
    summary = []
    
    # Header
    summary.append("📊 *Weekly Performance Report - Week 3, 2025*")
    summary.append("_January 13-19, 2025_\n")
    
    # Key Metrics
    summary.append("*🎯 Key Metrics*")
    summary.append("```")
    summary.append("Revenue:        £145,678 (+31.4% YoY)")
    summary.append("DAU:            45,230 avg (+23.5% YoY)")
    summary.append("WAU:            156,892 (+18.2% YoY)")
    summary.append("Cards Sent:     89,234")
    summary.append("```")
    
    # Install Metrics
    if install_data:
        total_installs = install_data['total_installs']
        summary.append("\n*📱 App Installs*")
        summary.append("```")
        summary.append(f"Total:          {total_installs:,}")
        summary.append(f"Organic:        {install_data['by_media_source'].get('organic', 0):,} (41.4%)")
        summary.append(f"Google Ads:     {install_data['by_media_source'].get('googleadwords_int', 0):,} (23.8%)")
        summary.append(f"Website:        {install_data['by_media_source'].get('website-thortful', 0):,} (22.2%)")
        summary.append(f"Facebook:       {install_data['by_media_source'].get('Facebook Ads', 0):,} (5.6%)")
        summary.append("```")
    
    # Channel Performance
    summary.append("\n*📈 Channel Insights*")
    summary.append("• Google Ads performing strongly - 119K installs")
    summary.append("• Organic growth healthy at 47% of installs")
    summary.append("• Website conversions up 15% WoW")
    summary.append("• Facebook Ads underperforming vs target")
    
    # Key Insights
    summary.append("\n*💡 Key Insights*")
    summary.append("• Install→Active rate: 31.4%")
    summary.append("• Revenue per user: £0.93")
    summary.append("• LTV/CAC ratio: 3.2:1")
    summary.append("• ROAS: 2.8x")
    
    # Alerts
    summary.append("\n*⚠️ Alerts*")
    summary.append("• Install-to-active conversion down 2% WoW")
    summary.append("• Facebook Ads CPA above target by 23%")
    
    # Recommendations
    summary.append("\n*📋 Recommendations*")
    summary.append("1. Increase Google Ads budget by 20%")
    summary.append("2. Review Facebook Ads targeting")
    summary.append("3. Test new website banner placements")
    summary.append("4. Audit onboarding flow for drop-offs")
    
    # Footer
    summary.append(f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    
    return "\n".join(summary)

def generate_executive_summary():
    """Generate an even more concise executive summary"""
    
    # Get AppsFlyer data
    handler = AppsFlyerCSVHandler()
    install_data = handler.get_week_install_summary(target_week=3, year=2025)
    
    summary = []
    
    summary.append("📊 *Week 3 Executive Summary*\n")
    
    summary.append("*Performance:* 🟢 Above Target")
    summary.append("• Revenue: £145.7K (+31% YoY)")
    summary.append("• Users: 156.9K WAU (+18% YoY)")
    summary.append(f"• Installs: {install_data['total_installs']:,}\n")
    
    summary.append("*What's Working:* ✅")
    summary.append("• Google Ads driving 119K quality installs")
    summary.append("• Strong organic growth (41% of installs)")
    summary.append("• Revenue per user up 8%\n")
    
    summary.append("*Needs Attention:* ⚠️")
    summary.append("• Facebook Ads efficiency (-23% vs target)")
    summary.append("• Install→Active conversion declining\n")
    
    summary.append("*Next Week Focus:*")
    summary.append("• Scale Google Ads budget")
    summary.append("• Fix onboarding friction")
    
    return "\n".join(summary)

if __name__ == "__main__":
    print("=== FULL SLACK SUMMARY ===")
    print(generate_slack_summary())
    
    print("\n\n=== EXECUTIVE SUMMARY (ULTRA CONCISE) ===")
    print(generate_executive_summary())
#!/usr/bin/env python3
"""
Show GA4 Acquisition Breakdown
Display the GA4 acquisition data structure and comparison format
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_ga4_acquisition_format():
    """Show the expected GA4 acquisition data format"""
    
    logger.info("📊 GA4 Acquisition Data Breakdown")
    logger.info("="*60)
    
    # Based on our ga4_acquisition_handler.py structure
    logger.info("📋 Data Structure:")
    logger.info("   • total_new_users: Total new users in period")
    logger.info("   • by_channel: New users grouped by first user default channel")
    logger.info("   • by_source: New users grouped by first user source")
    logger.info("   • detailed_data: Row-level data with date/channel/source")
    
    # Show example channels from GA4
    logger.info("\n📈 GA4 Channel Groups:")
    ga4_channels = [
        "Direct",
        "Organic Search", 
        "Paid Search",
        "Organic Social",
        "Paid Social",
        "Email",
        "Affiliates",
        "Referral",
        "Display",
        "Unassigned"
    ]
    
    for channel in ga4_channels:
        logger.info(f"   • {channel}")
    
    # Show reconciliation mapping
    logger.info("\n🔄 Channel Mapping (GA4 → AppsFlyer):")
    mapping = {
        'Direct': ['organic', 'QR_code', 'print'],
        'Paid Search': ['googleadwords_int', 'google_ads'],
        'Organic Search': ['google_organic_seo', 'duckduckgo_organic_seo', 'yahoo_organic_seo', 'bing_organic_seo'],
        'Paid Social': ['Facebook Ads', 'facebook', 'Social_Influencers'],
        'Email': ['emarsys', 'bloomreach', 'transactional_postmark'],
        'Affiliates': ['impactradius_int', 'impact', 'mentionme'],
        'Paid Shopping': ['google_shopping'],
        'Referral': ['website-thortful', 'card-back-thortful'],
        'Display': ['display_ads']
    }
    
    for ga4_channel, af_sources in mapping.items():
        logger.info(f"   {ga4_channel} ← {', '.join(af_sources)}")

def show_reconciliation_example():
    """Show example reconciliation output based on recent data"""
    
    logger.info("\n🔄 Example Reconciliation Report")
    logger.info("="*60)
    
    # Based on our verified Week 35 data
    logger.info("## User Acquisition Reconciliation Report")
    logger.info("**Period:** 2025-08-25 to 2025-08-31 (Week 35)")
    
    logger.info("\n### Summary")
    logger.info("- **AppsFlyer Installs:** 3,125")
    logger.info("- **GA4 New Users:** 1,917 (example from previous test)")
    logger.info("- **Difference:** -1,208 (-38.7%)")
    
    logger.info("\n### Channel Comparison")
    logger.info("| Channel | AppsFlyer | GA4 | Difference | % Diff |")
    logger.info("|---------|-----------|-----|------------|--------|")
    logger.info("| Paid Search | 638 | 73 | -565 | -88.6% |")
    logger.info("| Direct | 1,726 | 1,205 | -521 | -30.2% |")
    logger.info("| Referral | 506 | 0 | -506 | -100.0% |")
    logger.info("| Organic Search | 175 | 1 | -174 | -99.4% |")
    logger.info("| Email | 50 | 43 | -7 | -14.0% |")
    
    logger.info("\n### Key Insights")
    logger.info("- GA4 reports 1,208 fewer new users than AppsFlyer (-38.7%)")
    logger.info("- Paid Search: GA4 is underreporting by 565 users (-88.6%)")
    logger.info("- Referral: GA4 is underreporting by 506 users (-100.0%)")
    logger.info("- Organic Search: GA4 is underreporting by 174 users (-99.4%)")
    
    logger.info("\n### Recommendations")
    logger.info("- Large discrepancy in Paid Search attribution. Verify that all Google Ads")
    logger.info("  campaigns have proper AppsFlyer tracking links")
    logger.info("- GA4 may be missing some app installs. Check that GA4 SDK is properly")
    logger.info("  implemented and firing on all app opens")
    logger.info("- High Direct traffic in GA4 vs AppsFlyer. Consider implementing better")
    logger.info("  campaign tracking parameters")

def show_comprehensive_report_structure():
    """Show the comprehensive report structure"""
    
    logger.info("\n📋 Comprehensive Weekly Report Structure")
    logger.info("="*60)
    
    sections = [
        {
            'title': '🎯 Executive Summary',
            'content': [
                'Key metrics with YoY changes',
                'Cross-platform insights',
                'Recommended actions'
            ]
        },
        {
            'title': '📈 Amplitude Session Analysis', 
            'content': [
                'Sessions by platform (Apps/Web/Combined)',
                'Sessions per user metrics',
                'Conversion rates',
                'YoY comparisons'
            ]
        },
        {
            'title': '📱 AppsFlyer Install Attribution',
            'content': [
                'Total installs with YoY comparison', 
                'Top media sources breakdown',
                'Campaign performance (50+ installs)',
                'Attribution quality metrics'
            ]
        },
        {
            'title': '🔄 Acquisition Platform Reconciliation',
            'content': [
                'AppsFlyer vs GA4 total comparison',
                'Channel-by-channel analysis',
                'Major discrepancies highlighted',
                'Attribution gap insights'
            ]
        },
        {
            'title': '📊 GA4 User Acquisition Details',
            'content': [
                'Total new users',
                'Top acquisition channels',
                'Top traffic sources',
                'Channel performance breakdown'
            ]
        }
    ]
    
    for section in sections:
        logger.info(f"\n{section['title']}")
        for item in section['content']:
            logger.info(f"   • {item}")

def main():
    """Show comprehensive GA4 acquisition breakdown"""
    
    logger.info("🚀 GA4 Acquisition Data Summary")
    logger.info("="*80)
    
    show_ga4_acquisition_format()
    show_reconciliation_example()
    show_comprehensive_report_structure()
    
    logger.info("\n" + "="*80)
    logger.info("📝 The enhanced analyzer provides:")
    logger.info("   • Complete GA4 new user acquisition breakdown by channel and source")
    logger.info("   • Platform reconciliation showing where attribution differs")
    logger.info("   • Unified reporting across Amplitude, AppsFlyer, and GA4")
    logger.info("   • Executive insights for actionable business intelligence")

if __name__ == "__main__":
    main()
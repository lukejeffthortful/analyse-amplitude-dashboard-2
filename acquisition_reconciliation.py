#!/usr/bin/env python3
"""
User Acquisition Reconciliation
Compares AppsFlyer installs with GA4 new users to identify discrepancies
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import logging
from typing import Dict, List, Tuple

from appsflyer_weekly_integration import AppsFlyerWeeklyAnalyzer
from ga4_acquisition_handler import GA4AcquisitionHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AcquisitionReconciler:
    """Reconcile user acquisition data between AppsFlyer and GA4"""
    
    def __init__(self):
        self.appsflyer_analyzer = AppsFlyerWeeklyAnalyzer()
        self.ga4_handler = GA4AcquisitionHandler()
        
        # Channel mapping between AppsFlyer and GA4
        self.channel_mapping = {
            # GA4 Channel -> AppsFlyer sources
            'Direct': ['organic', 'QR_code', 'print'],
            'Paid Search': ['googleadwords_int', 'google_ads'],
            'Organic Search': ['google_organic_seo', 'duckduckgo_organic_seo', 'yahoo_organic_seo', 'bing_organic_seo'],
            'Paid Social': ['Facebook Ads', 'facebook', 'Social_Influencers'],
            'Email': ['emarsys', 'bloomreach', 'transactional_postmark'],
            'Affiliates': ['impactradius_int', 'impact', 'mentionme'],
            'Paid Shopping': ['google_shopping'],
            'Referral': ['website-thortful', 'card-back-thortful'],
            'Display': ['display_ads'],
            'Unassigned': ['unknown', 'other']
        }
        
        # Reverse mapping for AppsFlyer sources to GA4 channels
        self.reverse_mapping = {}
        for ga4_channel, af_sources in self.channel_mapping.items():
            for source in af_sources:
                self.reverse_mapping[source] = ga4_channel
    
    async def reconcile_week(self, year: int, week: int) -> Dict:
        """Reconcile data for a specific ISO week"""
        
        logger.info(f"🔄 Reconciling acquisition data for Week {week}, {year}")
        
        # Get AppsFlyer data
        logger.info("📱 Fetching AppsFlyer data...")
        await self.appsflyer_analyzer.start_session(headless=True)
        
        try:
            # Get week dates
            monday, sunday = self.appsflyer_analyzer.get_iso_week_dates(year, week)
            
            # Export AppsFlyer data
            csv_path = await self.appsflyer_analyzer.export_week_data(year, week)
            if not csv_path:
                raise Exception("Failed to get AppsFlyer data")
            
            appsflyer_data = self.appsflyer_analyzer.analyze_week_data(csv_path)
            
        finally:
            await self.appsflyer_analyzer.close_session()
        
        # Get GA4 data
        logger.info("📊 Fetching GA4 data...")
        ga4_data = self.ga4_handler.get_week_acquisition_data(year, week)
        
        # Perform reconciliation
        reconciliation = self._perform_reconciliation(appsflyer_data, ga4_data, monday, sunday)
        
        return reconciliation
    
    def _perform_reconciliation(self, appsflyer: Dict, ga4: Dict, start_date, end_date) -> Dict:
        """Perform detailed reconciliation between data sources"""
        
        reconciliation = {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'summary': {
                'appsflyer_installs': appsflyer.get('total_installs', 0),
                'ga4_new_users': ga4.get('total_new_users', 0),
                'difference': 0,
                'difference_percent': 0
            },
            'by_channel': {},
            'unmapped_sources': {
                'appsflyer': [],
                'ga4': []
            },
            'insights': [],
            'recommendations': []
        }
        
        # Calculate summary difference
        af_total = reconciliation['summary']['appsflyer_installs']
        ga4_total = reconciliation['summary']['ga4_new_users']
        diff = ga4_total - af_total
        reconciliation['summary']['difference'] = diff
        if af_total > 0:
            reconciliation['summary']['difference_percent'] = (diff / af_total) * 100
        
        # Map AppsFlyer sources to GA4 channels
        af_by_channel = {}
        for source, installs in appsflyer.get('media_sources', {}).items():
            channel = self.reverse_mapping.get(source, 'Unmapped')
            if channel not in af_by_channel:
                af_by_channel[channel] = 0
            af_by_channel[channel] += installs
            
            if channel == 'Unmapped':
                reconciliation['unmapped_sources']['appsflyer'].append({
                    'source': source,
                    'installs': installs
                })
        
        # Compare by channel
        all_channels = set(af_by_channel.keys()) | set(ga4.get('by_channel', {}).keys())
        
        for channel in all_channels:
            af_value = af_by_channel.get(channel, 0)
            ga4_value = ga4.get('by_channel', {}).get(channel, 0)
            
            channel_diff = ga4_value - af_value
            channel_pct = (channel_diff / af_value * 100) if af_value > 0 else 0
            
            reconciliation['by_channel'][channel] = {
                'appsflyer': af_value,
                'ga4': ga4_value,
                'difference': channel_diff,
                'difference_percent': channel_pct
            }
        
        # Generate insights
        reconciliation['insights'] = self._generate_insights(reconciliation)
        reconciliation['recommendations'] = self._generate_recommendations(reconciliation)
        
        return reconciliation
    
    def _generate_insights(self, reconciliation: Dict) -> List[str]:
        """Generate insights from the reconciliation"""
        insights = []
        
        # Overall discrepancy
        summary = reconciliation['summary']
        if abs(summary['difference_percent']) > 5:
            direction = "more" if summary['difference'] > 0 else "fewer"
            insights.append(
                f"GA4 reports {abs(summary['difference']):,} {direction} new users than AppsFlyer "
                f"({summary['difference_percent']:+.1f}%)"
            )
        else:
            insights.append("Overall totals are well-aligned between GA4 and AppsFlyer (within 5%)")
        
        # Channel-specific insights
        major_discrepancies = []
        for channel, data in reconciliation['by_channel'].items():
            if data['appsflyer'] > 50 or data['ga4'] > 50:  # Significant channels
                if abs(data['difference']) > 100 and abs(data['difference_percent']) > 20:
                    major_discrepancies.append({
                        'channel': channel,
                        'difference': data['difference'],
                        'percent': data['difference_percent']
                    })
        
        # Sort by absolute difference
        major_discrepancies.sort(key=lambda x: abs(x['difference']), reverse=True)
        
        for disc in major_discrepancies[:3]:  # Top 3 discrepancies
            direction = "overreporting" if disc['difference'] > 0 else "underreporting"
            insights.append(
                f"{disc['channel']}: GA4 is {direction} by {abs(disc['difference']):,} users "
                f"({disc['percent']:+.1f}%)"
            )
        
        # Unmapped sources
        if reconciliation['unmapped_sources']['appsflyer']:
            total_unmapped = sum(s['installs'] for s in reconciliation['unmapped_sources']['appsflyer'])
            insights.append(f"{total_unmapped:,} AppsFlyer installs from unmapped sources")
        
        return insights
    
    def _generate_recommendations(self, reconciliation: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for missing GA4 tracking
        if reconciliation['summary']['appsflyer_installs'] > reconciliation['summary']['ga4_new_users'] * 1.1:
            recommendations.append(
                "GA4 may be missing some app installs. Check that GA4 SDK is properly implemented "
                "and firing on all app opens"
            )
        
        # Check for attribution discrepancies
        for channel, data in reconciliation['by_channel'].items():
            if channel == 'Direct' and data['ga4'] > data['appsflyer'] * 1.5:
                recommendations.append(
                    f"High Direct traffic in GA4 ({data['ga4']:,}) vs AppsFlyer ({data['appsflyer']:,}). "
                    "Consider implementing better campaign tracking parameters"
                )
            
            if channel == 'Paid Search' and abs(data['difference_percent']) > 30:
                recommendations.append(
                    "Large discrepancy in Paid Search attribution. Verify that all Google Ads "
                    "campaigns have proper AppsFlyer tracking links"
                )
        
        # Unmapped sources
        if reconciliation['unmapped_sources']['appsflyer']:
            sources = [s['source'] for s in reconciliation['unmapped_sources']['appsflyer'][:3]]
            recommendations.append(
                f"Map these AppsFlyer sources to GA4 channels: {', '.join(sources)}"
            )
        
        return recommendations
    
    def format_reconciliation_report(self, reconciliation: Dict) -> str:
        """Format reconciliation into readable report"""
        lines = []
        lines.append("## 🔄 User Acquisition Reconciliation Report")
        lines.append(f"**Period:** {reconciliation['period']}")
        
        # Summary
        lines.append("\n### Summary")
        summary = reconciliation['summary']
        lines.append(f"- **AppsFlyer Installs:** {summary['appsflyer_installs']:,}")
        lines.append(f"- **GA4 New Users:** {summary['ga4_new_users']:,}")
        lines.append(f"- **Difference:** {summary['difference']:+,} ({summary['difference_percent']:+.1f}%)")
        
        # Channel breakdown
        lines.append("\n### Channel Comparison")
        lines.append("| Channel | AppsFlyer | GA4 | Difference | % Diff |")
        lines.append("|---------|-----------|-----|------------|--------|")
        
        # Sort by GA4 volume
        sorted_channels = sorted(
            reconciliation['by_channel'].items(),
            key=lambda x: x[1]['ga4'],
            reverse=True
        )
        
        for channel, data in sorted_channels:
            if data['appsflyer'] > 0 or data['ga4'] > 0:
                lines.append(
                    f"| {channel} | {data['appsflyer']:,} | {data['ga4']:,} | "
                    f"{data['difference']:+,} | {data['difference_percent']:+.1f}% |"
                )
        
        # Insights
        if reconciliation['insights']:
            lines.append("\n### Key Insights")
            for insight in reconciliation['insights']:
                lines.append(f"- {insight}")
        
        # Recommendations
        if reconciliation['recommendations']:
            lines.append("\n### Recommendations")
            for rec in reconciliation['recommendations']:
                lines.append(f"- {rec}")
        
        # Unmapped sources
        if reconciliation['unmapped_sources']['appsflyer']:
            lines.append("\n### Unmapped AppsFlyer Sources")
            for source in reconciliation['unmapped_sources']['appsflyer'][:5]:
                lines.append(f"- {source['source']}: {source['installs']:,} installs")
        
        return "\n".join(lines)

async def test_reconciliation():
    """Test the reconciliation for last week"""
    reconciler = AcquisitionReconciler()
    
    try:
        # Get last week info
        now = datetime.now()
        iso_week = (now - timedelta(days=7)).isocalendar()
        year = iso_week[0]
        week = iso_week[1]
        
        logger.info(f"Testing reconciliation for Week {week}, {year}")
        
        # Run reconciliation
        result = await reconciler.reconcile_week(year, week)
        
        # Format and display report
        report = reconciler.format_reconciliation_report(result)
        
        print("\n" + "="*80)
        print("USER ACQUISITION RECONCILIATION")
        print("="*80)
        print(report)
        print("="*80)
        
        return result
        
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_reconciliation())
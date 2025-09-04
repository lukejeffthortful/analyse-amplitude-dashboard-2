#!/usr/bin/env python3
"""
GA4 User Acquisition Handler
Extracts new users by first user primary channel group for comparison with AppsFlyer
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, OrderBy
)
import pandas as pd
import logging
from ga4_data_handler import GA4DataHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GA4AcquisitionHandler(GA4DataHandler):
    """Specialized handler for GA4 user acquisition data"""
    
    def __init__(self, app_property_id: str = None):
        """Initialize with app property only"""
        self.app_property_id = app_property_id or os.getenv('GA4_APP_PROPERTY_ID')
        if not self.app_property_id:
            raise ValueError("GA4_APP_PROPERTY_ID must be set")
        
        # Initialize parent class with app property
        # Pass dummy web property since parent requires it
        super().__init__(
            web_property_id=self.app_property_id,  # Use app as web to satisfy parent
            app_property_id=self.app_property_id,
            credentials_path=os.getenv('GA4_SERVICE_ACCOUNT_PATH')
        )
        
        # Channel mapping to align with AppsFlyer
        self.channel_mapping = {
            'Organic Search': 'organic_search',
            'Paid Search': 'paid_search',
            'Direct': 'direct',
            'Organic Social': 'organic_social',
            'Paid Social': 'paid_social',
            'Email': 'email',
            'Affiliates': 'affiliates',
            'Referral': 'referral',
            'Display': 'display',
            '(Other)': 'other',
            'Unassigned': 'unassigned'
        }
    
    def get_new_users_by_channel(self, start_date: str, end_date: str) -> Dict:
        """Get new users by first user primary channel group"""
        
        logger.info(f"Fetching GA4 new users for {start_date} to {end_date}")
        
        try:
            request = RunReportRequest(
                property=f"properties/{self.app_property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="firstUserDefaultChannelGroup"),  # Primary acquisition channel
                    Dimension(name="firstUserSource"),  # Source detail
                    Dimension(name="firstUserMedium"),  # Medium detail
                ],
                metrics=[
                    Metric(name="newUsers"),
                    Metric(name="totalUsers"),
                    Metric(name="sessions"),
                ],
                order_bys=[
                    OrderBy(desc=True, metric=OrderBy.MetricOrderBy(metric_name="newUsers"))
                ]
            )
            
            response = self.client.run_report(request)
            
            # Parse response into structured data
            results = {
                'date_range': f"{start_date} to {end_date}",
                'total_new_users': 0,
                'by_channel': {},
                'by_source': {},
                'detailed_data': []
            }
            
            for row in response.rows:
                date = row.dimension_values[0].value
                channel = row.dimension_values[1].value
                source = row.dimension_values[2].value
                medium = row.dimension_values[3].value
                new_users = int(row.metric_values[0].value)
                total_users = int(row.metric_values[1].value)
                sessions = int(row.metric_values[2].value)
                
                # Aggregate totals
                results['total_new_users'] += new_users
                
                # By channel
                if channel not in results['by_channel']:
                    results['by_channel'][channel] = 0
                results['by_channel'][channel] += new_users
                
                # By source
                if source not in results['by_source']:
                    results['by_source'][source] = 0
                results['by_source'][source] += new_users
                
                # Detailed data for analysis
                results['detailed_data'].append({
                    'date': date,
                    'channel': channel,
                    'source': source,
                    'medium': medium,
                    'new_users': new_users,
                    'total_users': total_users,
                    'sessions': sessions
                })
            
            # Sort channels by new users
            results['by_channel'] = dict(
                sorted(results['by_channel'].items(), key=lambda x: x[1], reverse=True)
            )
            
            # Sort sources by new users
            results['by_source'] = dict(
                sorted(results['by_source'].items(), key=lambda x: x[1], reverse=True)
            )
            
            logger.info(f"✓ Retrieved {results['total_new_users']:,} new users from GA4")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch GA4 data: {str(e)}")
            raise
    
    def get_week_acquisition_data(self, year: int, week: int) -> Dict:
        """Get acquisition data for a specific ISO week"""
        # Calculate week dates
        jan4 = datetime(year, 1, 4)
        days_to_monday = jan4.weekday() % 7
        week1_monday = jan4 - timedelta(days=days_to_monday)
        
        target_monday = week1_monday + timedelta(weeks=week - 1)
        target_sunday = target_monday + timedelta(days=6)
        
        start_date = target_monday.strftime('%Y-%m-%d')
        end_date = target_sunday.strftime('%Y-%m-%d')
        
        return self.get_new_users_by_channel(start_date, end_date)
    
    def compare_with_appsflyer(self, ga4_data: Dict, appsflyer_data: Dict) -> Dict:
        """Compare GA4 acquisition data with AppsFlyer installs"""
        
        comparison = {
            'summary': {
                'ga4_new_users': ga4_data.get('total_new_users', 0),
                'appsflyer_installs': appsflyer_data.get('total_installs', 0),
                'difference': 0,
                'difference_percent': 0
            },
            'channel_comparison': {},
            'insights': []
        }
        
        # Calculate summary differences
        diff = comparison['summary']['ga4_new_users'] - comparison['summary']['appsflyer_installs']
        comparison['summary']['difference'] = diff
        if comparison['summary']['appsflyer_installs'] > 0:
            comparison['summary']['difference_percent'] = (diff / comparison['summary']['appsflyer_installs']) * 100
        
        # Map GA4 channels to AppsFlyer sources
        ga4_channels = ga4_data.get('by_channel', {})
        appsflyer_sources = appsflyer_data.get('media_sources', {})
        
        # Channel mapping logic
        channel_map = {
            'Organic Search': ['organic', 'google_organic_seo', 'duckduckgo_organic_seo', 'yahoo_organic_seo'],
            'Paid Search': ['googleadwords_int', 'google_ads'],
            'Paid Social': ['Facebook Ads', 'facebook'],
            'Email': ['emarsys', 'bloomreach', 'transactional_postmark'],
            'Referral': ['website-thortful', 'card-back-thortful'],
            'Direct': ['QR_code', 'print'],
            'Affiliates': ['impactradius_int']
        }
        
        # Compare by channel
        for ga4_channel, ga4_count in ga4_channels.items():
            appsflyer_count = 0
            
            # Sum up corresponding AppsFlyer sources
            if ga4_channel in channel_map:
                for af_source in channel_map[ga4_channel]:
                    appsflyer_count += appsflyer_sources.get(af_source, 0)
            
            comparison['channel_comparison'][ga4_channel] = {
                'ga4': ga4_count,
                'appsflyer': appsflyer_count,
                'difference': ga4_count - appsflyer_count,
                'difference_percent': ((ga4_count - appsflyer_count) / appsflyer_count * 100) if appsflyer_count > 0 else 0
            }
        
        # Generate insights
        comparison['insights'] = self._generate_insights(comparison)
        
        return comparison
    
    def _generate_insights(self, comparison: Dict) -> List[str]:
        """Generate insights from the comparison"""
        insights = []
        
        # Overall difference
        summary = comparison['summary']
        if abs(summary['difference_percent']) > 10:
            direction = "higher" if summary['difference'] > 0 else "lower"
            insights.append(
                f"GA4 reports {abs(summary['difference_percent']):.1f}% {direction} new users than AppsFlyer installs"
            )
        
        # Channel-specific insights
        for channel, data in comparison['channel_comparison'].items():
            if data['ga4'] > 100:  # Only for significant channels
                if abs(data['difference_percent']) > 20:
                    direction = "more" if data['difference'] > 0 else "fewer"
                    insights.append(
                        f"{channel}: GA4 shows {abs(data['difference']):,} {direction} users ({data['difference_percent']:+.1f}%)"
                    )
        
        return insights
    
    def format_acquisition_report(self, ga4_data: Dict, comparison: Optional[Dict] = None) -> str:
        """Format acquisition data into a report section"""
        lines = []
        lines.append("## 📱 GA4 App User Acquisition")
        lines.append(f"**Period:** {ga4_data['date_range']}")
        lines.append(f"**Total New Users:** {ga4_data['total_new_users']:,}")
        
        lines.append("\n### Top Acquisition Channels")
        for channel, count in list(ga4_data['by_channel'].items())[:5]:
            lines.append(f"- **{channel}:** {count:,}")
        
        lines.append("\n### Top Sources")
        for source, count in list(ga4_data['by_source'].items())[:5]:
            lines.append(f"- **{source}:** {count:,}")
        
        if comparison:
            lines.append("\n### GA4 vs AppsFlyer Comparison")
            summary = comparison['summary']
            lines.append(f"- **GA4 New Users:** {summary['ga4_new_users']:,}")
            lines.append(f"- **AppsFlyer Installs:** {summary['appsflyer_installs']:,}")
            lines.append(f"- **Difference:** {summary['difference']:+,} ({summary['difference_percent']:+.1f}%)")
            
            if comparison['insights']:
                lines.append("\n### Key Insights")
                for insight in comparison['insights']:
                    lines.append(f"- {insight}")
        
        return "\n".join(lines)


def test_ga4_acquisition():
    """Test GA4 acquisition data extraction"""
    try:
        handler = GA4AcquisitionHandler()
        
        # Test with last week
        now = datetime.now()
        last_monday = now - timedelta(days=now.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        data = handler.get_new_users_by_channel(
            last_monday.strftime('%Y-%m-%d'),
            last_sunday.strftime('%Y-%m-%d')
        )
        
        logger.info(f"\nGA4 Acquisition Data:")
        logger.info(f"Total new users: {data['total_new_users']:,}")
        logger.info(f"\nTop channels:")
        for channel, count in list(data['by_channel'].items())[:5]:
            logger.info(f"  {channel}: {count:,}")
        
        return data
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return None


if __name__ == "__main__":
    test_ga4_acquisition()
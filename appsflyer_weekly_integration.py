#!/usr/bin/env python3
"""
AppsFlyer Weekly Integration
Integrates with weekly summary to provide YoY install analysis
"""

import os
import json
import base64
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerWeeklyAnalyzer:
    def __init__(self, base_dir="./appsflyer_data"):
        self.username = os.getenv('APPSFLYER_USERNAME')
        self.password = os.getenv('APPSFLYER_PASSWORD')
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create organized folder structure
        self.current_year_dir = self.base_dir / str(datetime.now().year)
        self.previous_year_dir = self.base_dir / str(datetime.now().year - 1)
        self.current_year_dir.mkdir(exist_ok=True)
        self.previous_year_dir.mkdir(exist_ok=True)
        
        self.base_url = "https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&v=NTE5ODM3"
        
        # Session management
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False
    
    def get_iso_week_dates(self, year: int, week: int) -> Tuple[datetime, datetime]:
        """Get Monday and Sunday for an ISO week"""
        # For ISO week calculation, we need to find the Monday of the given week
        # ISO week 1 is the week containing the first Thursday of the year
        
        # Find January 4th (always in week 1)
        jan4 = datetime(year, 1, 4)
        
        # Find the Monday of week 1
        days_to_monday = (jan4.weekday()) % 7
        week1_monday = jan4 - timedelta(days=days_to_monday)
        
        # Calculate target week's Monday
        target_monday = week1_monday + timedelta(weeks=week - 1)
        target_sunday = target_monday + timedelta(days=6)
        
        return target_monday, target_sunday
    
    def get_current_week_info(self) -> Dict:
        """Get current ISO week information"""
        now = datetime.now()
        iso_calendar = now.isocalendar()
        current_year = iso_calendar[0]
        current_week = iso_calendar[1]
        
        # For weekly reports, we want the previous complete week
        if current_week == 1:
            # If it's week 1, go to last week of previous year
            prev_year = current_year - 1
            # December usually has 52 or 53 weeks
            dec31 = datetime(prev_year, 12, 31)
            prev_week = dec31.isocalendar()[1]
        else:
            prev_year = current_year
            prev_week = current_week - 1
        
        return {
            'current_year': current_year,
            'current_week': current_week,
            'analysis_year': prev_year,
            'analysis_week': prev_week
        }
    
    def build_date_url(self, start_date: datetime, end_date: datetime) -> str:
        """Build AppsFlyer URL with encoded date range"""
        query_obj = {
            "view_type": "unified",
            "date": [
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            ],
            "isSsot": False,
            "isPerWidget": False
        }
        
        json_str = json.dumps(query_obj, separators=(',', ':'))
        encoded_query = base64.urlsafe_b64encode(json_str.encode()).decode()
        return f"{self.base_url}&q={encoded_query}&v=LTU%3D"
    
    async def start_session(self, headless: bool = True):
        """Start browser session and login"""
        if self.logged_in:
            return
            
        logger.info("Starting AppsFlyer session...")
        
        playwright = await async_playwright().__aenter__()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            downloads_path=str(self.base_dir)
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Login
        await self.page.goto("https://hq1.appsflyer.com/auth/login")
        await self.page.get_by_role("textbox", name="user-email").fill(self.username)
        await self.page.get_by_role("textbox", name="Password").fill(self.password)
        await self.page.get_by_role("button", name="login").click()
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        self.logged_in = True
        logger.info("✓ AppsFlyer session ready")
    
    async def export_week_data(self, year: int, week: int) -> Optional[Path]:
        """Export data for a specific ISO week"""
        start_date, end_date = self.get_iso_week_dates(year, week)
        
        # Determine save directory
        save_dir = self.current_year_dir if year == datetime.now().year else self.previous_year_dir
        filename = f"week_{week:02d}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        save_path = save_dir / filename
        
        # Check if file already exists
        if save_path.exists():
            logger.info(f"✓ Using existing data: {save_path.relative_to(self.base_dir)}")
            return save_path
        
        try:
            # Navigate to date range
            dashboard_url = self.build_date_url(start_date, end_date)
            await self.page.goto(dashboard_url)
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)
            
            # Export CSV
            await self.page.get_by_test_id("platform-chart:7").get_by_role("button", name="dots icon").click()
            await asyncio.sleep(1)
            
            async with self.page.expect_download() as download_info:
                await self.page.get_by_text("Export CSV").click()
            
            download = await download_info.value
            await download.save_as(save_path)
            
            logger.info(f"✓ Downloaded: {save_path.relative_to(self.base_dir)}")
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to export week {week} of {year}: {str(e)}")
            return None
    
    async def close_session(self):
        """Close browser session"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.logged_in = False
    
    def analyze_week_data(self, csv_path: Path, min_installs: int = 50) -> Dict:
        """Analyze weekly AppsFlyer data with campaign filtering"""
        try:
            df = pd.read_csv(csv_path)
            
            # Basic info
            total_installs = df['installs appsflyer'].sum() if 'installs appsflyer' in df.columns else 0
            date_range = f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else "Unknown"
            
            # Media source analysis
            media_sources = {}
            if 'media-source' in df.columns:
                media_summary = df.groupby('media-source')['installs appsflyer'].sum().sort_values(ascending=False)
                media_sources = media_summary.to_dict()
            
            # Campaign analysis (if available and above threshold)
            campaigns = {}
            if 'campaign' in df.columns and 'installs appsflyer' in df.columns:
                campaign_summary = df.groupby('campaign')['installs appsflyer'].sum()
                # Filter campaigns with significant installs
                significant_campaigns = campaign_summary[campaign_summary >= min_installs].sort_values(ascending=False)
                campaigns = significant_campaigns.to_dict()
            
            return {
                'file_path': csv_path,
                'total_installs': int(total_installs),
                'date_range': date_range,
                'media_sources': media_sources,
                'campaigns': campaigns,
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze {csv_path}: {str(e)}")
            return {'error': str(e), 'file_path': csv_path}
    
    def calculate_yoy_changes(self, current_data: Dict, previous_data: Dict) -> Dict:
        """Calculate year-over-year changes"""
        changes = {
            'total_installs': {
                'current': current_data.get('total_installs', 0),
                'previous': previous_data.get('total_installs', 0),
                'change': 0,
                'percent_change': 0
            },
            'media_sources': {},
            'campaigns': {}
        }
        
        # Total installs change
        current_total = current_data.get('total_installs', 0)
        previous_total = previous_data.get('total_installs', 0)
        changes['total_installs']['change'] = current_total - previous_total
        if previous_total > 0:
            changes['total_installs']['percent_change'] = (changes['total_installs']['change'] / previous_total) * 100
        
        # Media source changes
        current_media = current_data.get('media_sources', {})
        previous_media = previous_data.get('media_sources', {})
        
        all_sources = set(current_media.keys()) | set(previous_media.keys())
        for source in all_sources:
            current_val = current_media.get(source, 0)
            previous_val = previous_media.get(source, 0)
            change = current_val - previous_val
            percent_change = (change / previous_val * 100) if previous_val > 0 else 0
            
            changes['media_sources'][source] = {
                'current': current_val,
                'previous': previous_val,
                'change': change,
                'percent_change': percent_change
            }
        
        # Campaign changes (only for campaigns that appear in either year)
        current_campaigns = current_data.get('campaigns', {})
        previous_campaigns = previous_data.get('campaigns', {})
        
        all_campaigns = set(current_campaigns.keys()) | set(previous_campaigns.keys())
        for campaign in all_campaigns:
            current_val = current_campaigns.get(campaign, 0)
            previous_val = previous_campaigns.get(campaign, 0)
            change = current_val - previous_val
            percent_change = (change / previous_val * 100) if previous_val > 0 else 0
            
            changes['campaigns'][campaign] = {
                'current': current_val,
                'previous': previous_val,
                'change': change,
                'percent_change': percent_change
            }
        
        return changes
    
    async def generate_weekly_appsflyer_summary(self, week_info: Dict = None, headless: bool = True) -> Dict:
        """Generate weekly AppsFlyer summary with YoY comparison"""
        if not week_info:
            week_info = self.get_current_week_info()
        
        analysis_year = week_info['analysis_year']
        analysis_week = week_info['analysis_week']
        previous_year = analysis_year - 1
        
        logger.info(f"📊 Generating AppsFlyer summary for Week {analysis_week}")
        logger.info(f"   Current year: {analysis_year}")
        logger.info(f"   Previous year: {previous_year}")
        
        try:
            await self.start_session(headless=headless)
            
            # Export current year data
            current_csv = await self.export_week_data(analysis_year, analysis_week)
            await asyncio.sleep(2)
            
            # Export previous year data
            previous_csv = await self.export_week_data(previous_year, analysis_week)
            
            if not current_csv or not previous_csv:
                raise Exception("Failed to export required data files")
            
            # Analyze both datasets
            current_analysis = self.analyze_week_data(current_csv)
            previous_analysis = self.analyze_week_data(previous_csv)
            
            # Calculate YoY changes
            yoy_changes = self.calculate_yoy_changes(current_analysis, previous_analysis)
            
            # Create summary
            summary = {
                'week_info': week_info,
                'current_year_data': current_analysis,
                'previous_year_data': previous_analysis,
                'yoy_changes': yoy_changes,
                'files': {
                    'current_year': current_csv,
                    'previous_year': previous_csv
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate AppsFlyer summary: {str(e)}")
            return {'error': str(e)}
        
        finally:
            await self.close_session()
    
    def format_appsflyer_insights(self, summary: Dict) -> str:
        """Format AppsFlyer analysis into readable insights"""
        if 'error' in summary:
            return f"❌ AppsFlyer Analysis Error: {summary['error']}"
        
        insights = []
        insights.append("## 📱 AppsFlyer Install Analysis")
        
        # Week info
        week_info = summary['week_info']
        insights.append(f"**Analysis Period:** Week {week_info['analysis_week']} ({week_info['analysis_year']} vs {week_info['analysis_year']-1})")
        
        # Total installs YoY
        total_changes = summary['yoy_changes']['total_installs']
        change_symbol = "📈" if total_changes['change'] >= 0 else "📉"
        insights.append(f"{change_symbol} **Total Installs:** {total_changes['current']:,} vs {total_changes['previous']:,} ({total_changes['change']:+,}, {total_changes['percent_change']:+.1f}%)")
        
        # Top media sources
        insights.append("\n### Media Source Performance")
        media_changes = summary['yoy_changes']['media_sources']
        
        # Sort by current year volume
        sorted_sources = sorted(media_changes.items(), key=lambda x: x[1]['current'], reverse=True)
        
        for source, data in sorted_sources[:5]:  # Top 5 sources
            if data['current'] > 0 or data['previous'] > 0:  # Only show sources with installs
                change_symbol = "📈" if data['change'] >= 0 else "📉"
                insights.append(f"- **{source}:** {data['current']:,} vs {data['previous']:,} ({data['change']:+,}, {data['percent_change']:+.1f}%) {change_symbol}")
        
        # Significant campaigns (if any)
        campaign_changes = summary['yoy_changes']['campaigns']
        if campaign_changes:
            insights.append("\n### Campaign Performance (50+ installs)")
            
            # Sort by current year volume
            sorted_campaigns = sorted(campaign_changes.items(), key=lambda x: x[1]['current'], reverse=True)
            
            for campaign, data in sorted_campaigns[:3]:  # Top 3 campaigns
                if data['current'] >= 50 or data['previous'] >= 50:  # Show if significant in either year
                    change_symbol = "📈" if data['change'] >= 0 else "📉"
                    insights.append(f"- **{campaign}:** {data['current']:,} vs {data['previous']:,} ({data['change']:+,}, {data['percent_change']:+.1f}%) {change_symbol}")
        
        # Data freshness info
        current_data = summary['current_year_data']
        insights.append(f"\n*Data range: {current_data.get('date_range', 'Unknown')} ({current_data.get('data_points', 0)} data points)*")
        
        return "\n".join(insights)

async def test_weekly_integration():
    """Test the weekly integration"""
    analyzer = AppsFlyerWeeklyAnalyzer()
    
    try:
        # Generate summary for current week
        summary = await analyzer.generate_weekly_appsflyer_summary(headless=False)
        
        if 'error' not in summary:
            # Format insights
            insights = analyzer.format_appsflyer_insights(summary)
            
            logger.info("\n" + "="*60)
            logger.info("APPSFLYER WEEKLY INSIGHTS")
            logger.info("="*60)
            print(insights)
            logger.info("="*60)
            
            # Show file locations
            files = summary['files']
            logger.info(f"\n📁 Data files saved:")
            logger.info(f"   Current: {files['current_year'].relative_to(analyzer.base_dir)}")
            logger.info(f"   Previous: {files['previous_year'].relative_to(analyzer.base_dir)}")
        else:
            logger.error(f"Summary generation failed: {summary['error']}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_weekly_integration())
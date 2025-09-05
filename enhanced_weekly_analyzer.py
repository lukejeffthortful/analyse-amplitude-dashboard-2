#!/usr/bin/env python3
"""
Enhanced Weekly Analyzer
Combines Amplitude sessions, AppsFlyer installs, and GA4 acquisition with reconciliation
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, Optional, Tuple

from amplitude_analyzer import AmplitudeAnalyzer
from appsflyer_weekly_integration import AppsFlyerWeeklyAnalyzer
from ga4_acquisition_handler import GA4AcquisitionHandler
from acquisition_reconciliation import AcquisitionReconciler
from slack_enhanced_poster import SlackEnhancedPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWeeklyAnalyzer:
    """Orchestrates weekly analysis across all platforms with reconciliation"""
    
    def __init__(self):
        self.amplitude_analyzer = AmplitudeAnalyzer()
        self.appsflyer_analyzer = AppsFlyerWeeklyAnalyzer()
        self.ga4_handler = GA4AcquisitionHandler()
        self.reconciler = AcquisitionReconciler()
    
    def get_week_info(self) -> Dict:
        """Get current and analysis week information"""
        now = datetime.now()
        current_iso = now.isocalendar()
        
        # Analysis week is last week
        analysis_date = now - timedelta(days=7)
        analysis_iso = analysis_date.isocalendar()
        
        return {
            'current_year': current_iso[0],
            'current_week': current_iso[1],
            'analysis_year': analysis_iso[0],
            'analysis_week': analysis_iso[1]
        }
    
    async def run_comprehensive_analysis(self, week_info: Optional[Dict] = None) -> Dict:
        """Run analysis across all platforms with reconciliation"""
        
        if not week_info:
            week_info = self.get_week_info()
        
        year = week_info['analysis_year']
        week = week_info['analysis_week']
        
        logger.info(f"🚀 Running comprehensive analysis for Week {week}, {year}")
        
        results = {
            'week_info': week_info,
            'amplitude': None,
            'appsflyer': None,
            'ga4_acquisition': None,
            'reconciliation': None,
            'summary': None
        }
        
        try:
            # 1. Get Amplitude session data
            logger.info("📊 Fetching Amplitude data...")
            amplitude_data = self.amplitude_analyzer.analyze_weekly_data(
                target_week=week,
                target_year=year
            )
            results['amplitude'] = amplitude_data
            
            # 2. Get AppsFlyer install data with YoY comparison
            logger.info("📱 Fetching AppsFlyer data...")
            await self.appsflyer_analyzer.start_session(headless=True)
            
            try:
                appsflyer_summary = await self.appsflyer_analyzer.generate_weekly_appsflyer_summary(
                    week_info=week_info,
                    headless=True
                )
                results['appsflyer'] = appsflyer_summary
            finally:
                await self.appsflyer_analyzer.close_session()
            
            # 3. Get GA4 acquisition data
            logger.info("📊 Fetching GA4 acquisition data...")
            ga4_data = self.ga4_handler.get_week_acquisition_data(year, week)
            results['ga4_acquisition'] = ga4_data
            
            # 4. Run reconciliation between AppsFlyer and GA4
            if 'error' not in appsflyer_summary:
                logger.info("🔄 Running acquisition reconciliation...")
                reconciliation = self.reconciler._perform_reconciliation(
                    appsflyer_summary['current_year_data'],
                    ga4_data,
                    *self.appsflyer_analyzer.get_iso_week_dates(year, week)
                )
                results['reconciliation'] = reconciliation
            
            # 5. Generate executive summary
            results['summary'] = self._generate_executive_summary(results)
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _generate_executive_summary(self, results: Dict) -> Dict:
        """Generate high-level insights from all data sources"""
        
        summary = {
            'key_metrics': {},
            'insights': [],
            'actions': []
        }
        
        # Extract key metrics from Amplitude data (direct structure)
        if results['amplitude'] and 'sessions' in results['amplitude']:
            amp_sessions = results['amplitude']['sessions']
            if 'combined' in amp_sessions and isinstance(amp_sessions['combined'], dict):
                combined_sessions = amp_sessions['combined']
                if 'current' in combined_sessions and 'yoy_change' in combined_sessions:
                    summary['key_metrics']['sessions'] = {
                        'current': combined_sessions['current'],
                        'yoy_change': combined_sessions['yoy_change']
                    }
                elif 'current' in combined_sessions:
                    # Handle case where it's nested under 'value'
                    current_val = combined_sessions['current']
                    if isinstance(current_val, dict) and 'value' in current_val:
                        yoy_data = combined_sessions.get('yoy', {})
                        yoy_change = yoy_data.get('percentage', 0) if isinstance(yoy_data, dict) else 0
                        summary['key_metrics']['sessions'] = {
                            'current': current_val['value'],
                            'yoy_change': yoy_change
                        }
                    else:
                        summary['key_metrics']['sessions'] = {
                            'current': current_val,
                            'yoy_change': 0
                        }
        
        if results['appsflyer'] and 'error' not in results['appsflyer']:
            af_current = results['appsflyer']['current_year_data']['total_installs']
            af_previous = results['appsflyer']['previous_year_data']['total_installs']
            af_yoy = ((af_current - af_previous) / af_previous * 100) if af_previous > 0 else 0
            
            summary['key_metrics']['installs'] = {
                'current': af_current,
                'yoy_change': af_yoy
            }
        
        if results['ga4_acquisition']:
            summary['key_metrics']['ga4_new_users'] = results['ga4_acquisition']['total_new_users']
        
        # Generate cross-platform insights
        if results['reconciliation']:
            diff_pct = results['reconciliation']['summary']['difference_percent']
            if abs(diff_pct) > 10:
                direction = "more" if diff_pct > 0 else "fewer"
                summary['insights'].append(
                    f"GA4 tracking {abs(diff_pct):.1f}% {direction} new users than AppsFlyer - investigate tracking discrepancy"
                )
        
        # Check for growth/decline patterns
        if 'sessions' in summary['key_metrics'] and 'installs' in summary['key_metrics']:
            session_yoy = summary['key_metrics']['sessions']['yoy_change']
            install_yoy = summary['key_metrics']['installs']['yoy_change']
            
            if session_yoy > 5 and install_yoy < -5:
                summary['insights'].append(
                    "Sessions growing while installs declining - focus on user acquisition"
                )
            elif install_yoy > 5 and session_yoy < -5:
                summary['insights'].append(
                    "New users increasing but sessions declining - improve retention"
                )
        
        # Generate recommended actions
        if results['reconciliation'] and results['reconciliation']['recommendations']:
            summary['actions'].extend(results['reconciliation']['recommendations'][:2])
        
        return summary
    
    def format_comprehensive_report(self, results: Dict) -> str:
        """Format all results into a unified report"""
        
        lines = []
        week_info = results['week_info']
        week = week_info['analysis_week']
        year = week_info['analysis_year']
        
        # Get week dates
        monday, sunday = self.appsflyer_analyzer.get_iso_week_dates(year, week)
        
        lines.append(f"# 📊 Comprehensive Weekly Report - Week {week}, {year}")
        lines.append(f"**Period:** {monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}")
        lines.append("")
        
        # Executive Summary
        if results['summary']:
            lines.append("## 🎯 Executive Summary")
            
            # Key metrics
            metrics = results['summary']['key_metrics']
            if 'sessions' in metrics:
                lines.append(f"- **Sessions:** {metrics['sessions']['current']:,} ({metrics['sessions']['yoy_change']:+.1f}% YoY)")
            if 'installs' in metrics:
                lines.append(f"- **App Installs:** {metrics['installs']['current']:,} ({metrics['installs']['yoy_change']:+.1f}% YoY)")
            if 'ga4_new_users' in metrics:
                lines.append(f"- **GA4 New Users:** {metrics['ga4_new_users']:,}")
            
            # Key insights
            if results['summary']['insights']:
                lines.append("\n### Key Insights")
                for insight in results['summary']['insights']:
                    lines.append(f"- {insight}")
            
            # Recommended actions
            if results['summary']['actions']:
                lines.append("\n### Recommended Actions")
                for action in results['summary']['actions']:
                    lines.append(f"- {action}")
            
            lines.append("")
        
        # Amplitude Section
        if results['amplitude']:
            lines.append("## 📈 Amplitude Session Analysis")
            
            amp_data = results['amplitude']
            
            # Sessions
            if 'sessions' in amp_data and 'combined' in amp_data['sessions']:
                combined_sessions = amp_data['sessions']['combined']
                if 'current' in combined_sessions and 'yoy_change' in combined_sessions:
                    lines.append(f"**Sessions:** {combined_sessions['current']:,} (YoY: {combined_sessions['yoy_change']:+.1f}%)")
                elif 'current' in combined_sessions:
                    # Handle nested structure
                    current_val = combined_sessions['current']
                    if isinstance(current_val, dict) and 'value' in current_val:
                        yoy_data = combined_sessions.get('yoy', {})
                        yoy_change = yoy_data.get('percentage', 0) if isinstance(yoy_data, dict) else 0
                        lines.append(f"**Sessions:** {current_val['value']:,} (YoY: {yoy_change:+.1f}%)")
                    else:
                        lines.append(f"**Sessions:** {current_val:,}")
                
                # Platform breakdown
                lines.append("")
                lines.append("**Platform Breakdown:**")
                if 'apps' in amp_data['sessions'] and isinstance(amp_data['sessions']['apps'], dict):
                    apps = amp_data['sessions']['apps']
                    if 'current' in apps and 'yoy_change' in apps:
                        lines.append(f"- Apps: {apps['current']:,} ({apps['yoy_change']:+.1f}% YoY)")
                if 'web' in amp_data['sessions'] and isinstance(amp_data['sessions']['web'], dict):
                    web = amp_data['sessions']['web']
                    if 'current' in web and 'yoy_change' in web:
                        lines.append(f"- Web: {web['current']:,} ({web['yoy_change']:+.1f}% YoY)")
            
            # Sessions per user
            if 'sessions_per_user' in amp_data and 'combined' in amp_data['sessions_per_user']:
                spu = amp_data['sessions_per_user']['combined']
                if 'current' in spu and 'yoy_change' in spu and spu['current'] and spu['yoy_change'] is not None:
                    lines.append(f"**Sessions per User:** {spu['current']:.2f} (YoY: {spu['yoy_change']:+.1f}%)")
            
            # Session conversion
            if 'session_conversion' in amp_data and 'combined' in amp_data['session_conversion']:
                sc = amp_data['session_conversion']['combined']
                if 'current' in sc and sc['current'] is not None:
                    yoy_change = sc.get('yoy_change', 0)
                    lines.append(f"**Session Conversion:** {sc['current']:.1%} (YoY: {yoy_change:+.1f} ppts)")
            
            # User conversion
            if 'user_conversion' in amp_data:
                uc = amp_data['user_conversion']
                if 'combined' in uc and isinstance(uc['combined'], dict):
                    combined_uc = uc['combined']
                    if 'current' in combined_uc:
                        lines.append(f"**User Conversion:** {combined_uc['current']:.1%}")
                elif isinstance(uc, (int, float)):
                    lines.append(f"**User Conversion:** {uc:.1%}")
            
            lines.append("")
        
        # AppsFlyer Section
        if results['appsflyer'] and 'error' not in results['appsflyer']:
            lines.append("## 📱 AppsFlyer Install Attribution")
            af_report = self.appsflyer_analyzer.format_appsflyer_insights(results['appsflyer'])
            # Extract key parts
            for line in af_report.split('\n')[2:]:  # Skip header
                if line.strip() and not line.startswith('##'):
                    lines.append(line)
            lines.append("")
        
        # Acquisition Reconciliation Section
        if results['reconciliation']:
            lines.append("## 🔄 Acquisition Platform Reconciliation")
            recon_report = self.reconciler.format_reconciliation_report(results['reconciliation'])
            # Extract reconciliation details
            for line in recon_report.split('\n')[2:]:  # Skip header
                if line.strip():
                    lines.append(line)
            lines.append("")
        
        # GA4 Acquisition Details
        if results['ga4_acquisition']:
            lines.append("## 📊 GA4 User Acquisition Details")
            lines.append(f"**Total New Users:** {results['ga4_acquisition']['total_new_users']:,}")
            
            lines.append("\n### Top Acquisition Channels")
            for channel, count in list(results['ga4_acquisition']['by_channel'].items())[:5]:
                lines.append(f"- **{channel}:** {count:,}")
            
            lines.append("\n### Top Sources")
            for source, count in list(results['ga4_acquisition']['by_source'].items())[:5]:
                lines.append(f"- **{source}:** {count:,}")
        
        return "\n".join(lines)
    
    def save_report(self, results: Dict, filename: Optional[str] = None) -> Path:
        """Save the comprehensive report to file"""
        
        if not filename:
            week_info = results['week_info']
            filename = f"comprehensive_report_week{week_info['analysis_week']}_{week_info['analysis_year']}.txt"
        
        report = self.format_comprehensive_report(results)
        
        output_path = Path(filename)
        output_path.write_text(report)
        
        logger.info(f"📄 Report saved to: {output_path}")
        
        # Post to Slack if webhook is configured
        slack_url = os.getenv('SLACK_WEBHOOK_URL')
        if slack_url:
            try:
                poster = SlackEnhancedPoster(slack_url)
                if poster.post_to_slack(results):
                    logger.info("✅ Posted to Slack successfully!")
                else:
                    logger.warning("⚠️ Failed to post to Slack")
            except Exception as e:
                logger.error(f"❌ Slack posting error: {str(e)}")
        else:
            logger.info("ℹ️ No Slack webhook configured")
        
        return output_path

async def test_enhanced_analyzer():
    """Test the enhanced weekly analyzer"""
    
    analyzer = EnhancedWeeklyAnalyzer()
    
    try:
        # Run comprehensive analysis for last week
        results = await analyzer.run_comprehensive_analysis()
        
        # Format and display report
        report = analyzer.format_comprehensive_report(results)
        
        print("\n" + "="*80)
        print("COMPREHENSIVE WEEKLY ANALYSIS")
        print("="*80)
        print(report)
        print("="*80)
        
        # Save report
        output_path = analyzer.save_report(results)
        print(f"\n✅ Report saved to: {output_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return None

async def test_amplitude_formatting():
    """Test the Amplitude formatting specifically"""
    
    # Mock results with realistic Amplitude data structure  
    mock_results = {
        'week_info': {'analysis_week': 35, 'analysis_year': 2025},
        'amplitude': {
            'sessions': {
                'combined': {'current': 188923, 'previous': 223299, 'yoy_change': -15.4},
                'apps': {'current': 51960, 'previous': 42781, 'yoy_change': 21.4},
                'web': {'current': 136963, 'previous': 180518, 'yoy_change': -24.1}
            },
            'sessions_per_user': {
                'combined': {'current': 1.54, 'previous': 1.50, 'yoy_change': 2.7}
            },
            'session_conversion': {
                'combined': {'current': 0.195, 'previous': 0.205, 'yoy_change': -1.0}
            },
            'user_conversion': {
                'combined': {'current': 0.285}
            }
        },
        'appsflyer': None,
        'ga4_acquisition': None,
        'reconciliation': None,
        'summary': None
    }
    
    analyzer = EnhancedWeeklyAnalyzer()
    report = analyzer.format_comprehensive_report(mock_results)
    
    print("=== AMPLITUDE FORMATTING TEST ===")
    print(report)
    print("================================")

if __name__ == "__main__":
    asyncio.run(test_enhanced_analyzer())
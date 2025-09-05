#!/usr/bin/env python3
"""
Slack Enhanced Poster
Posts enhanced weekly analysis results to Slack with proper formatting
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackEnhancedPoster:
    """Posts enhanced weekly analysis to Slack"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL must be set")
    
    def format_slack_message(self, results: Dict) -> Dict:
        """Format enhanced results for Slack"""
        
        week_info = results['week_info']
        week = week_info['analysis_week']
        year = week_info['analysis_year']
        
        # Build Slack blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Weekly Analytics Report - Week {week}, {year}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Executive Summary
        if results['summary']:
            summary = results['summary']
            
            exec_text = "*Executive Summary*\n"
            
            # Key metrics
            if 'sessions' in summary['key_metrics']:
                sessions = summary['key_metrics']['sessions']
                exec_text += f"• *Sessions:* {sessions['current']:,} ({sessions['yoy_change']:+.1f}% YoY)\n"
            
            if 'installs' in summary['key_metrics']:
                installs = summary['key_metrics']['installs']
                exec_text += f"• *App Installs:* {installs['current']:,} ({installs['yoy_change']:+.1f}% YoY)\n"
            
            if 'ga4_new_users' in summary['key_metrics']:
                ga4_users = summary['key_metrics']['ga4_new_users']
                exec_text += f"• *GA4 New Users:* {ga4_users:,}\n"
            
            # Key insights
            if summary['insights']:
                exec_text += f"\n*Key Insights:*\n"
                for insight in summary['insights'][:2]:  # Top 2 insights
                    exec_text += f"• {insight}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": exec_text.strip()
                }
            })
            
            blocks.append({"type": "divider"})
        
        # Amplitude Session Analysis Section
        if results['amplitude']:
            amp_data = results['amplitude']
            
            amp_text = f"*📈 Amplitude Session Analytics*\n"
            
            # Handle direct Amplitude data structure (sessions, sessions_per_user, etc. at top level)
            if 'sessions' in amp_data:
                # Sessions
                sessions = amp_data['sessions']
                if 'combined' in sessions and isinstance(sessions['combined'], dict):
                    combined = sessions['combined']
                    if 'current' in combined and 'yoy_change' in combined:
                        amp_text += f"• *Sessions:* {combined['current']:,} (YoY: {combined['yoy_change']:+.1f}%)\n"
                
                # Platform breakdown
                amp_text += f"\n*Platform Breakdown:*\n"
                if 'apps' in sessions and isinstance(sessions['apps'], dict):
                    apps = sessions['apps']
                    if 'current' in apps and 'yoy_change' in apps:
                        amp_text += f"• Apps: {apps['current']:,} ({apps['yoy_change']:+.1f}% YoY)\n"
                if 'web' in sessions and isinstance(sessions['web'], dict):
                    web = sessions['web']
                    if 'current' in web and 'yoy_change' in web:
                        amp_text += f"• Web: {web['current']:,} ({web['yoy_change']:+.1f}% YoY)\n"
            
            # Sessions per user
            if 'sessions_per_user' in amp_data:
                spu = amp_data['sessions_per_user']
                if 'combined' in spu and isinstance(spu['combined'], dict):
                    combined_spu = spu['combined']
                    if 'current' in combined_spu and 'yoy_change' in combined_spu:
                        if combined_spu['current'] and combined_spu['yoy_change'] is not None:
                            amp_text += f"• *Sessions per User:* {combined_spu['current']:.2f} (YoY: {combined_spu['yoy_change']:+.1f}%)\n"
            
            # Session conversion
            if 'session_conversion' in amp_data:
                sc = amp_data['session_conversion']
                if 'combined' in sc and isinstance(sc['combined'], dict):
                    combined_sc = sc['combined']
                    if 'current' in combined_sc and combined_sc['current'] is not None:
                        yoy_change = combined_sc.get('yoy_change', 0)
                        amp_text += f"• *Session Conversion:* {combined_sc['current']:.1%} (YoY: {yoy_change:+.1f} ppts)\n"
            
            # User conversion
            if 'user_conversion' in amp_data:
                uc = amp_data['user_conversion']
                if 'combined' in uc and isinstance(uc['combined'], dict):
                    combined_uc = uc['combined']
                    if 'current' in combined_uc:
                        amp_text += f"• *User Conversion:* {combined_uc['current']:.1%}\n"
                elif isinstance(uc, (int, float)):
                    amp_text += f"• *User Conversion:* {uc:.1%}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": amp_text.strip()
                }
            })
            
            blocks.append({"type": "divider"})
        
        # AppsFlyer Section
        if results['appsflyer'] and 'error' not in results['appsflyer']:
            af_data = results['appsflyer']['current_year_data']
            prev_data = results['appsflyer']['previous_year_data']
            
            af_text = f"*📱 AppsFlyer Install Attribution*\n"
            af_text += f"• *Total Installs:* {af_data['total_installs']:,}\n"
            
            # YoY change
            if prev_data['total_installs'] > 0:
                yoy_change = ((af_data['total_installs'] - prev_data['total_installs']) / prev_data['total_installs']) * 100
                af_text += f"• *YoY Change:* {yoy_change:+.1f}% (vs {prev_data['total_installs']:,} in {year-1})\n"
            
            # Top sources
            af_text += f"\n*Top Media Sources:*\n"
            for source, installs in list(af_data['media_sources'].items())[:3]:
                pct = (installs / af_data['total_installs'] * 100) if af_data['total_installs'] > 0 else 0
                af_text += f"• {source}: {installs:,} ({pct:.1f}%)\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": af_text.strip()
                }
            })
            
            blocks.append({"type": "divider"})
        
        # GA4 Acquisition Section
        if results['ga4_acquisition']:
            ga4_data = results['ga4_acquisition']
            
            ga4_text = f"*📊 GA4 User Acquisition*\n"
            ga4_text += f"• *Total New Users:* {ga4_data['total_new_users']:,}\n"
            
            ga4_text += f"\n*Top Acquisition Channels:*\n"
            for channel, count in list(ga4_data['by_channel'].items())[:3]:
                pct = (count / ga4_data['total_new_users'] * 100) if ga4_data['total_new_users'] > 0 else 0
                ga4_text += f"• {channel}: {count:,} ({pct:.1f}%)\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ga4_text.strip()
                }
            })
            
            blocks.append({"type": "divider"})
        
        # Reconciliation Section
        if results['reconciliation']:
            recon = results['reconciliation']
            
            recon_text = f"*🔄 Attribution Reconciliation*\n"
            recon_text += f"• *AppsFlyer:* {recon['summary']['appsflyer_installs']:,} installs\n"
            recon_text += f"• *GA4:* {recon['summary']['ga4_new_users']:,} new users\n"
            recon_text += f"• *Difference:* {recon['summary']['difference']:+,} ({recon['summary']['difference_percent']:+.1f}%)\n"
            
            # Top discrepancies
            major_discrepancies = []
            for channel, data in recon['by_channel'].items():
                if abs(data['difference']) > 100 and abs(data['difference_percent']) > 20:
                    major_discrepancies.append({
                        'channel': channel,
                        'difference': data['difference'],
                        'percent': data['difference_percent']
                    })
            
            major_discrepancies.sort(key=lambda x: abs(x['difference']), reverse=True)
            
            if major_discrepancies:
                recon_text += f"\n*Major Channel Discrepancies:*\n"
                for disc in major_discrepancies[:2]:
                    direction = "overreporting" if disc['difference'] > 0 else "underreporting"
                    recon_text += f"• {disc['channel']}: GA4 {direction} by {abs(disc['difference']):,} ({disc['percent']:+.1f}%)\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": recon_text.strip()
                }
            })
        
        # Footer
        blocks.extend([
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Enhanced Weekly Analyzer v2.0"
                    }
                ]
            }
        ])
        
        return {
            "text": f"Weekly Analytics Report - Week {week}, {year}",
            "blocks": blocks
        }
    
    def post_to_slack(self, results: Dict) -> bool:
        """Post results to Slack webhook"""
        try:
            import requests
            
            message = self.format_slack_message(results)
            
            logger.info("📤 Posting to test Slack channel...")
            logger.info(f"   Webhook: {self.webhook_url[:50]}...")
            
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Successfully posted to Slack!")
                return True
            else:
                logger.error(f"❌ Slack post failed: {response.status_code} - {response.text}")
                return False
                
        except ImportError:
            logger.warning("⚠️ requests module not available, cannot post to Slack")
            logger.info("📝 Would post this message to Slack:")
            print(json.dumps(self.format_slack_message(results), indent=2))
            return False
        except Exception as e:
            logger.error(f"❌ Slack posting failed: {str(e)}")
            return False

if __name__ == "__main__":
    # This module is typically imported and used by the enhanced_weekly_analyzer
    # For testing the Slack formatting, use the enhanced_weekly_analyzer.py test function
    print("Slack Enhanced Poster - use via enhanced_weekly_analyzer.py for live data testing")
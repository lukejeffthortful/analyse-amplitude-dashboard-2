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

async def simulate_production_run():
    """Simulate a production run with mock data"""
    
    logger.info("🎭 Simulating Production Run with Mock Data")
    logger.info("="*60)
    
    # Create mock results based on our verified data
    mock_results = {
        'week_info': {
            'current_year': 2025,
            'current_week': 36,
            'analysis_year': 2025,
            'analysis_week': 35
        },
        'amplitude': {
            'sessions': {
                'combined': {
                    'current': {'value': 125000},
                    'yoy': {'percentage': 8.5}
                }
            }
        },
        'appsflyer': {
            'current_year_data': {
                'total_installs': 3125,
                'media_sources': {
                    'organic': 1726,
                    'googleadwords_int': 638,
                    'website-thortful': 506,
                    'google_organic_seo': 175,
                    'bloomreach': 50
                }
            },
            'previous_year_data': {
                'total_installs': 4033,
                'media_sources': {
                    'organic': 1675,
                    'googleadwords_int': 1508,
                    'website-thortful': 565,
                    'google_organic_seo': 217,
                    'Facebook Ads': 26
                }
            }
        },
        'ga4_acquisition': {
            'total_new_users': 1917,
            'by_channel': {
                'Direct': 1205,
                'Paid Search': 73,
                'Email': 43,
                'Organic Search': 1,
                'Referral': 0
            },
            'by_source': {
                'google': 1100,
                'direct': 1205,
                'email': 43,
                'thortful.com': 25
            }
        },
        'reconciliation': {
            'summary': {
                'appsflyer_installs': 3125,
                'ga4_new_users': 1917,
                'difference': -1208,
                'difference_percent': -38.7
            },
            'by_channel': {
                'Paid Search': {
                    'appsflyer': 638,
                    'ga4': 73,
                    'difference': -565,
                    'difference_percent': -88.6
                },
                'Direct': {
                    'appsflyer': 1726,
                    'ga4': 1205,
                    'difference': -521,
                    'difference_percent': -30.2
                },
                'Referral': {
                    'appsflyer': 506,
                    'ga4': 0,
                    'difference': -506,
                    'difference_percent': -100.0
                }
            }
        },
        'summary': {
            'key_metrics': {
                'sessions': {
                    'current': 125000,
                    'yoy_change': 8.5
                },
                'installs': {
                    'current': 3125,
                    'yoy_change': -22.5
                },
                'ga4_new_users': 1917
            },
            'insights': [
                "GA4 tracking 38.7% fewer new users than AppsFlyer - investigate tracking discrepancy",
                "Sessions growing (+8.5%) while installs declining (-22.5%) - focus on user acquisition"
            ],
            'actions': [
                "Verify that all Google Ads campaigns have proper AppsFlyer tracking links",
                "Check that GA4 SDK is properly implemented and firing on all app opens"
            ]
        }
    }
    
    # Test Slack posting
    poster = SlackEnhancedPoster()
    success = poster.post_to_slack(mock_results)
    
    if success:
        logger.info("✅ Production simulation successful!")
    else:
        logger.info("📝 Production simulation completed (Slack posting simulated)")
    
    return mock_results

if __name__ == "__main__":
    asyncio.run(simulate_production_run())
#!/usr/bin/env python3
"""
Mock GA4 vs Amplitude Comparative Report Generator
Creates a realistic comparison report to test the output format.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class MockComparativeReport:
    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
    def generate_mock_data(self):
        """Generate realistic mock data for GA4 vs Amplitude comparison"""
        return {
            'week_info': {
                'iso_week': 30,
                'year': 2025,
                'date_range': '2025-07-21 to 2025-07-27'
            },
            'amplitude_metrics': {
                'sessions': {
                    'apps': {
                        'current': 54054,
                        'previous': 40656,
                        'yoy_change': 33.0
                    },
                    'web': {
                        'current': 149215,
                        'previous': 174835,
                        'yoy_change': -14.7
                    },
                    'combined': {
                        'current': 203269,
                        'previous': 215491,
                        'yoy_change': -5.7
                    }
                },
                'session_conversion': {
                    'apps': {
                        'current': 0.1945,
                        'previous': 0.2392,
                        'yoy_change': -4.5
                    },
                    'web': {
                        'current': 0.1866,
                        'previous': 0.1892,
                        'yoy_change': -0.3
                    },
                    'combined': {
                        'current': 0.1887,
                        'previous': 0.1986,
                        'yoy_change': -1.0
                    }
                },
                'metadata': {
                    'source': 'amplitude'
                }
            },
            'ga4_metrics': {
                'sessions': {
                    'apps': {
                        'current': 50620,
                        'previous': 40150,
                        'yoy_change': 26.1
                    },
                    'web': {
                        'current': 134800,
                        'previous': 158200,
                        'yoy_change': -14.8
                    },
                    'combined': {
                        'current': 185420,
                        'previous': 198350,
                        'yoy_change': -6.5
                    }
                },
                'conversions': {
                    'purchase_events': {
                        'current': 2500,
                        'previous': 2300,
                        'yoy_change': 8.7
                    },
                    'revenue': {
                        'current': 85000,
                        'previous': 78000,
                        'yoy_change': 9.0
                    },
                    'conversion_rate': {
                        'current': 0.0135,
                        'previous': 0.0116,
                        'yoy_change': 1.9  # percentage points * 100
                    }
                },
                'metadata': {
                    'source': 'ga4'
                }
            },
            'variance_analysis': {
                'total_sessions': {
                    'amplitude': 203269,
                    'ga4': 185420,
                    'variance_pct': -8.8,
                    'variance_direction': 'ga4_lower'
                },
                'web_sessions': {
                    'amplitude': 149215,
                    'ga4': 134800,
                    'variance_pct': -9.7
                },
                'app_sessions': {
                    'amplitude': 54054,
                    'ga4': 50620,
                    'variance_pct': -6.4
                },
                'insights': {
                    'consistent_variance': True,
                    'typical_range': '6-10% lower for GA4',
                    'growth_trend_alignment': 'similar_yoy_patterns'
                }
            }
        }
    
    def format_amplitude_style_report(self, mock_data):
        """Format the report using original Amplitude format with added GA4 comparison section"""
        week_info = mock_data['week_info']
        amplitude = mock_data['amplitude_metrics']
        ga4 = mock_data['ga4_metrics']
        variance = mock_data['variance_analysis']
        
        # Start with original Amplitude format
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Week {week_info['iso_week']} Analytics Report (MOCK)",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 *{week_info['date_range']}*"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
        
        # Original Amplitude Key Metrics Overview section
        metric_fields = []
        
        # Sessions (Amplitude data)
        sessions_data = amplitude['sessions']['combined']
        sessions_emoji = "🔥" if sessions_data['yoy_change'] > 0 else "⚠️"
        metric_fields.append({
            "type": "mrkdwn",
            "text": f"{sessions_emoji} *Sessions* {'up' if sessions_data['yoy_change'] > 0 else 'down'} {abs(sessions_data['yoy_change']):.1f}% YoY\n`{int(sessions_data['current']):,} vs {int(sessions_data['previous']):,}`"
        })
        
        # Session Conversion (Amplitude data)
        conv_data = amplitude['session_conversion']['combined']
        conv_emoji = "🚀" if conv_data['yoy_change'] > 0 else "📉"
        metric_fields.append({
            "type": "mrkdwn", 
            "text": f"{conv_emoji} *Session CVR* {'up' if conv_data['yoy_change'] > 0 else 'down'} {abs(conv_data['yoy_change']):.1f} ppts YoY\n`{conv_data['current']*100:.1f}% vs {conv_data['previous']*100:.1f}%`"
        })
        
        # Sessions per User (mock data - would come from Amplitude)
        spu_data = {'current': 1.55, 'previous': 1.46, 'yoy_change': 5.7}
        spu_emoji = "🔥" if spu_data['yoy_change'] > 0 else "⚠️"
        metric_fields.append({
            "type": "mrkdwn",
            "text": f"{spu_emoji} *Sessions per User* {'up' if spu_data['yoy_change'] > 0 else 'down'} {abs(spu_data['yoy_change']):.1f}% YoY\n`{spu_data['current']:.2f} vs {spu_data['previous']:.2f}`"
        })
        
        # User Conversion (mock data - would come from Amplitude)
        uc_data = {'current': 0.287, 'previous': 0.287, 'yoy_change': 0.0}
        uc_emoji = "🚀" if uc_data['yoy_change'] > 0 else "📉"
        metric_fields.append({
            "type": "mrkdwn",
            "text": f"{uc_emoji} *User CVR* {'up' if uc_data['yoy_change'] > 0 else 'down'} {abs(uc_data['yoy_change']):.1f} ppts YoY\n`{uc_data['current']*100:.1f}% vs {uc_data['previous']*100:.1f}%`"
        })
        
        # Add metrics section
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 Key Metrics Overview*"
                }
            },
            {
                "type": "section", 
                "fields": metric_fields
            }
        ])
        
        # Original Platform Analysis section
        web_sessions = amplitude['sessions']['web']
        app_sessions = amplitude['sessions']['apps']
        combined_sessions = amplitude['sessions']['combined']
        web_volume_pct = (web_sessions['current'] / combined_sessions['current']) * 100
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎯 Platform Analysis*\n💻 Web {web_volume_pct:.0f}%, 📱 App {(100-web_volume_pct):.0f}% of sessions"
                }
            }
        ])
        
        # Platform details (original Amplitude format)
        web_emoji = "🔥" if web_sessions.get('yoy_change', 0) > 0 else "⚠️"
        app_emoji = "🔥" if app_sessions.get('yoy_change', 0) > 0 else "⚠️"
        web_conv_emoji = "🚀" if amplitude['session_conversion']['web']['yoy_change'] > 0 else "📉"
        app_conv_emoji = "🚀" if amplitude['session_conversion']['apps']['yoy_change'] > 0 else "📉"
        
        platform_fields = [
            {
                "type": "mrkdwn",
                "text": f"{web_emoji} *Web Sessions*\n{'🟢' if web_sessions['yoy_change'] > 0 else '🔴'} {abs(web_sessions['yoy_change']):.1f}% {'up' if web_sessions['yoy_change'] > 0 else 'down'} YoY\n`{int(web_sessions['current']):,} vs {int(web_sessions['previous']):,}`"
            },
            {
                "type": "mrkdwn", 
                "text": f"{app_emoji} *App Sessions*\n{'🟢' if app_sessions['yoy_change'] > 0 else '🔴'} {abs(app_sessions['yoy_change']):.1f}% {'up' if app_sessions['yoy_change'] > 0 else 'down'} YoY\n`{int(app_sessions['current']):,} vs {int(app_sessions['previous']):,}`"
            },
            {
                "type": "mrkdwn",
                "text": f"{web_conv_emoji} *Web Session CVR*\n{'🟢' if amplitude['session_conversion']['web']['yoy_change'] > 0 else '🔴'} {abs(amplitude['session_conversion']['web']['yoy_change']):.1f} ppts {'up' if amplitude['session_conversion']['web']['yoy_change'] > 0 else 'down'} YoY\n`{amplitude['session_conversion']['web']['current']*100:.1f}% vs {amplitude['session_conversion']['web']['previous']*100:.1f}%`"
            },
            {
                "type": "mrkdwn",
                "text": f"{app_conv_emoji} *App Session CVR*\n{'🟢' if amplitude['session_conversion']['apps']['yoy_change'] > 0 else '🔴'} {abs(amplitude['session_conversion']['apps']['yoy_change']):.1f} ppts {'up' if amplitude['session_conversion']['apps']['yoy_change'] > 0 else 'down'} YoY\n`{amplitude['session_conversion']['apps']['current']*100:.1f}% vs {amplitude['session_conversion']['apps']['previous']*100:.1f}%`"
            },
            # Sessions per user (mock additional data)
            {
                "type": "mrkdwn",
                "text": f"🔥 *Web Sessions per User*\n🟢 2.2% up YoY\n`1.42 vs 1.39`"
            },
            {
                "type": "mrkdwn",
                "text": f"🔥 *App Sessions per User*\n🟢 10.6% up YoY\n`1.97 vs 1.78`"
            },
            # User conversion (mock additional data)
            {
                "type": "mrkdwn",
                "text": f"🚀 *Web User CVR*\n🟢 0.2 ppts up YoY\n`26.5% vs 26.4%`"
            },
            {
                "type": "mrkdwn",
                "text": f"📉 *App User CVR*\n🔴 4.7 ppts down YoY\n`38.0% vs 42.6%`"
            }
        ]
        
        blocks.append({
            "type": "section",
            "fields": platform_fields
        })
        
        # NEW: GA4 vs Amplitude Session Comparison section
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 GA4 vs Amplitude Session Comparison*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📈 Total Sessions*\nAmplitude: {amplitude['sessions']['combined']['current']:,}\nGA4: {ga4['sessions']['combined']['current']:,}\nVariance: {abs(variance['total_sessions']['variance_pct']):.1f}% fewer in GA4"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*💻 Web Sessions*\nAmplitude: {amplitude['sessions']['web']['current']:,}\nGA4: {ga4['sessions']['web']['current']:,}\nVariance: {abs(variance['web_sessions']['variance_pct']):.1f}% fewer in GA4"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*📱 App Sessions*\nAmplitude: {amplitude['sessions']['apps']['current']:,}\nGA4: {ga4['sessions']['apps']['current']:,}\nVariance: {abs(variance['app_sessions']['variance_pct']):.1f}% fewer in GA4"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*📈 YoY Trends*\nAmplitude: {amplitude['sessions']['combined']['yoy_change']:.1f}% change\nGA4: {ga4['sessions']['combined']['yoy_change']:.1f}% change\nTrend alignment: Similar patterns"
                    }
                ]
            }
        ])
        
        # Original Google Sheets Export Section (mock data)
        sheets_data = f"Week {week_info['iso_week']} ({week_info['date_range']}):\nSessions ↓{abs(amplitude['sessions']['combined']['yoy_change']):.1f}% YoY | Session CVR ↓{abs(amplitude['session_conversion']['combined']['yoy_change']):.1f}ppts YoY | Sessions/User ↑{spu_data['yoy_change']:.1f}% YoY\nWeb: Sessions ↓{abs(amplitude['sessions']['web']['yoy_change']):.1f}% | Session CVR ↓{abs(amplitude['session_conversion']['web']['yoy_change']):.1f}ppts\nApp: Sessions ↑{amplitude['sessions']['apps']['yoy_change']:.1f}% | Session CVR ↓{abs(amplitude['session_conversion']['apps']['yoy_change']):.1f}ppts"
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Single-Cell Summary (Copy & Paste)*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{sheets_data}```"
                }
            }
        ])
        
        # Original Data Sources Section
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📋 Data Sources*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Dashboard:* <https://app.amplitude.com/analytics/thortful/dashboard/6pqbsp18|Thortful Analytics Dashboard>\n\n*Charts Used:*\n• <https://app.amplitude.com/analytics/thortful/chart/y0ivh3am|Sessions (Current Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/5vbaz782|Sessions (Previous Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/pc9c0crz|Sessions per User (Current Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/3d400y6n|Sessions per User (Previous Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/42c5gcv4|Session Conversion % (Current Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/3t0wgn4i|Session Conversion % (Previous Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/4j2gp4ph|User Conversion %>\n• GA4 Property (Mock Data)"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🧪 *MOCK REPORT* - Testing format with GA4 comparison section | 🤖 *Generated by Enhanced Analytics Bot*"
                    }
                ]
            }
        ])
        
        return {
            "text": f"📊 Week {week_info['iso_week']} Analytics Report (MOCK)",
            "blocks": blocks
        }
    
    def send_mock_report(self):
        """Generate and send mock comparative report to Slack"""
        if not self.slack_webhook_url:
            print("❌ No Slack webhook URL configured")
            return False
        
        # Generate mock data
        mock_data = self.generate_mock_data()
        
        # Format for Slack
        slack_message = self.format_amplitude_style_report(mock_data)
        
        # Send to Slack
        try:
            response = requests.post(self.slack_webhook_url, json=slack_message)
            response.raise_for_status()
            print("✅ Mock comparative report sent to Slack successfully!")
            
            # Also save the mock data for reference
            with open('mock_comparative_analysis.json', 'w') as f:
                json.dump(mock_data, f, indent=2)
            print("📄 Mock data saved to mock_comparative_analysis.json")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send mock report to Slack: {e}")
            return False

def main():
    """Generate and send mock comparative report"""
    print("🧪 Generating mock GA4 vs Amplitude comparative report...")
    
    reporter = MockComparativeReport()
    success = reporter.send_mock_report()
    
    if success:
        print("\n✅ Mock report generation complete!")
        print("📋 Review the Slack report format and provide feedback")
        print("🔍 Key features demonstrated:")
        print("   • Side-by-side session comparison")
        print("   • Variance analysis with percentages")
        print("   • Platform-specific breakdowns")
        print("   • Measurement insights")
    else:
        print("\n❌ Mock report generation failed")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Unified Analyzer
Combines Amplitude and GA4 data handlers to produce comparative analytics reports.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from amplitude_data_handler import AmplitudeDataHandler
from ga4_data_handler import GA4DataHandler

load_dotenv()


class UnifiedAnalyzer:
    """Combines Amplitude and GA4 data sources for comparative analysis"""
    
    def __init__(self):
        self.ga4_enabled = os.getenv('GA4_ENABLED', 'false').lower() == 'true'
        
        # Initialize Amplitude handler
        self.amplitude_handler = AmplitudeDataHandler()
        
        # Initialize GA4 handler if enabled
        self.ga4_handler = None
        if self.ga4_enabled:
            try:
                self.ga4_handler = GA4DataHandler()
                print("✅ GA4 integration enabled and connected")
            except Exception as e:
                print(f"⚠️ GA4 integration disabled due to error: {e}")
                self.ga4_enabled = False
        else:
            print("ℹ️ GA4 integration disabled via configuration")
    
    def get_iso_week_info(self, date):
        """Get ISO week number and year for a given date."""
        iso_year, iso_week, _ = date.isocalendar()
        return iso_year, iso_week
    
    def calculate_variance_analysis(self, amplitude_data: Dict[str, Any], ga4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate variance between Amplitude and GA4 session data"""
        if not amplitude_data or not ga4_data:
            return None
        
        amplitude_sessions = amplitude_data.get('sessions', {})
        ga4_sessions = ga4_data.get('sessions', {})
        
        variance_analysis = {}
        
        for platform in ['apps', 'web', 'combined']:
            amp_current = amplitude_sessions.get(platform, {}).get('current', 0)
            ga4_current = ga4_sessions.get(platform, {}).get('current', 0)
            
            if amp_current > 0:
                variance_pct = ((ga4_current - amp_current) / amp_current) * 100
                variance_direction = 'ga4_higher' if variance_pct > 0 else 'ga4_lower'
            else:
                variance_pct = 0
                variance_direction = 'no_data'
            
            key_name = 'app_sessions' if platform == 'apps' else f'{platform}_sessions'
            variance_analysis[key_name] = {
                'amplitude': amp_current,
                'ga4': ga4_current,
                'variance_pct': round(variance_pct, 1),
                'variance_direction': variance_direction
            }
        
        # Add insights
        variance_analysis['insights'] = {
            'consistent_variance': abs(variance_analysis['web_sessions']['variance_pct']) > 10,
            'typical_range': self._categorize_variance_range(variance_analysis['combined_sessions']['variance_pct']),
            'growth_trend_alignment': self._check_trend_alignment(amplitude_sessions, ga4_sessions)
        }
        
        return variance_analysis
    
    def _categorize_variance_range(self, variance_pct: float) -> str:
        """Categorize variance percentage into descriptive ranges"""
        abs_variance = abs(variance_pct)
        if abs_variance < 5:
            return 'very_close_alignment'
        elif abs_variance < 15:
            return 'moderate_variance'
        elif abs_variance < 30:
            return 'significant_variance'
        else:
            return 'major_measurement_differences'
    
    def _check_trend_alignment(self, amplitude_sessions: Dict, ga4_sessions: Dict) -> str:
        """Check if YoY trends align between platforms"""
        amp_combined_trend = amplitude_sessions.get('combined', {}).get('yoy_change', 0)
        ga4_combined_trend = ga4_sessions.get('combined', {}).get('yoy_change', 0)
        
        # Check if both trends are in the same direction
        if (amp_combined_trend > 0 and ga4_combined_trend > 0) or (amp_combined_trend < 0 and ga4_combined_trend < 0):
            return 'similar_yoy_patterns'
        else:
            return 'divergent_yoy_patterns'
    
    def analyze_weekly_data_unified(self, target_week: int = None, target_year: int = None) -> Dict[str, Any]:
        """Analyze weekly data from both Amplitude and GA4 sources"""
        if not target_week or not target_year:
            # Default to previous week
            today = datetime.now()
            last_week = today - timedelta(days=7)
            target_year, target_week = self.get_iso_week_info(last_week)
        
        print(f"🔍 Analyzing unified data for Week {target_week} ({target_year})")
        
        # Get Amplitude data
        amplitude_data = self.amplitude_handler.get_weekly_yoy_data(target_week, target_year)
        
        # Get GA4 data if enabled
        ga4_data = None
        if self.ga4_enabled and self.ga4_handler:
            try:
                ga4_data = self.ga4_handler.get_weekly_yoy_data(target_week, target_year)
            except Exception as e:
                print(f"⚠️ GA4 data fetch failed: {e}")
                ga4_data = None
        
        # Calculate variance analysis
        variance_analysis = None
        if ga4_data:
            variance_analysis = self.calculate_variance_analysis(amplitude_data, ga4_data)
        
        return {
            'week_info': {
                'iso_week': target_week,
                'year': target_year,
                'date_range': amplitude_data['metadata']['date_range']
            },
            'amplitude_metrics': amplitude_data,
            'ga4_metrics': ga4_data,
            'variance_analysis': variance_analysis,
            'comparison_enabled': self.ga4_enabled and ga4_data is not None
        }
    
    def generate_comparative_summary(self, unified_data: Dict[str, Any]) -> str:
        """Generate text summary with comparative analysis"""
        week_info = unified_data['week_info']
        amplitude = unified_data['amplitude_metrics']
        ga4 = unified_data.get('ga4_metrics')
        variance = unified_data.get('variance_analysis')
        
        # Start with standard Amplitude summary
        summary = f"Week {week_info['iso_week']} Analysis ({week_info['date_range']}):\n\n"
        
        # Amplitude metrics (preserve original format)
        if amplitude.get('sessions'):
            sessions_data = amplitude['sessions']['combined']
            sessions_direction = "up" if sessions_data['yoy_change'] > 0 else "down"
            summary += f"Sessions {sessions_direction} {abs(sessions_data['yoy_change']):.1f}% YoY ({int(sessions_data['current']):,} vs {int(sessions_data['previous']):,})"
        
        if amplitude.get('session_conversion'):
            conv_data = amplitude['session_conversion']['combined']
            conv_direction = "up" if conv_data['yoy_change'] > 0 else "down"
            summary += f", session conversion {conv_direction} {abs(conv_data['yoy_change']):.1f} ppts YoY ({conv_data['current']*100:.1f}% vs {conv_data['previous']*100:.1f}%)"
        
        if amplitude.get('sessions_per_user'):
            spu_data = amplitude['sessions_per_user']['combined']
            spu_direction = "up" if spu_data['yoy_change'] > 0 else "down"
            summary += f", sessions per user {spu_direction} {abs(spu_data['yoy_change']):.1f}% YoY ({spu_data['current']:.2f} vs {spu_data['previous']:.2f})"
        
        if amplitude.get('user_conversion') and isinstance(amplitude['user_conversion'], dict):
            if amplitude['user_conversion'].get('combined') and isinstance(amplitude['user_conversion']['combined'], dict):
                uc_data = amplitude['user_conversion']['combined']
                if uc_data.get('yoy_change') is not None:
                    uc_direction = "up" if uc_data['yoy_change'] > 0 else "down"
                    summary += f", and user conversion {uc_direction} {abs(uc_data['yoy_change']):.1f} ppts YoY ({uc_data['current']*100:.1f}% vs {uc_data['previous']*100:.1f}%)"
        
        summary += ". \n\n"
        
        # Platform Analysis (Amplitude data)
        if amplitude.get('sessions'):
            web_sessions = amplitude['sessions']['web']
            app_sessions = amplitude['sessions']['apps']
            combined_sessions = amplitude['sessions']['combined']
            
            web_volume_pct = (web_sessions['current'] / combined_sessions['current']) * 100
            app_volume_pct = (app_sessions['current'] / combined_sessions['current']) * 100
            
            summary += f"Platform Analysis:\nWeb {web_volume_pct:.0f}%, App {app_volume_pct:.0f}% of sessions\n\n"
            
            summary += f"Web: sessions {('up' if web_sessions['yoy_change'] > 0 else 'down')} {abs(web_sessions['yoy_change']):.1f}% YoY ({int(web_sessions['current']):,} vs {int(web_sessions['previous']):,})"
            
            if amplitude.get('session_conversion'):
                web_conv = amplitude['session_conversion']['web']
                summary += f", conversion {('up' if web_conv['yoy_change'] > 0 else 'down')} {abs(web_conv['yoy_change']):.1f} ppts YoY ({web_conv['current']*100:.1f}% vs {web_conv['previous']*100:.1f}%)"
            summary += "\n"
            
            summary += f"Apps: sessions {('up' if app_sessions['yoy_change'] > 0 else 'down')} {abs(app_sessions['yoy_change']):.1f}% YoY ({int(app_sessions['current']):,} vs {int(app_sessions['previous']):,})"
            
            if amplitude.get('session_conversion'):
                app_conv = amplitude['session_conversion']['apps']
                summary += f", conversion {('up' if app_conv['yoy_change'] > 0 else 'down')} {abs(app_conv['yoy_change']):.1f} ppts YoY ({app_conv['current']*100:.1f}% vs {app_conv['previous']*100:.1f}%)"
            summary += "\n"
        
        # Sessions per user details
        if amplitude.get('sessions_per_user'):
            web_spu = amplitude['sessions_per_user']['web']
            app_spu = amplitude['sessions_per_user']['apps']
            
            summary += f"\nSessions per user: Web {('up' if web_spu['yoy_change'] > 0 else 'down')} {abs(web_spu['yoy_change']):.1f}% YoY ({web_spu['current']:.2f} vs {web_spu['previous']:.2f}), App {('up' if app_spu['yoy_change'] > 0 else 'down')} {abs(app_spu['yoy_change']):.1f}% YoY ({app_spu['current']:.2f} vs {app_spu['previous']:.2f})"
        
        # User conversion details
        if amplitude.get('user_conversion') and isinstance(amplitude['user_conversion'], dict):
            if amplitude['user_conversion'].get('web') and isinstance(amplitude['user_conversion']['web'], dict):
                web_uc = amplitude['user_conversion']['web']
                app_uc = amplitude['user_conversion']['apps']
                
                summary += f"\nUser conversion: Web {('up' if web_uc['yoy_change'] > 0 else 'down')} {abs(web_uc['yoy_change']):.1f} ppts YoY ({web_uc['current']*100:.1f}% vs {web_uc['previous']*100:.1f}%), App {('up' if app_uc['yoy_change'] > 0 else 'down')} {abs(app_uc['yoy_change']):.1f} ppts YoY ({app_uc['current']*100:.1f}% vs {app_uc['previous']*100:.1f}%)"
        
        # Add GA4 comparison if available
        if ga4 and variance:
            summary += f"\n\nGA4 vs Amplitude Session Comparison:\n"
            summary += f"Total Sessions: Amplitude {int(amplitude['sessions']['combined']['current']):,}, GA4 {int(ga4['sessions']['combined']['current']):,} ({'+' if variance['combined_sessions']['variance_pct'] > 0 else ''}{variance['combined_sessions']['variance_pct']:.1f}% variance)\n"
            summary += f"Web Sessions: Amplitude {int(amplitude['sessions']['web']['current']):,}, GA4 {int(ga4['sessions']['web']['current']):,} ({'+' if variance['web_sessions']['variance_pct'] > 0 else ''}{variance['web_sessions']['variance_pct']:.1f}% variance)\n"
            summary += f"App Sessions: Amplitude {int(amplitude['sessions']['apps']['current']):,}, GA4 {int(ga4['sessions']['apps']['current']):,} ({'+' if variance['app_sessions']['variance_pct'] > 0 else ''}{variance['app_sessions']['variance_pct']:.1f}% variance)"
        
        return summary


def main():
    """Test unified analyzer"""
    try:
        analyzer = UnifiedAnalyzer()
        
        # Test unified analysis
        unified_data = analyzer.analyze_weekly_data_unified()
        
        print("\n" + "="*60)
        print("UNIFIED ANALYSIS RESULTS")
        print("="*60)
        
        # Generate and display summary
        summary = analyzer.generate_comparative_summary(unified_data)
        print(summary)
        
        # Save detailed results
        with open('unified_analysis.json', 'w') as f:
            json.dump(unified_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed analysis saved to unified_analysis.json")
        print("✅ UnifiedAnalyzer test completed successfully!")
        
    except Exception as e:
        print(f"❌ UnifiedAnalyzer test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
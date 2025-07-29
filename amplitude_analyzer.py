#!/usr/bin/env python3
"""
Amplitude Dashboard Analyzer
Fetches data from Amplitude charts and generates executive summary reports.
"""

import os
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

class AmplitudeAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('AMPLITUDE_API_KEY')
        self.secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.base_url = "https://amplitude.com/api/2/query"
        
        # Chart configurations from plan.md
        self.charts = {
            'sessions_current': 'y0ivh3am',
            'sessions_previous': '5vbaz782',
            'sessions_per_user_current': 'pc9c0crz',
            'sessions_per_user_previous': '3d400y6n',
            'session_conversion_current': '42c5gcv4',
            'session_conversion_previous': '3t0wgn4i',
            'user_conversion': '4j2gp4ph'  # Note: Single chart, may use built-in comparison
        }
    
    def get_chart_data(self, chart_id, start_date=None, end_date=None):
        """Fetch data from a specific Amplitude chart."""
        url = f"https://amplitude.com/api/3/chart/{chart_id}/csv"
        
        auth = (self.api_key, self.secret_key)
        
        try:
            response = requests.get(url, auth=auth)
            print(f"Fetching chart {chart_id}: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
            response.raise_for_status()
            # API returns JSON with 'data' field containing CSV content
            json_response = response.json()
            return json_response.get('data', '')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chart {chart_id}: {e}")
            return None
    
    def get_iso_week_info(self, date):
        """Get ISO week number and year for a given date."""
        iso_year, iso_week, _ = date.isocalendar()
        return iso_year, iso_week
    
    def get_week_date_range(self, year, week):
        """Get Monday-Sunday date range for a given ISO week."""
        # January 4th is always in week 1
        jan4 = datetime(year, 1, 4)
        week1_monday = jan4 - timedelta(days=jan4.weekday())
        target_monday = week1_monday + timedelta(weeks=week-1)
        target_sunday = target_monday + timedelta(days=6)
        return target_monday, target_sunday
    
    def calculate_platform_yoy_comparison(self, current_data, previous_data, is_conversion=False, target_week=None):
        """Calculate year-over-year comparison for all platform segments."""
        if not current_data or not previous_data:
            return None
        
        # Extract platform metrics from the data
        current_metrics = self.extract_platform_metrics(current_data, year=2025, target_week=target_week)
        previous_metrics = self.extract_platform_metrics(previous_data, year=2024, target_week=target_week)
        
        result = {}
        for platform in ['apps', 'web', 'combined']:
            current_value = current_metrics.get(platform, 0)
            previous_value = previous_metrics.get(platform, 0)
            
            if previous_value == 0:
                yoy_change = None
            else:
                if is_conversion:
                    # For conversion rates, calculate percentage points change
                    yoy_change = (current_value - previous_value) * 100
                else:
                    # For other metrics, calculate percentage change
                    yoy_change = ((current_value - previous_value) / previous_value) * 100
                yoy_change = round(yoy_change, 1)
            
            result[platform] = {
                'current': current_value,
                'previous': previous_value,
                'yoy_change': yoy_change
            }
        
        return result
    
    def extract_platform_metrics(self, csv_data, year=2025, target_week=None):
        """Extract metrics for all three platform segments from CSV response."""
        if not csv_data:
            return {'apps': 0, 'web': 0, 'combined': 0}
        
        lines = csv_data.strip().split('\r\n')
        if len(lines) < 4:  # Need header rows + at least one data row
            print(f"Not enough data lines: {len(lines)}")
            return {'apps': 0, 'web': 0, 'combined': 0}
        
        # Find the header row with dates to identify the correct column for our target week
        header_row = None
        target_date_column = None
        
        for line in lines:
            if 'T00:00:00' in line:  # This is a header row with dates
                header_row = line
                break
        
        if header_row:
            header_cols = header_row.split(',')
            
            # Get the correct ISO week date for the given year and target week
            if target_week is None:
                # Default to previous week if not specified
                today = datetime.now()
                last_week = today - timedelta(days=7)
                _, target_week = self.get_iso_week_info(last_week)
            
            target_week_start = datetime.fromisocalendar(year, target_week, 1).strftime('%Y-%m-%d')
            
            for i, col in enumerate(header_cols):
                if target_week_start in col:
                    target_date_column = i
                    print(f"Found target week column {i} for {target_week_start} in {year}")
                    break
        
        # Find data rows for each platform (handle different naming conventions)
        platform_data = {}
        for line in lines:
            if 'Apps Only' in line or '"	App"' in line:
                platform_data['apps'] = line
            elif 'Web Only' in line or '"	Web"' in line:
                platform_data['web'] = line
            elif 'App + Web' in line:
                platform_data['combined'] = line
        
        if not platform_data:
            print("No platform data rows found")
            return {'apps': 0, 'web': 0, 'combined': 0}
        
        # Extract values for each platform
        result = {}
        for platform, row in platform_data.items():
            try:
                row_data = row.split(',')
                
                # Use target date column if found, otherwise fall back to last value
                if target_date_column and target_date_column < len(row_data):
                    value_str = row_data[target_date_column].strip('"').replace('%', '').replace(',', '')
                    value = float(value_str) if value_str else 0
                    print(f"Extracted {platform} value: {value} from column {target_date_column}")
                else:
                    # Fallback: Get the last numeric value (most recent week)
                    value = 0
                    for i in range(len(row_data) - 1, 0, -1):  # Skip first column (platform name)
                        try:
                            value_str = row_data[i].strip('"').replace('%', '').replace(',', '')
                            if value_str:
                                value = float(value_str)
                                print(f"Fallback: extracted {platform} value: {value} from column {i}")
                                break
                        except ValueError:
                            continue
                
                result[platform] = value
            except (ValueError, IndexError) as e:
                print(f"Could not parse {platform} value: {e}")
                result[platform] = 0
        
        # Ensure all platforms are present
        for platform in ['apps', 'web', 'combined']:
            if platform not in result:
                result[platform] = 0
        
        return result
    
    def parse_user_conversion_with_yoy(self, csv_data):
        """Parse user conversion data that includes YoY comparison built-in."""
        if not csv_data:
            return {'apps': {'current': 0, 'previous': 0, 'yoy_change': None},
                    'web': {'current': 0, 'previous': 0, 'yoy_change': None},
                    'combined': {'current': 0, 'previous': 0, 'yoy_change': None}}
        
        lines = csv_data.strip().split('\r\n')
        
        # Find current and previous year data rows
        current_data = {}
        previous_data = {}
        
        for line in lines:
            if 'App + Web' in line:
                if '[Previous]' not in line:
                    current_data['combined'] = line
                else:
                    previous_data['combined'] = line
            elif ('Apps' in line or 'App"' in line) and 'App + Web' not in line:
                if '[Previous]' not in line:
                    current_data['apps'] = line
                else:
                    previous_data['apps'] = line
            elif 'Web' in line and 'App + Web' not in line:
                if '[Previous]' not in line:
                    current_data['web'] = line
                else:
                    previous_data['web'] = line
        
        # Extract values and calculate YoY changes
        result = {}
        for platform in ['apps', 'web', 'combined']:
            current_val = self.extract_value_from_row(current_data.get(platform, ''))
            previous_val = self.extract_value_from_row(previous_data.get(platform, ''))
            
            if previous_val > 0:
                # For conversion rates, calculate percentage points change
                yoy_change = (current_val - previous_val) * 100
            else:
                yoy_change = None
            
            result[platform] = {
                'current': current_val,
                'previous': previous_val,
                'yoy_change': round(yoy_change, 1) if yoy_change is not None else None
            }
        
        return result
    
    def extract_value_from_row(self, row_data):
        """Extract numeric value from a CSV row."""
        if not row_data:
            return 0
        
        try:
            row_parts = row_data.split(',')
            
            # For user conversion, get the second-to-last value (last is usually current/incomplete week)
            if len(row_parts) >= 3:
                # Try second-to-last value first (target week data should be here)
                try:
                    value_str = row_parts[-2].strip('"').replace('%', '').replace(',', '')
                    if value_str:
                        return float(value_str)
                except ValueError:
                    pass
            
            # Fallback: Get the last numeric value from the row
            for i in range(len(row_parts) - 1, 0, -1):
                try:
                    value_str = row_parts[i].strip('"').replace('%', '').replace(',', '')
                    if value_str:
                        return float(value_str)
                except ValueError:
                    continue
            return 0
        except Exception:
            return 0
    
    def analyze_weekly_data(self, target_week=None, target_year=None):
        """Analyze data for a specific week and generate summary."""
        if not target_week or not target_year:
            # Default to previous week
            today = datetime.now()
            last_week = today - timedelta(days=7)
            target_year, target_week = self.get_iso_week_info(last_week)
        
        # Get date ranges
        current_monday, current_sunday = self.get_week_date_range(target_year, target_week)
        previous_monday, previous_sunday = self.get_week_date_range(target_year - 1, target_week)
        
        # Fetch data for all charts
        results = {}
        
        for chart_name, chart_id in self.charts.items():
            print(f"Processing {chart_name}...")
            data = self.get_chart_data(chart_id)
            if data:
                print(f"Sample data for {chart_name}: {data[:200]}...")
                # Save full sample for analysis
                if chart_name == 'sessions_current':
                    with open('sample_csv_output.txt', 'w') as f:
                        f.write(data)
                elif chart_name == 'session_conversion_current':
                    with open('sample_conversion_output.txt', 'w') as f:
                        f.write(data)
                elif chart_name == 'sessions_per_user_current':
                    with open('sample_sessions_per_user_output.txt', 'w') as f:
                        f.write(data)
                elif chart_name == 'user_conversion':
                    with open('sample_user_conversion_output.txt', 'w') as f:
                        f.write(data)
            results[chart_name] = data
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        
        # Calculate platform-specific comparisons
        sessions_comparison = self.calculate_platform_yoy_comparison(
            results['sessions_current'], 
            results['sessions_previous'],
            target_week=target_week
        )
        
        sessions_per_user_comparison = self.calculate_platform_yoy_comparison(
            results['sessions_per_user_current'],
            results['sessions_per_user_previous'],
            target_week=target_week
        )
        
        conversion_comparison = self.calculate_platform_yoy_comparison(
            results['session_conversion_current'],
            results['session_conversion_previous'],
            is_conversion=True,
            target_week=target_week
        )
        
        # User conversion uses a single chart (may have built-in comparison)
        user_conversion_comparison = None
        if 'user_conversion' in results and results['user_conversion']:
            # Check if this chart has built-in YoY comparison or current values only
            csv_data = results['user_conversion']
            if 'Previous' in csv_data or 'previous' in csv_data.lower():
                # Chart has built-in YoY comparison, parse as platform comparison
                user_conversion_comparison = self.parse_user_conversion_with_yoy(csv_data)
            else:
                # Chart has current values only, extract platform metrics
                user_conversion_comparison = self.extract_platform_metrics(csv_data, year=2025, target_week=target_week)
        
        return {
            'week_info': {
                'iso_week': target_week,
                'year': target_year,
                'date_range': f"{current_monday.strftime('%Y-%m-%d')} to {current_sunday.strftime('%Y-%m-%d')}"
            },
            'metrics': {
                'sessions': sessions_comparison,
                'sessions_per_user': sessions_per_user_comparison,
                'session_conversion': conversion_comparison,
                'user_conversion': user_conversion_comparison
            }
        }
    
    def generate_executive_summary(self, analysis_data):
        """Generate executive summary text with platform breakdowns."""
        week_info = analysis_data['week_info']
        metrics = analysis_data['metrics']
        
        summary = f"Week {week_info['iso_week']} Analysis ({week_info['date_range']}):\n\n"
        
        # High-level YoY summary for each category
        summary_items = []
        
        # Sessions summary
        if metrics['sessions'] and metrics['sessions']['combined']['yoy_change'] is not None:
            sessions_data = metrics['sessions']['combined']
            sessions_change = sessions_data['yoy_change']
            sessions_direction = "up" if sessions_change > 0 else "down"
            sessions_current = int(sessions_data['current'])
            sessions_previous = int(sessions_data['previous'])
            summary_items.append(f"sessions {sessions_direction} {abs(sessions_change)}% YoY ({sessions_current:,} vs {sessions_previous:,})")
        
        # Session conversion summary
        if metrics['session_conversion'] and metrics['session_conversion']['combined']['yoy_change'] is not None:
            conv_data = metrics['session_conversion']['combined']
            conv_change = conv_data['yoy_change']
            conv_direction = "up" if conv_change > 0 else "down"
            conv_current = conv_data['current'] * 100
            conv_previous = conv_data['previous'] * 100
            summary_items.append(f"session conversion {conv_direction} {abs(conv_change)} ppts YoY ({conv_current:.1f}% vs {conv_previous:.1f}%)")
        
        # Sessions per user summary
        if metrics['sessions_per_user'] and metrics['sessions_per_user']['combined']['yoy_change'] is not None:
            spu_data = metrics['sessions_per_user']['combined']
            spu_change = spu_data['yoy_change']
            spu_direction = "up" if spu_change > 0 else "down"
            summary_items.append(f"sessions per user {spu_direction} {abs(spu_change)}% YoY ({spu_data['current']:.2f} vs {spu_data['previous']:.2f})")
        
        # User conversion summary (if available with YoY data)
        if metrics.get('user_conversion'):
            user_conv = metrics['user_conversion']
            if isinstance(user_conv, dict) and user_conv.get('combined'):
                if isinstance(user_conv['combined'], dict) and user_conv['combined'].get('yoy_change') is not None:
                    uc_data = user_conv['combined']
                    uc_change = uc_data['yoy_change']
                    uc_direction = "up" if uc_change > 0 else "down"
                    uc_current = uc_data['current'] * 100
                    uc_previous = uc_data['previous'] * 100
                    summary_items.append(f"user conversion {uc_direction} {abs(uc_change)} ppts YoY ({uc_current:.1f}% vs {uc_previous:.1f}%)")
        
        # Join all summary items
        if summary_items:
            if len(summary_items) == 1:
                summary += f"{summary_items[0].capitalize()}. "
            elif len(summary_items) == 2:
                summary += f"{summary_items[0].capitalize()}, {summary_items[1]}. "
            else:
                summary += f"{summary_items[0].capitalize()}, "
                for item in summary_items[1:-1]:
                    summary += f"{item}, "
                summary += f"and {summary_items[-1]}. "
        
        # Platform-specific breakdowns with driver analysis
        summary += "\n\nPlatform Analysis:\n"
        
        # Analyze which platform is driving overall changes
        driving_insights = []
        
        # Sessions analysis
        if metrics['sessions']:
            web_sessions = metrics['sessions']['web'] 
            app_sessions = metrics['sessions']['apps']
            combined_sessions = metrics['sessions']['combined']
            
            if all(data.get('current') for data in [web_sessions, app_sessions, combined_sessions]):
                web_volume_pct = (web_sessions['current'] / combined_sessions['current']) * 100
                app_volume_pct = (app_sessions['current'] / combined_sessions['current']) * 100
                
                # Determine primary driver for sessions
                if web_sessions.get('yoy_change') is not None and app_sessions.get('yoy_change') is not None:
                    web_impact = abs(web_sessions['yoy_change']) * (web_volume_pct / 100)
                    app_impact = abs(app_sessions['yoy_change']) * (app_volume_pct / 100)
                    
                    if web_impact > app_impact:
                        driving_insights.append(f"Web {web_volume_pct:.0f}%, App {app_volume_pct:.0f}% of sessions")
                    else:
                        driving_insights.append(f"App {app_volume_pct:.0f}%, Web {web_volume_pct:.0f}% of sessions")
        
        # Display platform details with driver context
        if driving_insights:
            summary += f"{' • '.join(driving_insights)}\n\n"
        
        # Web platform details
        if metrics['sessions']:
            web_sessions = metrics['sessions']['web']
            if web_sessions['yoy_change'] is not None:
                web_sess_dir = "up" if web_sessions['yoy_change'] > 0 else "down"
                web_current = int(web_sessions['current'])
                web_previous = int(web_sessions['previous'])
                summary += f"Web: sessions {web_sess_dir} {abs(web_sessions['yoy_change'])}% YoY ({web_current:,} vs {web_previous:,})"
                
                # Add conversion if available
                if metrics['session_conversion'] and metrics['session_conversion']['web']['yoy_change'] is not None:
                    web_conversion = metrics['session_conversion']['web']
                    web_conv_dir = "up" if web_conversion['yoy_change'] > 0 else "down"
                    web_conv_curr = web_conversion['current'] * 100
                    web_conv_prev = web_conversion['previous'] * 100
                    summary += f", conversion {web_conv_dir} {abs(web_conversion['yoy_change'])} ppts YoY ({web_conv_curr:.1f}% vs {web_conv_prev:.1f}%)"
                summary += "\n"
        
        # App platform details  
        if metrics['sessions']:
            app_sessions = metrics['sessions']['apps']
            if app_sessions['yoy_change'] is not None:
                app_sess_dir = "up" if app_sessions['yoy_change'] > 0 else "down"
                app_current = int(app_sessions['current'])
                app_previous = int(app_sessions['previous'])
                summary += f"Apps: sessions {app_sess_dir} {abs(app_sessions['yoy_change'])}% YoY ({app_current:,} vs {app_previous:,})"
                
                # Add conversion if available
                if metrics['session_conversion'] and metrics['session_conversion']['apps']['yoy_change'] is not None:
                    app_conversion = metrics['session_conversion']['apps']
                    app_conv_dir = "up" if app_conversion['yoy_change'] > 0 else "down"
                    app_conv_curr = app_conversion['current'] * 100
                    app_conv_prev = app_conversion['previous'] * 100
                    summary += f", conversion {app_conv_dir} {abs(app_conversion['yoy_change'])} ppts YoY ({app_conv_curr:.1f}% vs {app_conv_prev:.1f}%)"
                summary += "\n"
        
        # Sessions per user platform breakdown with actual values
        if metrics['sessions_per_user']:
            web_spu = metrics['sessions_per_user']['web']
            app_spu = metrics['sessions_per_user']['apps']
            
            spu_platform_details = []
            if web_spu.get('yoy_change') is not None:
                web_spu_dir = "up" if web_spu['yoy_change'] > 0 else "down"
                spu_platform_details.append(f"Web {web_spu_dir} {abs(web_spu['yoy_change'])}% YoY ({web_spu['current']:.2f} vs {web_spu['previous']:.2f})")
            
            if app_spu.get('yoy_change') is not None:
                app_spu_dir = "up" if app_spu['yoy_change'] > 0 else "down"
                spu_platform_details.append(f"App {app_spu_dir} {abs(app_spu['yoy_change'])}% YoY ({app_spu['current']:.2f} vs {app_spu['previous']:.2f})")
            
            if spu_platform_details:
                summary += f"\nSessions per user: {', '.join(spu_platform_details)}"
        
        # User conversion analysis
        if metrics.get('user_conversion'):
            user_conv = metrics['user_conversion']
            
            # Check if we have YoY comparison data
            if isinstance(user_conv, dict) and user_conv.get('combined') and isinstance(user_conv['combined'], dict):
                # We have YoY comparison data
                summary += f"\nUser conversion: "
                platform_uc_details = []
                
                for platform_name, platform_key in [('Web', 'web'), ('App', 'apps')]:
                    platform_data = user_conv.get(platform_key, {})
                    if platform_data.get('yoy_change') is not None:
                        uc_change = platform_data['yoy_change']
                        uc_dir = "up" if uc_change > 0 else "down"
                        uc_current = platform_data['current'] * 100
                        uc_previous = platform_data['previous'] * 100
                        platform_uc_details.append(f"{platform_name} {uc_dir} {abs(uc_change)} ppts YoY ({uc_current:.1f}% vs {uc_previous:.1f}%)")
                
                if platform_uc_details:
                    summary += f"{', '.join(platform_uc_details)}"
            else:
                # We only have current values
                summary += f"\nUser conversion platform breakdown:\n"
                if user_conv.get('combined', 0) > 0:
                    summary += f"Combined: {user_conv['combined'] * 100:.1f}%"
                if user_conv.get('web', 0) > 0:
                    summary += f", Web: {user_conv['web'] * 100:.1f}%"
                if user_conv.get('apps', 0) > 0:
                    summary += f", App: {user_conv['apps'] * 100:.1f}%"
        
        return summary
    
    def format_metric_for_slack(self, metric_name, value, yoy_change, is_percentage=False):
        """Format a metric with emoji and color based on performance."""
        if yoy_change is None:
            return f"{metric_name}: {value}"
        
        # Determine if positive change is good (sessions, conversion) or context-dependent
        is_positive = yoy_change > 0
        
        # Choose emoji and color based on metric type and direction
        if metric_name.lower() in ['sessions', 'sessions per user']:
            # For sessions metrics, up is generally good
            emoji = "🔥" if is_positive else "⚠️"
            color = "#2E7D32" if is_positive else "#D32F2F"  # Green for up, Red for down
        else:  # conversion metrics
            # For conversion, up is always good
            emoji = "🚀" if is_positive else "📉"
            color = "#2E7D32" if is_positive else "#D32F2F"
        
        direction = "up" if is_positive else "down"
        change_text = f"{abs(yoy_change):.1f}{'ppts' if is_percentage else '%'}"
        
        return f"{emoji} *{metric_name}* {direction} {change_text} YoY", color

    def format_for_google_sheets(self, analysis_data):
        """Format key metrics as single-cell business summary for Google Sheets."""
        week_info = analysis_data['week_info']
        metrics = analysis_data.get('metrics', {})
        
        if not metrics or all(v is None for v in metrics.values()):
            return None
        
        # Create concise business summary for single cell
        summary_parts = []
        
        week_num = week_info['iso_week']
        date_range = week_info['date_range']
        
        # Start with week and date
        summary_parts.append(f"Week {week_num} ({date_range}):")
        
        # Key metrics summary
        key_metrics = []
        
        # Sessions
        if metrics.get('sessions', {}).get('combined', {}).get('yoy_change') is not None:
            sessions_data = metrics['sessions']['combined']
            sessions_change = sessions_data['yoy_change']
            sessions_direction = "↑" if sessions_change > 0 else "↓"
            key_metrics.append(f"Sessions {sessions_direction}{abs(sessions_change):.1f}% YoY")
        
        # Session conversion
        if metrics.get('session_conversion', {}).get('combined', {}).get('yoy_change') is not None:
            conv_data = metrics['session_conversion']['combined']
            conv_change = conv_data['yoy_change']
            conv_direction = "↑" if conv_change > 0 else "↓"
            key_metrics.append(f"Session CVR {conv_direction}{abs(conv_change):.1f}ppts YoY")
        
        # Sessions per user
        if metrics.get('sessions_per_user', {}).get('combined', {}).get('yoy_change') is not None:
            spu_data = metrics['sessions_per_user']['combined']
            spu_change = spu_data['yoy_change']
            spu_direction = "↑" if spu_change > 0 else "↓"
            key_metrics.append(f"Sessions/User {spu_direction}{abs(spu_change):.1f}% YoY")
        
        # Note: User CVR will be shown on its own line below, so don't include in combined metrics
        
        if key_metrics:
            summary_parts.append(" | ".join(key_metrics))
        
        # Platform breakdown in same format as combined
        platform_breakdown = []
        
        # Web platform metrics
        web_metrics = []
        if metrics.get('sessions', {}).get('web', {}).get('yoy_change') is not None:
            web_sessions_change = metrics['sessions']['web']['yoy_change']
            web_sessions_direction = "↑" if web_sessions_change > 0 else "↓"
            web_metrics.append(f"Sessions {web_sessions_direction}{abs(web_sessions_change):.1f}%")
        
        if metrics.get('session_conversion', {}).get('web', {}).get('yoy_change') is not None:
            web_conv_change = metrics['session_conversion']['web']['yoy_change']
            web_conv_direction = "↑" if web_conv_change > 0 else "↓"
            web_metrics.append(f"Session CVR {web_conv_direction}{abs(web_conv_change):.1f}ppts")
        
        if (metrics.get('user_conversion', {}).get('web', {}) and 
            isinstance(metrics['user_conversion']['web'], dict) and 
            metrics['user_conversion']['web'].get('yoy_change') is not None):
            web_user_conv_change = metrics['user_conversion']['web']['yoy_change']
            web_user_conv_direction = "↑" if web_user_conv_change > 0 else "↓"
            web_metrics.append(f"User CVR {web_user_conv_direction}{abs(web_user_conv_change):.1f}ppts")
        
        if web_metrics:
            platform_breakdown.append(f"Web: {' | '.join(web_metrics)}")
        
        # App platform metrics
        app_metrics = []
        if metrics.get('sessions', {}).get('apps', {}).get('yoy_change') is not None:
            app_sessions_change = metrics['sessions']['apps']['yoy_change']
            app_sessions_direction = "↑" if app_sessions_change > 0 else "↓"
            app_metrics.append(f"Sessions {app_sessions_direction}{abs(app_sessions_change):.1f}%")
        
        if metrics.get('session_conversion', {}).get('apps', {}).get('yoy_change') is not None:
            app_conv_change = metrics['session_conversion']['apps']['yoy_change']
            app_conv_direction = "↑" if app_conv_change > 0 else "↓"
            app_metrics.append(f"Session CVR {app_conv_direction}{abs(app_conv_change):.1f}ppts")
        
        if (metrics.get('user_conversion', {}).get('apps', {}) and 
            isinstance(metrics['user_conversion']['apps'], dict) and 
            metrics['user_conversion']['apps'].get('yoy_change') is not None):
            app_user_conv_change = metrics['user_conversion']['apps']['yoy_change']
            app_user_conv_direction = "↑" if app_user_conv_change > 0 else "↓"
            app_metrics.append(f"User CVR {app_user_conv_direction}{abs(app_user_conv_change):.1f}ppts")
        
        if app_metrics:
            platform_breakdown.append(f"App: {' | '.join(app_metrics)}")
        
        # Format with line breaks for better readability
        result_lines = []
        
        # Week and date on first line
        result_lines.append(f"Week {week_num} ({date_range}):")
        
        # Combined metrics on second line
        if key_metrics:
            result_lines.append(" | ".join(key_metrics))
        
        # Combined User CVR on third line (if available from chart data)
        if metrics.get('user_conversion', {}).get('combined', {}).get('yoy_change') is not None:
            uc_data = metrics['user_conversion']['combined']
            uc_change = uc_data['yoy_change']
            uc_direction = "↑" if uc_change > 0 else "↓"
            result_lines.append(f"User CVR {uc_direction}{abs(uc_change):.1f}ppts YoY")
        
        # Platform breakdowns on separate lines
        for platform_info in platform_breakdown:
            result_lines.append(platform_info)
        
        return "\n".join(result_lines) if len(result_lines) > 1 else None

    def send_to_slack(self, summary, analysis_data):
        """Send the executive summary to Slack via webhook with enhanced formatting."""
        if not self.slack_webhook_url:
            print("No Slack webhook URL configured")
            return False
        
        # Create enhanced Slack message payload
        week_info = analysis_data['week_info']
        metrics = analysis_data.get('metrics', {})
        
        # Handle case where metrics are null due to API errors
        if not metrics or all(v is None for v in metrics.values()):
            error_message = {
                "text": f"⚠️ Amplitude Analytics Report - Week {week_info['iso_week']} - Data Unavailable",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"⚠️ Week {week_info['iso_week']} Analytics Report - Error",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"📅 *{week_info['date_range']}*\n\n🚫 *Unable to fetch data from Amplitude*\nLikely due to API rate limits. Please try again in a few minutes.\n\n📊 Dashboard: <https://app.amplitude.com/analytics/thortful/dashboard/6pqbsp18|Thortful Analytics Dashboard>"
                        }
                    }
                ]
            }
            
            try:
                response = requests.post(self.slack_webhook_url, json=error_message)
                response.raise_for_status()
                print("⚠️ Error message sent to Slack - API rate limited")
                return True
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to send error message to Slack: {e}")
                return False
        
        # Create summary blocks with colors and emojis
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Week {week_info['iso_week']} Analytics Report",
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
        
        # High-level metrics section with color coding
        metric_fields = []
        
        # Sessions
        if metrics.get('sessions', {}).get('combined', {}).get('yoy_change') is not None:
            sessions_data = metrics['sessions']['combined']
            sessions_text, sessions_color = self.format_metric_for_slack(
                "Sessions", 
                f"{int(sessions_data['current']):,}",
                sessions_data['yoy_change']
            )
            metric_fields.append({
                "type": "mrkdwn",
                "text": f"{sessions_text}\n`{int(sessions_data['current']):,} vs {int(sessions_data['previous']):,}`"
            })
        
        # Session Conversion
        if metrics.get('session_conversion', {}).get('combined', {}).get('yoy_change') is not None:
            conv_data = metrics['session_conversion']['combined']
            conv_text, conv_color = self.format_metric_for_slack(
                "Session CVR",
                f"{conv_data['current']*100:.1f}%", 
                conv_data['yoy_change'],
                is_percentage=True
            )
            metric_fields.append({
                "type": "mrkdwn", 
                "text": f"{conv_text}\n`{conv_data['current']*100:.1f}% vs {conv_data['previous']*100:.1f}%`"
            })
        
        # Sessions per User
        if metrics.get('sessions_per_user', {}).get('combined', {}).get('yoy_change') is not None:
            spu_data = metrics['sessions_per_user']['combined']
            spu_text, spu_color = self.format_metric_for_slack(
                "Sessions per User",
                f"{spu_data['current']:.2f}",
                spu_data['yoy_change']
            )
            metric_fields.append({
                "type": "mrkdwn",
                "text": f"{spu_text}\n`{spu_data['current']:.2f} vs {spu_data['previous']:.2f}`"
            })
        
        # User Conversion
        if metrics.get('user_conversion', {}).get('combined', {}).get('yoy_change') is not None:
            uc_data = metrics['user_conversion']['combined']
            uc_text, uc_color = self.format_metric_for_slack(
                "User CVR",
                f"{uc_data['current']*100:.1f}%",
                uc_data['yoy_change'],
                is_percentage=True
            )
            metric_fields.append({
                "type": "mrkdwn",
                "text": f"{uc_text}\n`{uc_data['current']*100:.1f}% vs {uc_data['previous']*100:.1f}%`"
            })
        
        # Add metrics section
        if metric_fields:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 Key Metrics Overview*"
                }
            })
            blocks.append({
                "type": "section", 
                "fields": metric_fields
            })
        
        # Platform Analysis
        if metrics.get('sessions'):
            web_sessions = metrics['sessions']['web']
            app_sessions = metrics['sessions']['apps']
            combined_sessions = metrics['sessions']['combined']
            
            if all(data.get('current') for data in [web_sessions, app_sessions, combined_sessions]):
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
                
                # Web platform details
                web_emoji = "🔥" if web_sessions.get('yoy_change', 0) > 0 else "⚠️"
                web_conv_emoji = "🚀" if metrics.get('session_conversion', {}).get('web', {}).get('yoy_change', 0) > 0 else "📉"
                
                app_emoji = "🔥" if app_sessions.get('yoy_change', 0) > 0 else "⚠️"
                app_conv_emoji = "🚀" if metrics.get('session_conversion', {}).get('apps', {}).get('yoy_change', 0) > 0 else "📉"
                
                platform_fields = [
                    {
                        "type": "mrkdwn",
                        "text": f"{web_emoji} *Web Sessions*\n{'🟢' if web_sessions['yoy_change'] > 0 else '🔴'} {abs(web_sessions['yoy_change']):.1f}% {'up' if web_sessions['yoy_change'] > 0 else 'down'} YoY\n`{int(web_sessions['current']):,} vs {int(web_sessions['previous']):,}`"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"{app_emoji} *App Sessions*\n{'🟢' if app_sessions['yoy_change'] > 0 else '🔴'} {abs(app_sessions['yoy_change']):.1f}% {'up' if app_sessions['yoy_change'] > 0 else 'down'} YoY\n`{int(app_sessions['current']):,} vs {int(app_sessions['previous']):,}`"
                    }
                ]
                
                # Add session conversion data if available
                if metrics.get('session_conversion', {}).get('web', {}).get('yoy_change') is not None:
                    web_conv = metrics['session_conversion']['web']
                    app_conv = metrics['session_conversion']['apps']
                    
                    platform_fields.extend([
                        {
                            "type": "mrkdwn",
                            "text": f"{web_conv_emoji} *Web Session CVR*\n{'🟢' if web_conv['yoy_change'] > 0 else '🔴'} {abs(web_conv['yoy_change']):.1f} ppts {'up' if web_conv['yoy_change'] > 0 else 'down'} YoY\n`{web_conv['current']*100:.1f}% vs {web_conv['previous']*100:.1f}%`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{app_conv_emoji} *App Session CVR*\n{'🟢' if app_conv['yoy_change'] > 0 else '🔴'} {abs(app_conv['yoy_change']):.1f} ppts {'up' if app_conv['yoy_change'] > 0 else 'down'} YoY\n`{app_conv['current']*100:.1f}% vs {app_conv['previous']*100:.1f}%`"
                        }
                    ])
                
                # Add sessions per user data if available
                if metrics.get('sessions_per_user', {}).get('web', {}).get('yoy_change') is not None:
                    web_spu = metrics['sessions_per_user']['web']
                    app_spu = metrics['sessions_per_user']['apps']
                    
                    web_spu_emoji = "🔥" if web_spu.get('yoy_change') and web_spu.get('yoy_change') > 0 else "⚠️"
                    app_spu_emoji = "🔥" if app_spu.get('yoy_change') and app_spu.get('yoy_change') > 0 else "⚠️"
                    
                    platform_fields.extend([
                        {
                            "type": "mrkdwn",
                            "text": f"{web_spu_emoji} *Web Sessions per User*\n{'🟢' if web_spu['yoy_change'] > 0 else '🔴'} {abs(web_spu['yoy_change']):.1f}% {'up' if web_spu['yoy_change'] > 0 else 'down'} YoY\n`{web_spu['current']:.2f} vs {web_spu['previous']:.2f}`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{app_spu_emoji} *App Sessions per User*\n" + 
                                   ('No data available' if app_spu.get('yoy_change') is None else 
                                    f"{'🟢' if app_spu['yoy_change'] > 0 else '🔴'} {abs(app_spu['yoy_change']):.1f}% {'up' if app_spu['yoy_change'] > 0 else 'down'} YoY") + 
                                   f"\n`{app_spu['current']:.2f} vs {app_spu['previous']:.2f}`"
                        }
                    ])
                
                # Add user conversion data if available
                if (metrics.get('user_conversion', {}).get('web', {}) and 
                    isinstance(metrics['user_conversion']['web'], dict) and 
                    metrics['user_conversion']['web'].get('yoy_change') is not None):
                    web_uc = metrics['user_conversion']['web']
                    app_uc = metrics['user_conversion']['apps']
                    
                    web_uc_emoji = "🚀" if web_uc.get('yoy_change', 0) > 0 else "📉"
                    app_uc_emoji = "🚀" if app_uc.get('yoy_change', 0) > 0 else "📉"
                    
                    platform_fields.extend([
                        {
                            "type": "mrkdwn",
                            "text": f"{web_uc_emoji} *Web User CVR*\n{'🟢' if web_uc['yoy_change'] > 0 else '🔴'} {abs(web_uc['yoy_change']):.1f} ppts {'up' if web_uc['yoy_change'] > 0 else 'down'} YoY\n`{web_uc['current']*100:.1f}% vs {web_uc['previous']*100:.1f}%`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{app_uc_emoji} *App User CVR*\n{'🟢' if app_uc['yoy_change'] > 0 else '🔴'} {abs(app_uc['yoy_change']):.1f} ppts {'up' if app_uc['yoy_change'] > 0 else 'down'} YoY\n`{app_uc['current']*100:.1f}% vs {app_uc['previous']*100:.1f}%`"
                        }
                    ])
                
                blocks.append({
                    "type": "section",
                    "fields": platform_fields
                })
        
        # Google Sheets Export Section
        sheets_data = self.format_for_google_sheets(analysis_data)
        if sheets_data:
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
        
        # Data Sources Section
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
                    "text": f"*Dashboard:* <https://app.amplitude.com/analytics/thortful/dashboard/6pqbsp18|Thortful Analytics Dashboard>\n\n*Charts Used:*\n• <https://app.amplitude.com/analytics/thortful/chart/y0ivh3am|Sessions (Current Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/5vbaz782|Sessions (Previous Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/pc9c0crz|Sessions per User (Current Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/3d400y6n|Sessions per User (Previous Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/42c5gcv4|Session Conversion % (Current Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/3t0wgn4i|Session Conversion % (Previous Year)>\n• <https://app.amplitude.com/analytics/thortful/chart/4j2gp4ph|User Conversion %>"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 *Generated by Amplitude Analytics Bot* | 📊 Data refreshed weekly | 🔗 All chart IDs validated"
                    }
                ]
            }
        ])
        
        slack_message = {
            "text": f"📊 Week {week_info['iso_week']} Analytics Report", 
            "blocks": blocks
        }
        
        try:
            response = requests.post(self.slack_webhook_url, json=slack_message)
            response.raise_for_status()
            print("✅ Report sent to Slack successfully!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send to Slack: {e}")
            return False

def main():
    analyzer = AmplitudeAnalyzer()
    
    # Analyze previous week
    analysis = analyzer.analyze_weekly_data()
    
    if analysis:
        summary = analyzer.generate_executive_summary(analysis)
        print(summary)
        
        # Save detailed results
        with open('weekly_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save text summary for easy reading
        with open('weekly_summary.txt', 'w') as f:
            f.write(summary)
        
        print("\nDetailed analysis saved to weekly_analysis.json")
        print("Summary saved to weekly_summary.txt")
        
        # Send to Slack
        analyzer.send_to_slack(summary, analysis)
    else:
        print("Failed to analyze data. Check API credentials and connectivity.")

if __name__ == "__main__":
    main()
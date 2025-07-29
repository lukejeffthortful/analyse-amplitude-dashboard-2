#!/usr/bin/env python3
"""
Amplitude Data Handler
Handles Amplitude-specific data extraction and processing with separated logic from GA4.
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class AmplitudeDataHandler:
    """Handles Amplitude-specific data extraction and processing"""
    
    def __init__(self):
        self.api_key = os.getenv('AMPLITUDE_API_KEY')
        self.secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("AMPLITUDE_API_KEY and AMPLITUDE_SECRET_KEY must be set in environment")
        
        # Chart configurations from original analyzer
        self.charts = {
            'sessions_current': 'y0ivh3am',
            'sessions_previous': '5vbaz782',
            'sessions_per_user_current': 'pc9c0crz',
            'sessions_per_user_previous': '3d400y6n',
            'session_conversion_current': '42c5gcv4',
            'session_conversion_previous': '3t0wgn4i',
            'user_conversion': '4j2gp4ph'
        }
    
    def get_chart_data(self, chart_id: str, start_date: str = None, end_date: str = None) -> str:
        """Fetch data from a specific Amplitude chart."""
        url = f"https://amplitude.com/api/3/chart/{chart_id}/csv"
        auth = (self.api_key, self.secret_key)
        
        try:
            response = requests.get(url, auth=auth)
            print(f"Fetching Amplitude chart {chart_id}: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
            response.raise_for_status()
            # API returns JSON with 'data' field containing CSV content
            json_response = response.json()
            return json_response.get('data', '')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Amplitude chart {chart_id}: {e}")
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
    
    def extract_platform_metrics(self, csv_data: str, year: int = 2025, target_week: int = None) -> Dict[str, float]:
        """Extract metrics for all three platform segments from Amplitude CSV response."""
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
    
    def calculate_platform_yoy_comparison(self, current_data: str, previous_data: str, 
                                        is_conversion: bool = False, target_week: int = None) -> Dict[str, Any]:
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
    
    def get_weekly_yoy_data(self, target_week: int = None, target_year: int = None) -> Dict[str, Any]:
        """Get Amplitude weekly year-over-year data in standardized format"""
        if not target_week or not target_year:
            # Default to previous week
            today = datetime.now()
            last_week = today - timedelta(days=7)
            target_year, target_week = self.get_iso_week_info(last_week)
        
        print(f"🔍 Fetching Amplitude data for Week {target_week} ({target_year})")
        
        # Fetch data for all charts
        results = {}
        
        for chart_name, chart_id in self.charts.items():
            print(f"Processing {chart_name}...")
            data = self.get_chart_data(chart_id)
            if data:
                print(f"Sample data for {chart_name}: {data[:200]}...")
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
            # For now, extract current year data only
            csv_data = results['user_conversion']
            if 'Previous' in csv_data or 'previous' in csv_data.lower():
                # Chart has built-in YoY comparison, parse as platform comparison
                user_conversion_comparison = self.parse_user_conversion_with_yoy(csv_data)
            else:
                # Chart has current values only, extract platform metrics
                user_conversion_comparison = self.extract_platform_metrics(csv_data, year=2025, target_week=target_week)
        
        return self.standardize_output(
            sessions_comparison,
            sessions_per_user_comparison, 
            conversion_comparison,
            user_conversion_comparison,
            target_week,
            target_year
        )
    
    def parse_user_conversion_with_yoy(self, csv_data: str) -> Dict[str, Any]:
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
    
    def extract_value_from_row(self, row_data: str) -> float:
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
    
    def standardize_output(self, sessions_data: Dict[str, Any], sessions_per_user_data: Dict[str, Any],
                          conversion_data: Dict[str, Any], user_conversion_data: Dict[str, Any],
                          target_week: int, target_year: int) -> Dict[str, Any]:
        """Standardize Amplitude output to match expected format"""
        monday, sunday = self.get_week_date_range(target_year, target_week)
        
        return {
            'sessions': sessions_data,
            'sessions_per_user': sessions_per_user_data,
            'session_conversion': conversion_data,
            'user_conversion': user_conversion_data,
            'metadata': {
                'source': 'amplitude',
                'iso_week': target_week,
                'year': target_year,
                'date_range': f"{monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}"
            }
        }


def main():
    """Test Amplitude data handler"""
    try:
        # Test data extraction
        handler = AmplitudeDataHandler()
        
        # Test weekly data extraction
        weekly_data = handler.get_weekly_yoy_data()
        
        print("\n📊 Amplitude Weekly Data Sample:")
        print(f"Source: {weekly_data['metadata']['source']}")
        print(f"Week: {weekly_data['metadata']['iso_week']} ({weekly_data['metadata']['year']})")
        print(f"Date Range: {weekly_data['metadata']['date_range']}")
        
        if weekly_data['sessions']:
            sessions = weekly_data['sessions']
            print(f"\nSessions:")
            print(f"  Combined: {sessions['combined']['current']:,} vs {sessions['combined']['previous']:,} ({sessions['combined']['yoy_change']:+.1f}% YoY)")
            print(f"  Web: {sessions['web']['current']:,} vs {sessions['web']['previous']:,} ({sessions['web']['yoy_change']:+.1f}% YoY)")
            print(f"  Apps: {sessions['apps']['current']:,} vs {sessions['apps']['previous']:,} ({sessions['apps']['yoy_change']:+.1f}% YoY)")
        
        print("\n✅ AmplitudeDataHandler test completed successfully!")
        
    except Exception as e:
        print(f"❌ AmplitudeDataHandler test failed: {e}")


if __name__ == "__main__":
    main()
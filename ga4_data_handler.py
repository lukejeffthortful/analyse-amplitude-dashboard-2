#!/usr/bin/env python3
"""
GA4 Data Handler
Handles Google Analytics 4 data extraction and processing with separated logic from Amplitude.
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, FilterExpression, Filter
)
from google.oauth2 import service_account
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()


class GA4DataHandler:
    """Handles GA4-specific data extraction and processing"""
    
    def __init__(self, web_property_id: str = None, app_property_id: str = None, credentials_path: str = None):
        self.web_property_id = web_property_id or os.getenv('GA4_WEB_PROPERTY_ID')
        self.app_property_id = app_property_id or os.getenv('GA4_APP_PROPERTY_ID') 
        self.credentials_path = credentials_path or os.getenv('GA4_SERVICE_ACCOUNT_PATH')
        self.client = None
        
        if not self.web_property_id:
            raise ValueError("GA4_WEB_PROPERTY_ID must be set in environment or passed as parameter")
        if not self.app_property_id:
            raise ValueError("GA4_APP_PROPERTY_ID must be set in environment or passed as parameter")
        if not self.credentials_path and not os.getenv('GA4_SERVICE_ACCOUNT_JSON'):
            raise ValueError("Either GA4_SERVICE_ACCOUNT_PATH or GA4_SERVICE_ACCOUNT_JSON must be set in environment")
            
        self._setup_client()
    
    def _setup_client(self):
        """Setup GA4 client with service account authentication"""
        try:
            # Try to get credentials from environment variable first (for GitHub Actions)
            service_account_json = os.getenv('GA4_SERVICE_ACCOUNT_JSON')
            
            if service_account_json:
                # Use credentials from environment variable (JSON string)
                service_account_info = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                print("✅ Using GA4 credentials from environment variable")
            else:
                # Fallback to file-based credentials
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                print(f"✅ Using GA4 credentials from file: {self.credentials_path}")
            
            self.client = BetaAnalyticsDataClient(credentials=credentials)
            print(f"✅ GA4 client initialized successfully for properties Web:{self.web_property_id}, App:{self.app_property_id}")
        except Exception as e:
            print(f"❌ Failed to initialize GA4 client: {e}")
            raise
    
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
    
    def iso_week_to_ga4_dates(self, year: int, week: int) -> Dict[str, str]:
        """Convert ISO week to GA4 date range format"""
        monday, sunday = self.get_week_date_range(year, week)
        return {
            'start_date': monday.strftime('%Y-%m-%d'),
            'end_date': sunday.strftime('%Y-%m-%d')
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_api_request(self, request: RunReportRequest):
        """Make GA4 API request with retry logic"""
        try:
            response = self.client.run_report(request)
            return response
        except Exception as e:
            print(f"GA4 API request failed: {e}")
            raise
    
    def query_ga4_sessions(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Query both GA4 properties separately for accurate platform breakdown"""
        # Query web property
        web_request = RunReportRequest(
            property=f"properties/{self.web_property_id}",
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers")
            ],
            date_ranges=[DateRange(
                start_date=date_range['start_date'], 
                end_date=date_range['end_date']
            )],
            return_property_quota=True
        )
        
        # Query app property
        app_request = RunReportRequest(
            property=f"properties/{self.app_property_id}",
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers")
            ],
            date_ranges=[DateRange(
                start_date=date_range['start_date'], 
                end_date=date_range['end_date']
            )],
            return_property_quota=True
        )
        
        web_response = self._make_api_request(web_request)
        app_response = self._make_api_request(app_request)
        
        return self._process_dual_property_response(web_response, app_response)
    
    def _process_dual_property_response(self, web_response, app_response) -> Dict[str, Any]:
        """Process responses from both GA4 properties into standardized format"""
        # Extract web sessions
        web_sessions = 0
        if web_response.rows:
            web_sessions = int(web_response.rows[0].metric_values[0].value)
        
        # Extract app sessions  
        app_sessions = 0
        if app_response.rows:
            app_sessions = int(app_response.rows[0].metric_values[0].value)
        
        print(f"GA4 Sessions - Web: {web_sessions:,}, App: {app_sessions:,}")
        
        return {
            'web': web_sessions,
            'apps': app_sessions,
            'combined': web_sessions + app_sessions
        }
    
    def get_weekly_yoy_data(self, target_week: int = None, target_year: int = None) -> Dict[str, Any]:
        """Get GA4 weekly year-over-year data in standardized format"""
        if not target_week or not target_year:
            # Default to previous week
            today = datetime.now()
            last_week = today - timedelta(days=7)
            target_year, target_week = self.get_iso_week_info(last_week)
        
        print(f"🔍 Fetching GA4 data for Week {target_week} ({target_year})")
        
        # Get current year data
        current_date_range = self.iso_week_to_ga4_dates(target_year, target_week)
        current_data = self.query_ga4_sessions(current_date_range)
        
        # Get previous year data
        previous_date_range = self.iso_week_to_ga4_dates(target_year - 1, target_week)
        previous_data = self.query_ga4_sessions(previous_date_range)
        
        # Calculate YoY changes
        sessions_metrics = {}
        for platform in ['apps', 'web', 'combined']:
            current_value = current_data.get(platform, 0)
            previous_value = previous_data.get(platform, 0)
            
            if previous_value == 0:
                yoy_change = None
            else:
                yoy_change = ((current_value - previous_value) / previous_value) * 100
                yoy_change = round(yoy_change, 1)
            
            sessions_metrics[platform] = {
                'current': current_value,
                'previous': previous_value,
                'yoy_change': yoy_change
            }
        
        return self.standardize_output(sessions_metrics, target_week, target_year)
    
    def standardize_output(self, sessions_data: Dict[str, Any], target_week: int, target_year: int) -> Dict[str, Any]:
        """Standardize GA4 output to match expected format"""
        monday, sunday = self.get_week_date_range(target_year, target_week)
        
        return {
            'sessions': sessions_data,
            'metadata': {
                'source': 'ga4',
                'iso_week': target_week,
                'year': target_year,
                'date_range': f"{monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}"
            }
        }
    
    def test_connection(self) -> bool:
        """Test GA4 API connection for both properties"""
        try:
            # Test web property
            web_request = RunReportRequest(
                property=f"properties/{self.web_property_id}",
                metrics=[Metric(name="sessions")],
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
            )
            
            # Test app property  
            app_request = RunReportRequest(
                property=f"properties/{self.app_property_id}",
                metrics=[Metric(name="sessions")],
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
            )
            
            web_response = self._make_api_request(web_request)
            app_response = self._make_api_request(app_request)
            
            print(f"✅ GA4 Web property connection successful. Quota: {web_response.property_quota}")
            print(f"✅ GA4 App property connection successful. Quota: {app_response.property_quota}")
            return True
            
        except Exception as e:
            print(f"❌ GA4 connection test failed: {e}")
            return False


def main():
    """Test GA4 data handler"""
    try:
        # Test connection
        handler = GA4DataHandler()
        
        if not handler.test_connection():
            print("❌ GA4 connection failed")
            return
        
        # Test weekly data extraction
        weekly_data = handler.get_weekly_yoy_data()
        
        print("\n📊 GA4 Weekly Data Sample:")
        print(f"Source: {weekly_data['metadata']['source']}")
        print(f"Week: {weekly_data['metadata']['iso_week']} ({weekly_data['metadata']['year']})")
        print(f"Date Range: {weekly_data['metadata']['date_range']}")
        
        sessions = weekly_data['sessions']
        print(f"\nSessions:")
        print(f"  Combined: {sessions['combined']['current']:,} vs {sessions['combined']['previous']:,} ({sessions['combined']['yoy_change']:+.1f}% YoY)")
        print(f"  Web: {sessions['web']['current']:,} vs {sessions['web']['previous']:,} ({sessions['web']['yoy_change']:+.1f}% YoY)")
        print(f"  Apps: {sessions['apps']['current']:,} vs {sessions['apps']['previous']:,} ({sessions['apps']['yoy_change']:+.1f}% YoY)")
        
        print("\n✅ GA4DataHandler test completed successfully!")
        
    except Exception as e:
        print(f"❌ GA4DataHandler test failed: {e}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
AppsFlyer Data Handler
Fetches install data from AppsFlyer Master API grouped by media source and campaign.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import time

load_dotenv()


class AppsFlyerDataHandler:
    """Handles AppsFlyer API interactions for fetching install data"""
    
    def __init__(self):
        self.api_token = os.getenv('APPSFLYER_API_TOKEN')
        self.app_id = os.getenv('APPSFLYER_APP_ID')
        
        if not self.api_token:
            raise ValueError("APPSFLYER_API_TOKEN not found in environment variables")
        if not self.app_id:
            raise ValueError("APPSFLYER_APP_ID not found in environment variables")
        
        # Base URL for Master Report API
        self.base_url = "https://hq1.appsflyer.com/api/master-report/export"
        
        print(f"✅ AppsFlyer handler initialized for app: {self.app_id}")
    
    def get_installs_by_source_and_campaign(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Fetch install data grouped by media source and campaign for a date range.
        
        Args:
            start_date: Start date for the data range
            end_date: End date for the data range
            
        Returns:
            Dictionary containing install data by media source and campaign
        """
        # Format dates for API
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Build API URL with app_id in path
        url = f"{self.base_url}/app/{self.app_id}"
        
        # Build API parameters
        params = {
            'from': from_date,
            'to': to_date,
            'groupings': 'pid,c',  # pid = media source, c = campaign
            'kpis': 'installs',  # Just installs for proof of concept
            'format': 'json'  # Request JSON format
        }
        
        # Use Bearer token authentication
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
        
        print(f"📊 Fetching AppsFlyer data from {from_date} to {to_date}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, params=params, headers=headers)
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if response is JSON or CSV
                content_type = response.headers.get('Content-Type', '')
                
                if 'json' in content_type:
                    data = response.json()
                else:
                    # Parse CSV response
                    data = self._parse_csv_response(response.text)
                
                return self._process_install_data(data, start_date, end_date)
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching AppsFlyer data: {e}")
            return None
    
    def _parse_csv_response(self, csv_text: str) -> List[Dict[str, Any]]:
        """Parse CSV response into list of dictionaries"""
        lines = csv_text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # First line is headers
        headers = lines[0].split(',')
        
        # Parse data rows
        data = []
        for line in lines[1:]:
            values = line.split(',')
            row = dict(zip(headers, values))
            data.append(row)
        
        return data
    
    def _process_install_data(self, raw_data: Any, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Process raw API response into structured install data"""
        
        # Initialize result structure
        result = {
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'total_installs': 0,
            'by_media_source': {},
            'by_campaign': {},
            'by_source_and_campaign': {},
            'top_sources': [],
            'top_campaigns': []
        }
        
        # Handle different response formats
        data_to_process = []
        
        if isinstance(raw_data, dict):
            # Check if data is in a 'data' field or 'results' field
            if 'data' in raw_data:
                data_to_process = raw_data['data']
            elif 'results' in raw_data:
                data_to_process = raw_data['results']
            else:
                # Assume the whole dict is a single record
                data_to_process = [raw_data]
        elif isinstance(raw_data, list):
            data_to_process = raw_data
        
        # Process data
        for record in data_to_process:
            media_source = record.get('pid', record.get('media_source', 'Unknown'))
            campaign = record.get('c', record.get('campaign', 'Unknown'))
            installs = int(float(record.get('installs', 0)))
            
            # Update totals
            result['total_installs'] += installs
            
            # By media source
            if media_source not in result['by_media_source']:
                result['by_media_source'][media_source] = 0
            result['by_media_source'][media_source] += installs
            
            # By campaign
            if campaign not in result['by_campaign']:
                result['by_campaign'][campaign] = 0
            result['by_campaign'][campaign] += installs
            
            # By source and campaign
            key = f"{media_source} | {campaign}"
            if key not in result['by_source_and_campaign']:
                result['by_source_and_campaign'][key] = {
                    'media_source': media_source,
                    'campaign': campaign,
                    'installs': 0
                }
            result['by_source_and_campaign'][key]['installs'] += installs
        
        # Calculate top sources and campaigns
        result['top_sources'] = sorted(
            [{'source': k, 'installs': v} for k, v in result['by_media_source'].items()],
            key=lambda x: x['installs'],
            reverse=True
        )[:10]
        
        result['top_campaigns'] = sorted(
            [{'campaign': k, 'installs': v} for k, v in result['by_campaign'].items()],
            key=lambda x: x['installs'],
            reverse=True
        )[:10]
        
        return result
    
    def get_week_install_summary(self, target_week: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get install summary for a specific ISO week.
        
        Args:
            target_week: ISO week number (1-53). If None, uses previous week.
            year: Year for the week. If None, uses current year.
            
        Returns:
            Dictionary containing weekly install summary
        """
        # Calculate week dates
        if target_week is None:
            # Use previous week
            today = datetime.now()
            last_monday = today - timedelta(days=today.weekday() + 7)
            iso_year, iso_week, _ = last_monday.isocalendar()
            target_week = iso_week
            year = iso_year
        elif year is None:
            year = datetime.now().year
        
        # Get Monday and Sunday of the target week
        jan4 = datetime(year, 1, 4)
        week1_monday = jan4 - timedelta(days=jan4.weekday())
        target_monday = week1_monday + timedelta(weeks=target_week-1)
        target_sunday = target_monday + timedelta(days=6)
        
        print(f"\n📅 Analyzing Week {target_week} of {year}")
        print(f"   Date range: {target_monday.strftime('%Y-%m-%d')} to {target_sunday.strftime('%Y-%m-%d')}")
        
        # Fetch data for the week
        return self.get_installs_by_source_and_campaign(target_monday, target_sunday)
    
    def format_install_summary(self, data: Dict[str, Any]) -> str:
        """Format install data into a readable summary"""
        if not data:
            return "No data available"
        
        summary = []
        summary.append(f"AppsFlyer Install Summary ({data['date_range']['start']} to {data['date_range']['end']}):")
        summary.append(f"\nTotal Installs: {data['total_installs']:,}")
        
        if data['top_sources']:
            summary.append("\nTop Media Sources:")
            for i, source in enumerate(data['top_sources'][:5], 1):
                pct = (source['installs'] / data['total_installs'] * 100) if data['total_installs'] > 0 else 0
                summary.append(f"  {i}. {source['source']}: {source['installs']:,} ({pct:.1f}%)")
        
        if data['top_campaigns']:
            summary.append("\nTop Campaigns:")
            for i, campaign in enumerate(data['top_campaigns'][:5], 1):
                pct = (campaign['installs'] / data['total_installs'] * 100) if data['total_installs'] > 0 else 0
                summary.append(f"  {i}. {campaign['campaign']}: {campaign['installs']:,} ({pct:.1f}%)")
        
        return "\n".join(summary)
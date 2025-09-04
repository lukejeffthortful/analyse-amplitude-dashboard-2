#!/usr/bin/env python3
"""
AppsFlyer Pull API Handler
Uses the Pull API for fetching install data (limited to 10 calls/day)
Only includes non-organic installs as per plan limitations
"""

import os
import requests
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import time

load_dotenv()


class AppsFlyerPullAPIHandler:
    """Handles AppsFlyer Pull API interactions for fetching non-organic install data"""
    
    def __init__(self):
        self.api_token = os.getenv('APPSFLYER_API_TOKEN')
        self.app_id = os.getenv('APPSFLYER_APP_ID')
        
        if not self.api_token:
            raise ValueError("APPSFLYER_API_TOKEN not found in environment variables")
        if not self.app_id:
            raise ValueError("APPSFLYER_APP_ID not found in environment variables")
        
        # Base URL for Aggregated Data Export API
        self.base_url = "https://hq1.appsflyer.com/api/agg-data/export"
        
        print(f"✅ AppsFlyer Pull API handler initialized for app: {self.app_id}")
        print("⚠️  Note: Limited to 10 API calls per day, using aggregated partners report")
    
    def get_installs_by_source_and_campaign(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Fetch non-organic install data grouped by media source and campaign.
        
        Args:
            start_date: Start date for the data range
            end_date: End date for the data range
            
        Returns:
            Dictionary containing install data by media source and campaign
        """
        # Format dates for API (YYYY-MM-DD)
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Build API URL for partners report (aggregated data like dashboard)
        url = f"{self.base_url}/app/{self.app_id}/partners_report/v5"
        
        # Build API parameters - basic installs report includes media source and campaign by default
        params = {
            'from': from_date,
            'to': to_date
        }
        
        # Use Bearer token authentication
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'text/csv'
        }
        
        print(f"📊 Fetching AppsFlyer data from {from_date} to {to_date}")
        print(f"   URL: {url}")
        print("   ⏱️  This counts as 1 of your 10 daily API calls")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse CSV response
                return self._process_csv_data(response.text, start_date, end_date)
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching AppsFlyer data: {e}")
            return None
    
    def _process_csv_data(self, csv_text: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Process CSV response from Pull API"""
        
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
            'top_campaigns': [],
            'data_type': 'non-organic'  # As per plan limitations
        }
        
        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            
            for row in csv_reader:
                # Extract relevant fields from partners report (aggregated data)
                media_source = row.get('Media Source', row.get('media_source', 'Unknown'))
                campaign = row.get('Campaign', row.get('campaign', 'Unknown'))
                
                # Get install count from aggregated data
                installs = 0
                for col in ['Installs', 'installs', 'Total Installs']:
                    if col in row and row[col]:
                        try:
                            installs = int(float(row[col]))
                            break
                        except (ValueError, TypeError):
                            continue
                
                if installs == 0:
                    continue
                
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
            
            print(f"✅ Processed {result['total_installs']:,} installs from partners report")
            
            # Save raw CSV for debugging
            with open('appsflyer_raw_response.csv', 'w') as f:
                f.write(csv_text)
            print("📁 Raw CSV saved to: appsflyer_raw_response.csv")
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing CSV data: {e}")
            # Save problematic CSV for debugging
            with open('appsflyer_error_response.csv', 'w') as f:
                f.write(csv_text)
            print("📁 Error response saved to: appsflyer_error_response.csv")
            return None
    
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
        summary.append(f"Data Type: Non-Organic Installs Only")
        summary.append(f"\nTotal Non-Organic Installs: {data['total_installs']:,}")
        
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
        
        summary.append("\n⚠️  Note: This data excludes organic installs")
        summary.append("📊 API Calls: You have 9 remaining calls today (10 per day limit)")
        
        return "\n".join(summary)
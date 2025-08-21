#!/usr/bin/env python3
"""
AppsFlyer CSV Handler - Reads from manually exported CSV files
This approach works around API limitations by using manual exports that include Google Ads data
"""

import os
import csv
import glob
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import re


class AppsFlyerCSVHandler:
    """Handler for manually exported AppsFlyer CSV files"""
    
    def __init__(self, exports_dir: str = "appsflyer-report-exports", auto_merge: bool = True):
        """
        Initialize the CSV handler
        
        Args:
            exports_dir: Directory containing exported CSV files
            auto_merge: Whether to automatically merge multiple CSV files
        """
        self.exports_dir = exports_dir
        self.app_id = os.getenv('APPSFLYER_APP_ID', 'Unknown')
        self.auto_merge = auto_merge
        self.merged_file = os.path.join(self.exports_dir, "appsflyer_merged_data.csv")
        
        # Create exports directory if it doesn't exist
        if not os.path.exists(self.exports_dir):
            os.makedirs(self.exports_dir)
            print(f"📁 Created exports directory: {self.exports_dir}")
        
        print(f"✅ AppsFlyer CSV handler initialized")
        print(f"📂 Looking for exports in: {self.exports_dir}/")
        
        # Check if merged file exists or needs updating
        if self.auto_merge:
            self._check_and_merge_if_needed()
    
    def _check_and_merge_if_needed(self):
        """Check if merged file needs to be created or updated"""
        csv_files = glob.glob(os.path.join(self.exports_dir, "*.csv"))
        # Exclude the merged file itself
        csv_files = [f for f in csv_files if os.path.basename(f) != "appsflyer_merged_data.csv"]
        
        if not csv_files:
            return
        
        # Check if merged file exists and is newer than all source files
        if os.path.exists(self.merged_file):
            merged_mtime = os.path.getmtime(self.merged_file)
            newest_source_mtime = max(os.path.getmtime(f) for f in csv_files)
            
            if merged_mtime > newest_source_mtime:
                print("📊 Using existing merged data file")
                return
        
        # Need to merge
        print("🔄 Merging CSV files...")
        from appsflyer_csv_merger_simple import merge_appsflyer_csvs
        merge_appsflyer_csvs(self.exports_dir)
    
    def _parse_filename_dates(self, filename: str) -> Optional[Tuple[datetime, datetime]]:
        """
        Parse start and end dates from filename format: YYYY-MM-DD__YYYY-MM-DD.csv
        
        Returns:
            Tuple of (start_date, end_date) or None if parsing fails
        """
        # Extract just the filename without path
        basename = os.path.basename(filename)
        
        # Match pattern: YYYY-MM-DD__YYYY-MM-DD.csv
        pattern = r'(\d{4}-\d{2}-\d{2})__(\d{4}-\d{2}-\d{2})\.csv'
        match = re.match(pattern, basename)
        
        if match:
            try:
                start_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                end_date = datetime.strptime(match.group(2), '%Y-%m-%d')
                return (start_date, end_date)
            except ValueError:
                return None
        return None
    
    def find_csv_for_date_range(self, start_date: datetime, end_date: datetime) -> Optional[str]:
        """
        Find a CSV file that contains data for the requested date range
        
        Returns:
            Path to the CSV file or None if not found
        """
        # If auto_merge is enabled and merged file exists, use it
        if self.auto_merge and os.path.exists(self.merged_file):
            # For merged file, we need to check if any source files cover the date range
            source_files = glob.glob(os.path.join(self.exports_dir, "*.csv"))
            source_files = [f for f in source_files if os.path.basename(f) != "appsflyer_merged_data.csv"]
            
            for csv_file in source_files:
                file_dates = self._parse_filename_dates(csv_file)
                if file_dates:
                    file_start, file_end = file_dates
                    if file_start <= start_date and file_end >= end_date:
                        return self.merged_file
            
            # Even if no exact match, return merged file as it has all available data
            if source_files:
                return self.merged_file
        
        # Otherwise, look for individual files
        csv_files = glob.glob(os.path.join(self.exports_dir, "*.csv"))
        
        for csv_file in csv_files:
            file_dates = self._parse_filename_dates(csv_file)
            if file_dates:
                file_start, file_end = file_dates
                
                # Check if requested range is within file range
                if file_start <= start_date and file_end >= end_date:
                    return csv_file
        
        return None
    
    def get_available_date_ranges(self) -> List[Tuple[datetime, datetime]]:
        """Get list of date ranges available from CSV files"""
        csv_files = glob.glob(os.path.join(self.exports_dir, "*.csv"))
        date_ranges = []
        
        for csv_file in csv_files:
            file_dates = self._parse_filename_dates(csv_file)
            if file_dates:
                date_ranges.append(file_dates)
        
        return sorted(date_ranges, key=lambda x: x[0])
    
    def get_installs_by_source_and_campaign(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get install data from CSV exports for the specified date range
        
        Args:
            start_date: Start date for the data range
            end_date: End date for the data range
            
        Returns:
            Dictionary containing install data by media source and campaign
        """
        # Find appropriate CSV file
        csv_file = self.find_csv_for_date_range(start_date, end_date)
        
        if not csv_file:
            # Provide helpful error message
            available_ranges = self.get_available_date_ranges()
            
            print(f"❌ No CSV export found for date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print(f"\n📊 Available CSV exports:")
            
            if available_ranges:
                for start, end in available_ranges:
                    print(f"   • {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
                print(f"\n💡 Please export data from AppsFlyer that includes your requested date range")
                print(f"   and save it as: {self.exports_dir}/{start_date.strftime('%Y-%m-%d')}__{end_date.strftime('%Y-%m-%d')}.csv")
            else:
                print(f"   No CSV exports found in {self.exports_dir}/")
                print(f"\n💡 To get started:")
                print(f"   1. Export data from AppsFlyer dashboard")
                print(f"   2. Save as: {self.exports_dir}/YYYY-MM-DD__YYYY-MM-DD.csv")
                print(f"   3. Example: {self.exports_dir}/{start_date.strftime('%Y-%m-%d')}__{end_date.strftime('%Y-%m-%d')}.csv")
            
            return None
        
        print(f"📄 Using CSV export: {csv_file}")
        
        # Read and process the CSV
        return self._process_csv_file(csv_file, start_date, end_date)
    
    def _process_csv_file(self, csv_file: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Process the CSV file and extract install data"""
        
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
            'data_source': 'manual_csv_export',
            'csv_file': os.path.basename(csv_file)
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                
                for row in csv_reader:
                    # Extract fields from the manual export format
                    media_source = row.get('media-source', 'Unknown').strip()
                    campaign = row.get('campaign', 'None').strip()
                    
                    # Get install count - manual exports use 'installs appsflyer' column
                    installs_str = row.get('installs appsflyer', '0')
                    try:
                        installs = int(float(installs_str)) if installs_str else 0
                    except (ValueError, TypeError):
                        installs = 0
                    
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
            
            print(f"✅ Processed {result['total_installs']:,} installs from CSV export")
            
            # Check for key sources
            key_sources = ['googleadwords_int', 'google_organic_seo', 'Facebook Ads']
            found_sources = [s for s in key_sources if s in result['by_media_source']]
            if found_sources:
                print(f"🎯 Found key sources: {found_sources}")
                for source in found_sources:
                    print(f"   • {source}: {result['by_media_source'][source]:,} installs")
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing CSV file: {e}")
            return None
    
    def get_week_install_summary(self, target_week: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """Get install summary for a specific ISO week using CSV exports"""
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
        summary.append(f"Data Source: Manual CSV Export ({data['csv_file']})")
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
        
        # Check for Google Ads presence
        google_sources = ['googleadwords_int', 'google_organic_seo']
        has_google = any(s in data['by_media_source'] for s in google_sources)
        
        if has_google:
            summary.append("\n✅ Google Ads data included in this export")
        else:
            summary.append("\n⚠️  No Google Ads data found in this export")
        
        return "\n".join(summary)
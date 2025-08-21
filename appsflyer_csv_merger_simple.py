#!/usr/bin/env python3
"""
AppsFlyer CSV Merger - Simple version without pandas
"""

import os
import csv
import glob
from collections import defaultdict
from typing import Dict, List


def merge_appsflyer_csvs(exports_dir: str = "appsflyer-report-exports") -> str:
    """
    Merge all AppsFlyer CSV files into a single consolidated file
    
    Returns:
        Path to the merged CSV file
    """
    csv_files = glob.glob(os.path.join(exports_dir, "*.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in {exports_dir}")
        return None
    
    print(f"📊 Found {len(csv_files)} CSV files to merge:")
    for file in sorted(csv_files):
        print(f"   • {os.path.basename(file)}")
    
    # Dictionary to store aggregated data
    # Key: (media-source, campaign), Value: dict of aggregated values
    aggregated_data = defaultdict(lambda: {
        'installs': 0,
        'impressions': 0,
        'clicks': 0,
        'source_files': set()
    })
    
    # Read and aggregate data from all files
    for csv_file in csv_files:
        print(f"\n📄 Processing: {os.path.basename(csv_file)}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                row_count = 0
                
                for row in reader:
                    row_count += 1
                    
                    # Extract key fields
                    media_source = row.get('media-source', 'Unknown').strip()
                    campaign = row.get('campaign', 'None').strip()
                    key = (media_source, campaign)
                    
                    # Aggregate numeric values
                    try:
                        installs = int(float(row.get('installs appsflyer', 0) or 0))
                        aggregated_data[key]['installs'] += installs
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        impressions = int(float(row.get('impressions', 0) or 0))
                        aggregated_data[key]['impressions'] += impressions
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        clicks = int(float(row.get('clicks', 0) or 0))
                        aggregated_data[key]['clicks'] += clicks
                    except (ValueError, TypeError):
                        pass
                    
                    # Track source file
                    aggregated_data[key]['source_files'].add(os.path.basename(csv_file))
                
                print(f"   ✓ Loaded {row_count} rows")
                
        except Exception as e:
            print(f"   ❌ Error reading {csv_file}: {e}")
    
    if not aggregated_data:
        print("❌ No data loaded from CSV files")
        return None
    
    # Convert to sorted list for output
    sorted_data = []
    for (media_source, campaign), values in aggregated_data.items():
        sorted_data.append({
            'media-source': media_source,
            'campaign': campaign,
            'installs appsflyer': values['installs'],
            'impressions': values['impressions'],
            'clicks': values['clicks'],
            'source_files': ', '.join(sorted(values['source_files']))
        })
    
    # Sort by installs (descending)
    sorted_data.sort(key=lambda x: x['installs appsflyer'], reverse=True)
    
    # Write merged data
    output_file = os.path.join(exports_dir, "appsflyer_merged_data.csv")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['media-source', 'campaign', 'installs appsflyer', 'impressions', 'clicks', 'source_files']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_data)
    
    print(f"\n✅ Merged data saved to: {output_file}")
    print(f"   Total unique media source/campaign combinations: {len(sorted_data)}")
    
    # Calculate totals
    total_installs = sum(row['installs appsflyer'] for row in sorted_data)
    print(f"   Total installs across all data: {total_installs:,}")
    
    # Show top sources
    media_source_totals = defaultdict(int)
    for row in sorted_data:
        media_source_totals[row['media-source']] += row['installs appsflyer']
    
    print("\n📈 Top 5 Media Sources:")
    top_sources = sorted(media_source_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    for source, installs in top_sources:
        print(f"   • {source}: {installs:,} installs")
    
    return output_file


if __name__ == "__main__":
    merge_appsflyer_csvs()
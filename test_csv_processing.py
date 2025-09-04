#!/usr/bin/env python3
"""Test processing of the existing AppsFlyer CSV file"""

import csv
import io

def test_csv_processing():
    """Test the CSV processing with the actual file"""
    
    # Read the CSV file
    with open('appsflyer_partners_aggregated.csv', 'r') as f:
        csv_text = f.read()
    
    print("Testing CSV processing with fixed column names...\n")
    
    # Process CSV
    csv_reader = csv.DictReader(io.StringIO(csv_text))
    
    total_installs = 0
    by_media_source = {}
    
    for row in csv_reader:
        # Use the correct column name
        media_source = row.get('Media Source (pid)', 'Unknown').strip()
        if not media_source:
            media_source = 'Unknown'
            
        # Get installs count
        installs = int(row.get('Installs', 0))
        
        if installs > 0:
            total_installs += installs
            
            if media_source not in by_media_source:
                by_media_source[media_source] = 0
            by_media_source[media_source] += installs
            
            print(f"✓ {media_source}: {installs} installs")
    
    print(f"\nTotal installs: {total_installs:,}")
    print("\nBy Media Source:")
    for source, count in sorted(by_media_source.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_installs * 100) if total_installs > 0 else 0
        print(f"  • {source}: {count:,} ({pct:.1f}%)")

if __name__ == "__main__":
    test_csv_processing()
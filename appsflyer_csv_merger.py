#!/usr/bin/env python3
"""
AppsFlyer CSV Merger - Combines multiple CSV exports into a single source of truth
"""

import os
import csv
import glob
from datetime import datetime
from typing import Dict, List, Set
import pandas as pd


class AppsFlyerCSVMerger:
    """Merges multiple AppsFlyer CSV exports into a single consolidated dataset"""
    
    def __init__(self, exports_dir: str = "appsflyer-report-exports"):
        self.exports_dir = exports_dir
        
    def merge_all_csvs(self, output_file: str = "appsflyer_merged_data.csv") -> str:
        """
        Merge all CSV files in the exports directory into a single file
        
        Returns:
            Path to the merged CSV file
        """
        csv_files = glob.glob(os.path.join(self.exports_dir, "*.csv"))
        
        if not csv_files:
            print(f"❌ No CSV files found in {self.exports_dir}")
            return None
        
        print(f"📊 Found {len(csv_files)} CSV files to merge:")
        for file in sorted(csv_files):
            print(f"   • {os.path.basename(file)}")
        
        # Read all CSVs and combine
        all_data = []
        
        for csv_file in csv_files:
            print(f"\n📄 Processing: {os.path.basename(csv_file)}")
            
            try:
                # Read CSV with pandas for better handling
                df = pd.read_csv(csv_file, dtype=str)
                
                # Add source file info
                df['source_file'] = os.path.basename(csv_file)
                
                # Convert numeric columns back to proper types
                numeric_columns = ['installs appsflyer', 'impressions', 'clicks', 
                                 'installs-ua appsflyer', 'installs-reattr appsflyer',
                                 'installs-retarget appsflyer']
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                all_data.append(df)
                print(f"   ✓ Loaded {len(df)} rows")
                
            except Exception as e:
                print(f"   ❌ Error reading {csv_file}: {e}")
        
        if not all_data:
            print("❌ No data loaded from CSV files")
            return None
        
        # Combine all dataframes
        print("\n🔄 Merging data...")
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicates based on media source and campaign combination
        print(f"   Total rows before deduplication: {len(merged_df)}")
        
        # Group by media source and campaign, summing the numeric values
        key_columns = ['media-source', 'campaign']
        numeric_columns = [col for col in numeric_columns if col in merged_df.columns]
        
        # Aggregate data
        aggregated = merged_df.groupby(key_columns, as_index=False).agg({
            **{col: 'sum' for col in numeric_columns},
            'source_file': lambda x: ', '.join(sorted(set(x)))  # Track which files contributed
        })
        
        print(f"   Rows after aggregation: {len(aggregated)}")
        
        # Sort by installs (descending)
        if 'installs appsflyer' in aggregated.columns:
            aggregated = aggregated.sort_values('installs appsflyer', ascending=False)
        
        # Save merged data
        output_path = os.path.join(self.exports_dir, output_file)
        aggregated.to_csv(output_path, index=False)
        
        print(f"\n✅ Merged data saved to: {output_path}")
        print(f"   Total unique media source/campaign combinations: {len(aggregated)}")
        
        # Show summary statistics
        if 'installs appsflyer' in aggregated.columns:
            total_installs = aggregated['installs appsflyer'].sum()
            print(f"   Total installs across all data: {total_installs:,}")
            
            # Top sources
            print("\n📈 Top 5 Media Sources:")
            top_sources = aggregated.groupby('media-source')['installs appsflyer'].sum().sort_values(ascending=False).head(5)
            for source, installs in top_sources.items():
                print(f"   • {source}: {installs:,} installs")
        
        return output_path


def merge_appsflyer_exports():
    """Convenience function to merge all AppsFlyer exports"""
    merger = AppsFlyerCSVMerger()
    return merger.merge_all_csvs()


if __name__ == "__main__":
    merge_appsflyer_exports()
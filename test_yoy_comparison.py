#!/usr/bin/env python3
"""
Test Year-over-Year Comparison for AppsFlyer Data
Export and compare Aug 25-31 for 2024 vs 2025
"""

import asyncio
from datetime import datetime
from appsflyer_working_final import AppsFlyerExporter
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def export_yoy_data():
    """Export data for both 2024 and 2025 for comparison"""
    exporter = AppsFlyerExporter()
    
    # Define date ranges
    # 2025 dates
    start_2025 = datetime(2025, 8, 25)
    end_2025 = datetime(2025, 8, 31)
    
    # Same week in 2024
    start_2024 = datetime(2024, 8, 26)  # Aug 26-Sep 1, 2024 (same week of year)
    end_2024 = datetime(2024, 9, 1)
    
    logger.info("🚀 Starting Year-over-Year AppsFlyer Export Test")
    logger.info(f"2025 range: {start_2025.strftime('%Y-%m-%d')} to {end_2025.strftime('%Y-%m-%d')}")
    logger.info(f"2024 range: {start_2024.strftime('%Y-%m-%d')} to {end_2024.strftime('%Y-%m-%d')}")
    
    try:
        # Export 2025 data first
        logger.info("\n📊 Exporting 2025 data...")
        csv_2025 = await exporter.export_date_range(start_2025, end_2025, headless=False)
        logger.info(f"✓ 2025 export complete: {csv_2025}")
        
        # Wait a bit between exports
        await asyncio.sleep(3)
        
        # Export 2024 data
        logger.info("\n📊 Exporting 2024 data...")
        csv_2024 = await exporter.export_date_range(start_2024, end_2024, headless=False)
        logger.info(f"✓ 2024 export complete: {csv_2024}")
        
        # Analyze the data
        logger.info("\n📈 Analyzing Year-over-Year Changes...")
        comparison_result = analyze_yoy_data(csv_2025, csv_2024)
        
        return comparison_result
        
    except Exception as e:
        logger.error(f"❌ Export failed: {str(e)}")
        raise

def analyze_yoy_data(csv_2025_path, csv_2024_path):
    """Analyze and compare the two CSV files"""
    
    try:
        # Read CSVs
        df_2025 = pd.read_csv(csv_2025_path)
        df_2024 = pd.read_csv(csv_2024_path)
        
        logger.info(f"\n2025 Data Shape: {df_2025.shape}")
        logger.info(f"2025 Columns: {list(df_2025.columns)}")
        logger.info(f"2025 Sample:\n{df_2025.head()}")
        
        logger.info(f"\n2024 Data Shape: {df_2024.shape}")
        logger.info(f"2024 Columns: {list(df_2024.columns)}")
        logger.info(f"2024 Sample:\n{df_2024.head()}")
        
        # Analyze by media source
        if 'media-source' in df_2025.columns and 'installs appsflyer' in df_2025.columns:
            # Group by media source
            installs_2025 = df_2025.groupby('media-source')['installs appsflyer'].sum()
            installs_2024 = df_2024.groupby('media-source')['installs appsflyer'].sum()
            
            # Create comparison
            comparison = pd.DataFrame({
                '2025_installs': installs_2025,
                '2024_installs': installs_2024
            }).fillna(0)
            
            comparison['yoy_change'] = comparison['2025_installs'] - comparison['2024_installs']
            comparison['yoy_percent'] = ((comparison['2025_installs'] - comparison['2024_installs']) / comparison['2024_installs'] * 100).round(1)
            comparison['yoy_percent'] = comparison['yoy_percent'].fillna(0)
            
            logger.info(f"\n📊 Year-over-Year Comparison by Media Source:")
            logger.info(f"{comparison}")
            
            # Total installs comparison
            total_2025 = df_2025['installs appsflyer'].sum()
            total_2024 = df_2024['installs appsflyer'].sum()
            total_change = total_2025 - total_2024
            total_percent = (total_change / total_2024 * 100) if total_2024 > 0 else 0
            
            logger.info(f"\n📈 Total Installs Comparison:")
            logger.info(f"2025: {total_2025:,} installs")
            logger.info(f"2024: {total_2024:,} installs") 
            logger.info(f"Change: {total_change:+,} ({total_percent:+.1f}%)")
            
            # Save comparison to file
            comparison_path = Path("appsflyer_exports/yoy_comparison_aug25-31.csv")
            comparison.to_csv(comparison_path)
            logger.info(f"\n💾 Comparison saved to: {comparison_path}")
            
            return {
                'csv_2025': csv_2025_path,
                'csv_2024': csv_2024_path,
                'comparison': comparison,
                'total_2025': total_2025,
                'total_2024': total_2024,
                'total_change': total_change,
                'total_percent': total_percent
            }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return None

async def main():
    """Main test function"""
    try:
        # Check if pandas is available
        import pandas as pd
        
        result = await export_yoy_data()
        
        if result:
            logger.info("\n🎉 Year-over-Year test completed successfully!")
        
    except ImportError:
        logger.error("pandas not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "pandas"], check=True)
        logger.info("pandas installed. Please run the script again.")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
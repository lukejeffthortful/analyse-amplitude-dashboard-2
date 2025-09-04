#!/usr/bin/env python3
"""
Simplified Year-over-Year Test
Using same-month ranges to avoid calendar issues
"""

import asyncio
from datetime import datetime
from appsflyer_working_final import AppsFlyerExporter
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simple_yoy_test():
    """Test YoY with same-month ranges to avoid date picker issues"""
    exporter = AppsFlyerExporter()
    
    # Use same-month ranges to avoid calendar complexity
    # 2025: Aug 25-31 (7 days)
    start_2025 = datetime(2025, 8, 25)
    end_2025 = datetime(2025, 8, 31)
    
    # 2024: Aug 25-31 (7 days) - same dates, different year
    start_2024 = datetime(2024, 8, 25)
    end_2024 = datetime(2024, 8, 31)
    
    logger.info("📊 Simplified Year-over-Year Test")
    logger.info(f"2025: {start_2025.strftime('%Y-%m-%d')} to {end_2025.strftime('%Y-%m-%d')}")
    logger.info(f"2024: {start_2024.strftime('%Y-%m-%d')} to {end_2024.strftime('%Y-%m-%d')}")
    
    try:
        # We already have 2025 data from previous test
        csv_2025_path = exporter.download_dir / "appsflyer_marketing_20250825_20250831.csv"
        
        if csv_2025_path.exists():
            logger.info("✓ Using existing 2025 data")
        else:
            logger.info("Exporting 2025 data...")
            csv_2025_path = await exporter.export_date_range(start_2025, end_2025, headless=False)
        
        # Export 2024 data
        logger.info("\n📊 Exporting 2024 data...")
        csv_2024_path = await exporter.export_date_range(start_2024, end_2024, headless=False)
        
        # Analyze both files
        logger.info("\n📈 Analyzing data...")
        analyze_comparison(csv_2025_path, csv_2024_path)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")

def analyze_comparison(csv_2025_path, csv_2024_path):
    """Analyze and compare the CSV data"""
    
    try:
        # Read the data
        df_2025 = pd.read_csv(csv_2025_path)
        df_2024 = pd.read_csv(csv_2024_path)
        
        logger.info(f"\n📊 2025 Data ({csv_2025_path.name}):")
        logger.info(f"   Shape: {df_2025.shape}")
        logger.info(f"   Columns: {list(df_2025.columns)}")
        
        logger.info(f"\n📊 2024 Data ({csv_2024_path.name}):")
        logger.info(f"   Shape: {df_2024.shape}")
        logger.info(f"   Columns: {list(df_2024.columns)}")
        
        # Show sample data
        logger.info(f"\n2025 Sample:\n{df_2025.head()}")
        logger.info(f"\n2024 Sample:\n{df_2024.head()}")
        
        # Basic comparison if we have install data
        if 'installs appsflyer' in df_2025.columns:
            total_2025 = df_2025['installs appsflyer'].sum()
            total_2024 = df_2024['installs appsflyer'].sum() if 'installs appsflyer' in df_2024.columns else 0
            
            change = total_2025 - total_2024
            percent_change = (change / total_2024 * 100) if total_2024 > 0 else 0
            
            logger.info(f"\n📈 Total Installs Comparison:")
            logger.info(f"   2025: {total_2025:,}")
            logger.info(f"   2024: {total_2024:,}")
            logger.info(f"   Change: {change:+,} ({percent_change:+.1f}%)")
            
            # By media source
            if 'media-source' in df_2025.columns:
                sources_2025 = df_2025.groupby('media-source')['installs appsflyer'].sum()
                logger.info(f"\n📱 2025 by Media Source:")
                for source, installs in sources_2025.items():
                    logger.info(f"   {source}: {installs:,}")
                
                if 'media-source' in df_2024.columns:
                    sources_2024 = df_2024.groupby('media-source')['installs appsflyer'].sum()
                    logger.info(f"\n📱 2024 by Media Source:")
                    for source, installs in sources_2024.items():
                        logger.info(f"   {source}: {installs:,}")
        
        logger.info(f"\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        # Show raw file contents for debugging
        logger.info("\nShowing raw file contents for debugging:")
        
        try:
            with open(csv_2025_path, 'r') as f:
                content_2025 = f.read()[:500]  # First 500 chars
                logger.info(f"2025 file content:\n{content_2025}")
        except:
            logger.info("Could not read 2025 file")
            
        try:
            with open(csv_2024_path, 'r') as f:
                content_2024 = f.read()[:500]
                logger.info(f"2024 file content:\n{content_2024}")
        except:
            logger.info("Could not read 2024 file")

if __name__ == "__main__":
    asyncio.run(simple_yoy_test())
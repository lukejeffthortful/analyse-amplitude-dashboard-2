#!/usr/bin/env python3
"""
Verify 2024 Data Export
Re-export 2024 week 35 and compare with reference file
"""

import asyncio
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging
from appsflyer_optimized import AppsFlyerOptimizedExporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_2024_export():
    """Re-export 2024 data and verify against reference"""
    
    # Reference file from user
    reference_file = Path("/Users/lukejeffery/Downloads/my_dashboards_export_chart_unified_view_2024-08-25__2024-08-31_Europe_London_GBP_vpw4P.csv")
    
    # Existing exported file
    existing_file = Path("/Users/lukejeffery/dev/analyse-amplitude-dashboard-2/appsflyer_data/2024/week_35_20240826_20240901.csv")
    
    # Date range for 2024 week 35
    start_2024 = datetime(2024, 8, 25)  # Sunday Aug 25
    end_2024 = datetime(2024, 8, 31)    # Saturday Aug 31
    
    logger.info("🔍 Verifying 2024 Week 35 Data Export")
    logger.info(f"Date range: {start_2024} to {end_2024}")
    
    # First, let's analyze the reference file
    logger.info("\n📊 Analyzing Reference File (User Provided):")
    try:
        ref_df = pd.read_csv(reference_file)
        logger.info(f"  Shape: {ref_df.shape}")
        logger.info(f"  Columns: {list(ref_df.columns)}")
        logger.info(f"  First few rows:\n{ref_df.head()}")
        
        if 'installs appsflyer' in ref_df.columns:
            total_ref = ref_df['installs appsflyer'].sum()
            logger.info(f"  Total installs: {total_ref:,}")
            
            if 'media-source' in ref_df.columns:
                media_breakdown = ref_df.groupby('media-source')['installs appsflyer'].sum().sort_values(ascending=False)
                logger.info(f"\n  Media source breakdown:")
                for source, installs in media_breakdown.head(10).items():
                    logger.info(f"    {source}: {installs:,}")
    except Exception as e:
        logger.error(f"Could not read reference file: {str(e)}")
        return
    
    # Analyze existing exported file
    logger.info("\n📊 Analyzing Existing Exported File:")
    try:
        existing_df = pd.read_csv(existing_file)
        logger.info(f"  Shape: {existing_df.shape}")
        logger.info(f"  Columns: {list(existing_df.columns)}")
        
        if 'installs appsflyer' in existing_df.columns:
            total_existing = existing_df['installs appsflyer'].sum()
            logger.info(f"  Total installs: {total_existing:,}")
            
            # Check if totals match
            if total_ref and total_existing:
                if total_ref != total_existing:
                    logger.warning(f"  ⚠️ MISMATCH: Reference has {total_ref:,} installs, exported has {total_existing:,}")
                else:
                    logger.info(f"  ✓ Totals match: {total_ref:,}")
                    
    except Exception as e:
        logger.error(f"Could not read existing file: {str(e)}")
    
    # Re-export the data
    logger.info("\n🔄 Re-exporting 2024 Week 35 data...")
    exporter = AppsFlyerOptimizedExporter(download_dir="./appsflyer_verification")
    
    try:
        await exporter.start_session(headless=False)
        
        # Export specifically Aug 25-31, 2024
        new_csv = await exporter.export_date_range(start_2024, end_2024)
        
        logger.info(f"✓ Re-exported to: {new_csv}")
        
        # Analyze the new export
        logger.info("\n📊 Analyzing New Export:")
        new_df = pd.read_csv(new_csv)
        logger.info(f"  Shape: {new_df.shape}")
        logger.info(f"  First few rows:\n{new_df.head()}")
        
        if 'installs appsflyer' in new_df.columns:
            total_new = new_df['installs appsflyer'].sum()
            logger.info(f"  Total installs: {total_new:,}")
            
            # Compare with reference
            if total_ref and total_new:
                if total_ref != total_new:
                    logger.warning(f"\n⚠️ DATA MISMATCH DETECTED:")
                    logger.warning(f"  Reference total: {total_ref:,}")
                    logger.warning(f"  New export total: {total_new:,}")
                    logger.warning(f"  Difference: {total_new - total_ref:,}")
                    
                    # Show media source differences
                    if 'media-source' in new_df.columns and 'media-source' in ref_df.columns:
                        new_media = new_df.groupby('media-source')['installs appsflyer'].sum()
                        ref_media = ref_df.groupby('media-source')['installs appsflyer'].sum()
                        
                        all_sources = set(new_media.index) | set(ref_media.index)
                        
                        logger.info(f"\n  Media source comparison:")
                        for source in sorted(all_sources):
                            new_val = new_media.get(source, 0)
                            ref_val = ref_media.get(source, 0)
                            if new_val != ref_val:
                                logger.warning(f"    {source}: New={new_val:,} vs Ref={ref_val:,} (diff={new_val-ref_val:+,})")
                else:
                    logger.info(f"  ✅ DATA MATCHES! Both have {total_ref:,} installs")
                    
        # Save comparison summary
        logger.info("\n📋 Summary:")
        logger.info(f"  Reference file: {reference_file.name}")
        logger.info(f"  New export: {new_csv.name}")
        logger.info(f"  Files saved in: ./appsflyer_verification/")
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        
    finally:
        await exporter.close_session()

if __name__ == "__main__":
    asyncio.run(verify_2024_export())
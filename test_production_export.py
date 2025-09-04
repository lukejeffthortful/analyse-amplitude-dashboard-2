#!/usr/bin/env python3
"""
Test the production export script
"""

import asyncio
from datetime import datetime
from appsflyer_export_production import AppsFlyerExporter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_specific_dates():
    """Test with the exact dates from your recording"""
    exporter = AppsFlyerExporter()
    
    # Test with Aug 25-31, 2025 (from your recording)
    start_date = datetime(2025, 8, 25)
    end_date = datetime(2025, 8, 31)
    
    logger.info(f"\nTesting export for: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
    
    try:
        csv_path = await exporter.export_date_range(start_date, end_date, headless=False)
        logger.info(f"\n✅ Export successful! CSV saved to: {csv_path}")
        
        # Verify file exists and has content
        if csv_path.exists():
            file_size = csv_path.stat().st_size
            logger.info(f"File size: {file_size:,} bytes")
            
            # Read first few lines
            with open(csv_path, 'r') as f:
                lines = f.readlines()[:5]
                logger.info(f"First few lines of CSV:")
                for line in lines:
                    logger.info(f"  {line.strip()}")
        
    except Exception as e:
        logger.error(f"\n❌ Export failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_specific_dates())
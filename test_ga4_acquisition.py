#!/usr/bin/env python3
"""
Test GA4 Acquisition Data
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if GA4 is configured
if not os.getenv('GA4_APP_PROPERTY_ID'):
    logger.error("GA4_APP_PROPERTY_ID not found in environment")
    logger.info("Please add to .env file: GA4_APP_PROPERTY_ID=158472024")
    sys.exit(1)

if not os.getenv('GA4_SERVICE_ACCOUNT_PATH') and not os.getenv('GA4_SERVICE_ACCOUNT_JSON'):
    logger.error("GA4 service account credentials not found")
    logger.info("Please add to .env file one of:")
    logger.info("  GA4_SERVICE_ACCOUNT_PATH=/path/to/service-account.json")
    logger.info("  GA4_SERVICE_ACCOUNT_JSON='{json content}'")
    sys.exit(1)

try:
    from ga4_acquisition_handler import GA4AcquisitionHandler
    
    logger.info("Testing GA4 Acquisition Handler...")
    logger.info(f"App Property ID: {os.getenv('GA4_APP_PROPERTY_ID')}")
    
    # Initialize handler
    handler = GA4AcquisitionHandler()
    
    # Test with last week's data
    now = datetime.now()
    last_monday = now - timedelta(days=now.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    
    logger.info(f"\nFetching data for: {last_monday.strftime('%Y-%m-%d')} to {last_sunday.strftime('%Y-%m-%d')}")
    
    data = handler.get_new_users_by_channel(
        last_monday.strftime('%Y-%m-%d'),
        last_sunday.strftime('%Y-%m-%d')
    )
    
    if data:
        logger.info(f"\n✅ GA4 Acquisition Data Retrieved:")
        logger.info(f"   Total new users: {data['total_new_users']:,}")
        
        logger.info(f"\n📊 Top Acquisition Channels:")
        for channel, count in list(data['by_channel'].items())[:5]:
            logger.info(f"   {channel}: {count:,}")
        
        logger.info(f"\n📱 Top Sources:")
        for source, count in list(data['by_source'].items())[:5]:
            logger.info(f"   {source}: {count:,}")
        
        # Show sample detailed data
        if data['detailed_data']:
            logger.info(f"\n📋 Sample Detailed Data (first 3 rows):")
            for row in data['detailed_data'][:3]:
                logger.info(f"   {row['date']}: {row['channel']} / {row['source']} = {row['new_users']} users")
    
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    logger.info("Check that all dependencies are installed")
except Exception as e:
    logger.error(f"Test failed: {str(e)}")
    logger.info("\nTroubleshooting:")
    logger.info("1. Check GA4_APP_PROPERTY_ID is correct (should be 158472024)")
    logger.info("2. Ensure service account has Analytics Viewer role")
    logger.info("3. Verify service account JSON file path is correct")
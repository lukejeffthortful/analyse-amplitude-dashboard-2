#!/usr/bin/env python3
"""
Test ISO Week 35 Comparison (2025 vs 2024)
This should show different data for the same ISO week across years
"""

import asyncio
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging
from appsflyer_weekly_integration import AppsFlyerWeeklyAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_iso_week_35():
    """Test proper ISO week 35 comparison"""
    
    analyzer = AppsFlyerWeeklyAnalyzer()
    
    # Get ISO week 35 dates for both years
    monday_2024, sunday_2024 = analyzer.get_iso_week_dates(2024, 35)
    monday_2025, sunday_2025 = analyzer.get_iso_week_dates(2025, 35)
    
    logger.info("📅 ISO Week 35 Comparison")
    logger.info(f"2024 Week 35: {monday_2024.strftime('%Y-%m-%d')} to {sunday_2024.strftime('%Y-%m-%d')}")
    logger.info(f"2025 Week 35: {monday_2025.strftime('%Y-%m-%d')} to {sunday_2025.strftime('%Y-%m-%d')}")
    
    # First, remove any incorrect files
    incorrect_2024_file = Path("appsflyer_data/2024/week_35_20240826_20240901.csv")
    if incorrect_2024_file.exists():
        logger.info(f"Removing incorrect file: {incorrect_2024_file}")
        incorrect_2024_file.unlink()
    
    try:
        # Generate the weekly summary for week 35
        week_info = {
            'current_year': 2025,
            'current_week': 36,  # Simulating running in week 36
            'analysis_year': 2025,
            'analysis_week': 35
        }
        
        logger.info("\n🚀 Running Weekly AppsFlyer Analysis for ISO Week 35...")
        summary = await analyzer.generate_weekly_appsflyer_summary(
            week_info=week_info,
            headless=False
        )
        
        if 'error' not in summary:
            # Format the insights
            insights = analyzer.format_appsflyer_insights(summary)
            
            logger.info("\n" + "="*60)
            logger.info("ISO WEEK 35 COMPARISON RESULTS")
            logger.info("="*60)
            print(insights)
            logger.info("="*60)
            
            # Show detailed comparison
            current_data = summary['current_year_data']
            previous_data = summary['previous_year_data']
            
            logger.info(f"\n📊 Detailed Numbers:")
            logger.info(f"2025 Week 35 ({monday_2025.strftime('%b %d')} - {sunday_2025.strftime('%b %d')}): {current_data['total_installs']:,} installs")
            logger.info(f"2024 Week 35 ({monday_2024.strftime('%b %d')} - {sunday_2024.strftime('%b %d')}): {previous_data['total_installs']:,} installs")
            
            if current_data['total_installs'] == previous_data['total_installs']:
                logger.warning("\n⚠️ WARNING: Data appears identical! This suggests wrong data was pulled.")
            else:
                diff = current_data['total_installs'] - previous_data['total_installs']
                pct = (diff / previous_data['total_installs'] * 100) if previous_data['total_installs'] > 0 else 0
                logger.info(f"\n✅ Data shows real differences: {diff:+,} ({pct:+.1f}%) change")
            
            # Show top media sources
            logger.info(f"\n📱 Top Media Sources 2025:")
            for source, installs in list(current_data['media_sources'].items())[:5]:
                logger.info(f"  {source}: {installs:,}")
                
            logger.info(f"\n📱 Top Media Sources 2024:")
            for source, installs in list(previous_data['media_sources'].items())[:5]:
                logger.info(f"  {source}: {installs:,}")
                
        else:
            logger.error(f"Summary failed: {summary['error']}")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_iso_week_35())
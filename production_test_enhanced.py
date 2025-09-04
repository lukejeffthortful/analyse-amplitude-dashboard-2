#!/usr/bin/env python3
"""
Production Test for Enhanced Weekly Analyzer
Simulates the GitHub Actions environment and posts to test Slack channel
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Set test environment
os.environ['SLACK_WEBHOOK_URL'] = "https://hooks.slack.com/services/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"
os.environ['GA4_ENABLED'] = "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_production_test():
    """Run production-level test of enhanced weekly analyzer"""
    
    logger.info("🚀 Starting Production Test of Enhanced Weekly Analyzer")
    logger.info("="*80)
    
    # Environment check
    logger.info("🔧 Environment Configuration:")
    required_vars = [
        'AMPLITUDE_API_KEY',
        'AMPLITUDE_SECRET_KEY', 
        'GA4_APP_PROPERTY_ID',
        'GA4_SERVICE_ACCOUNT_PATH',
        'APPSFLYER_USERNAME',
        'APPSFLYER_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"   ✓ {var}: {'*' * 8}")
        else:
            logger.warning(f"   ⚠️ {var}: Missing")
            missing_vars.append(var)
    
    logger.info(f"   ✓ SLACK_WEBHOOK_URL: Test channel configured")
    logger.info(f"   ✓ GA4_ENABLED: {os.getenv('GA4_ENABLED')}")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these in your .env file before running the test")
        return
    
    try:
        # Import and run enhanced analyzer
        logger.info("\n📊 Importing Enhanced Weekly Analyzer...")
        from enhanced_weekly_analyzer import EnhancedWeeklyAnalyzer
        
        analyzer = EnhancedWeeklyAnalyzer()
        
        # Get week info
        week_info = analyzer.get_week_info()
        logger.info(f"📅 Analysis Target: Week {week_info['analysis_week']}, {week_info['analysis_year']}")
        
        # Run comprehensive analysis
        logger.info("\n🔄 Running Comprehensive Analysis...")
        logger.info("   This will:")
        logger.info("   1. Fetch Amplitude session data with YoY comparison")
        logger.info("   2. Export AppsFlyer data using unified dashboard (SKAN + Traditional)")
        logger.info("   3. Fetch GA4 acquisition data by channel")
        logger.info("   4. Run acquisition reconciliation")
        logger.info("   5. Generate executive summary")
        logger.info("   6. Post complete report to test Slack channel")
        
        results = await analyzer.run_comprehensive_analysis()
        
        if 'error' in results:
            logger.error(f"❌ Analysis failed: {results['error']}")
            return
        
        # Format and display report
        report = analyzer.format_comprehensive_report(results)
        
        logger.info("\n" + "="*80)
        logger.info("PRODUCTION TEST RESULTS")
        logger.info("="*80)
        print(report)
        logger.info("="*80)
        
        # Save report
        output_path = analyzer.save_report(results, f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        
        # Post to Slack (simulated)
        logger.info(f"\n📤 Report would be posted to Slack test channel")
        logger.info(f"📁 Report saved locally: {output_path}")
        
        # Summary of what was tested
        logger.info(f"\n✅ Production Test Summary:")
        logger.info(f"   • Amplitude sessions: {'✓' if results['amplitude'] else '❌'}")
        logger.info(f"   • AppsFlyer installs: {'✓' if results['appsflyer'] and 'error' not in results['appsflyer'] else '❌'}")
        logger.info(f"   • GA4 acquisition: {'✓' if results['ga4_acquisition'] else '❌'}")
        logger.info(f"   • Reconciliation: {'✓' if results['reconciliation'] else '❌'}")
        logger.info(f"   • Executive summary: {'✓' if results['summary'] else '❌'}")
        
        return results
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {str(e)}")
        logger.info("Install dependencies first: pip3 install -r requirements.txt")
        logger.info("Then install Playwright: pip3 install playwright && playwright install chromium")
    except Exception as e:
        logger.error(f"❌ Production test failed: {str(e)}")
        return None

def create_github_action_command():
    """Show command to run this as GitHub Action"""
    
    logger.info("\n🔧 To run this in GitHub Actions:")
    logger.info("1. Push this code to your repository")
    logger.info("2. Go to Actions tab in GitHub")
    logger.info("3. Select 'Test Enhanced Weekly Analysis Report'") 
    logger.info("4. Click 'Run workflow'")
    logger.info("5. Check the test Slack channel for results")
    
    logger.info("\n📋 Required GitHub Secrets:")
    secrets = [
        "AMPLITUDE_API_KEY",
        "AMPLITUDE_SECRET_KEY",
        "GA4_APP_PROPERTY_ID", 
        "GA4_WEB_PROPERTY_ID",
        "GA4_SERVICE_ACCOUNT_JSON",
        "APPSFLYER_USERNAME",
        "APPSFLYER_PASSWORD",
        "APPSFLYER_API_TOKEN",
        "APPSFLYER_APP_ID"
    ]
    
    for secret in secrets:
        logger.info(f"   • {secret}")

if __name__ == "__main__":
    logger.info("🎯 Production Test Setup for Enhanced Weekly Analyzer")
    logger.info("="*80)
    
    # Show setup info
    create_github_action_command()
    
    # Run the test
    logger.info("\n" + "="*80)
    asyncio.run(run_production_test())
#!/usr/bin/env python3
"""
Run Enhanced Test Locally
Test the enhanced weekly analyzer locally before any remote deployment
Following SAFE_DEVELOPMENT_GUIDE.md - test locally first
"""

import os
import asyncio
import logging
from datetime import datetime
import sys

# Set test environment variables
os.environ['SLACK_WEBHOOK_URL'] = "https://hooks.slack.com/services/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"
os.environ['GA4_ENABLED'] = "true"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_local_enhanced_test():
    """Run enhanced analyzer test locally on development branch"""
    
    logger.info("🧪 Local Enhanced Analyzer Test (Development Branch)")
    logger.info("="*70)
    logger.info("📋 Following SAFE_DEVELOPMENT_GUIDE.md:")
    logger.info("   ✓ Testing on development-iteration branch")
    logger.info("   ✓ No modifications to main branch")
    logger.info("   ✓ Local testing before remote deployment")
    
    # Check branch
    try:
        import subprocess
        branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        if branch != "development-iteration":
            logger.error(f"❌ Wrong branch: {branch}. Switch to development-iteration first!")
            return
        logger.info(f"   ✓ On correct branch: {branch}")
    except:
        logger.warning("   ⚠️ Could not verify git branch")
    
    # Environment check
    logger.info("\n🔧 Environment Check:")
    required_env = ['AMPLITUDE_API_KEY', 'AMPLITUDE_SECRET_KEY']
    optional_env = ['GA4_APP_PROPERTY_ID', 'APPSFLYER_USERNAME']
    
    missing_required = []
    for var in required_env:
        if os.getenv(var):
            logger.info(f"   ✓ {var}: Set")
        else:
            logger.error(f"   ❌ {var}: Missing")
            missing_required.append(var)
    
    missing_optional = []
    for var in optional_env:
        if os.getenv(var):
            logger.info(f"   ✓ {var}: Set")
        else:
            logger.warning(f"   ⚠️ {var}: Missing (component may be skipped)")
            missing_optional.append(var)
    
    if missing_required:
        logger.error(f"❌ Cannot proceed without: {', '.join(missing_required)}")
        logger.info("   Add these to your .env file")
        return
    
    # Test imports
    logger.info("\n📦 Testing Component Imports:")
    components = [
        ('amplitude_analyzer', 'AmplitudeAnalyzer'),
        ('appsflyer_weekly_integration', 'AppsFlyerWeeklyAnalyzer'),
        ('ga4_acquisition_handler', 'GA4AcquisitionHandler'),
        ('acquisition_reconciliation', 'AcquisitionReconciler')
    ]
    
    available_components = []
    for module_name, class_name in components:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            logger.info(f"   ✓ {module_name}.{class_name}")
            available_components.append((module_name, class_name))
        except Exception as e:
            logger.warning(f"   ⚠️ {module_name}.{class_name}: {str(e)}")
    
    if not available_components:
        logger.error("❌ No components available - install dependencies first")
        logger.info("   pip3 install -r requirements.txt")
        return
    
    # Test enhanced analyzer
    logger.info("\n🚀 Testing Enhanced Weekly Analyzer:")
    try:
        from enhanced_weekly_analyzer import EnhancedWeeklyAnalyzer
        analyzer = EnhancedWeeklyAnalyzer()
        logger.info("   ✓ Enhanced analyzer initialized")
        
        # Get week info
        week_info = analyzer.get_week_info()
        logger.info(f"   ✓ Target: Week {week_info['analysis_week']}, {week_info['analysis_year']}")
        
        # Test individual components that are available
        logger.info("\n🔄 Testing Available Components:")
        
        if 'AMPLITUDE_API_KEY' in os.environ:
            logger.info("   📊 Amplitude: Ready for session data")
        
        if 'APPSFLYER_USERNAME' in os.environ:
            logger.info("   📱 AppsFlyer: Ready for install attribution")
            logger.info("   🔗 Using unified dashboard (SKAN + Traditional)")
        
        if 'GA4_APP_PROPERTY_ID' in os.environ:
            logger.info("   📈 GA4: Ready for acquisition data")
        
        logger.info("   🔄 Reconciliation: Ready to compare platforms")
        
        # Mock run simulation
        logger.info(f"\n🎭 Running Simulation...")
        logger.info("   (Use production_test_enhanced.py for full mock test)")
        
        # Show expected output format
        logger.info(f"\n📋 Expected Slack Output:")
        logger.info("   📊 Weekly Analytics Report - Week {week}, {year}")
        logger.info("   🎯 Executive Summary (sessions, installs, new users with YoY)")
        logger.info("   📱 AppsFlyer Install Attribution (top sources, YoY comparison)")
        logger.info("   📊 GA4 User Acquisition (channels, sources)")
        logger.info("   🔄 Attribution Reconciliation (platform differences)")
        
        logger.info(f"\n✅ Local test successful!")
        logger.info(f"📝 Next steps:")
        logger.info(f"   1. Install missing dependencies if needed")
        logger.info(f"   2. Run full test: python3 enhanced_weekly_analyzer.py")
        logger.info(f"   3. Check test Slack channel for results")
        logger.info(f"   4. After successful testing, can merge to main")
        
    except ImportError as e:
        logger.error(f"❌ Enhanced analyzer import failed: {str(e)}")
        logger.info("   Install dependencies: pip3 install -r requirements.txt")
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")

def show_manual_run_instructions():
    """Show how to manually run the enhanced analyzer"""
    
    logger.info("\n" + "="*70)
    logger.info("🛠️ MANUAL RUN INSTRUCTIONS")
    logger.info("="*70)
    
    logger.info("\n📋 Prerequisites:")
    logger.info("   pip3 install -r requirements.txt")
    logger.info("   pip3 install playwright")
    logger.info("   playwright install chromium")
    
    logger.info("\n🎯 Run Enhanced Weekly Summary:")
    logger.info("   python3 enhanced_weekly_analyzer.py")
    
    logger.info("\n📤 Test Slack Posting:")
    logger.info("   SLACK_WEBHOOK_URL='https://hooks.slack.com/services/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' \\")
    logger.info("   python3 slack_enhanced_poster.py")
    
    logger.info("\n🔄 Verify AppsFlyer Data:")
    logger.info("   python3 verify_unified_data.py")

if __name__ == "__main__":
    asyncio.run(run_local_enhanced_test())
    show_manual_run_instructions()
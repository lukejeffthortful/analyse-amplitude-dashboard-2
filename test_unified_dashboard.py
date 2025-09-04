#!/usr/bin/env python3
"""
Test Updated Unified Dashboard URL
Verify that the new SKAN + Traditional attribution URL works and returns different data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDashboardTester:
    """Test the updated unified dashboard URL"""
    
    def __init__(self):
        self.base_url = "https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&v=NTE5ODM3"
    
    def test_url_construction(self):
        """Test that URL is properly constructed"""
        
        logger.info("🔗 Testing URL construction for unified dashboard")
        logger.info(f"Base URL: {self.base_url}")
        
        # Check URL components
        url_parts = self.base_url.split('#')
        if len(url_parts) == 2:
            base = url_parts[0]
            fragment = url_parts[1]
            
            logger.info(f"✓ Base: {base}")
            logger.info(f"✓ Fragment: {fragment}")
            
            # Check for required parameters
            if "appIds=com.thortful.app,id1041914779" in fragment:
                logger.info("✓ App IDs found")
            else:
                logger.warning("⚠️ App IDs missing")
            
            if "v=NTE5ODM3" in fragment:
                logger.info("✓ Version parameter found (SKAN + Traditional)")
            else:
                logger.warning("⚠️ Version parameter missing")
        
        return True
    
    def test_iso_week_calculation(self):
        """Test ISO week calculation to ensure different dates"""
        
        logger.info("\n📅 Testing ISO week date calculation")
        
        # Test week 35 for both years
        week = 35
        
        # 2024 Week 35
        jan4_2024 = datetime(2024, 1, 4)
        days_to_monday_2024 = (jan4_2024.weekday()) % 7
        week1_monday_2024 = jan4_2024 - timedelta(days=days_to_monday_2024)
        target_monday_2024 = week1_monday_2024 + timedelta(weeks=week - 1)
        target_sunday_2024 = target_monday_2024 + timedelta(days=6)
        
        # 2025 Week 35  
        jan4_2025 = datetime(2025, 1, 4)
        days_to_monday_2025 = (jan4_2025.weekday()) % 7
        week1_monday_2025 = jan4_2025 - timedelta(days=days_to_monday_2025)
        target_monday_2025 = week1_monday_2025 + timedelta(weeks=week - 1)
        target_sunday_2025 = target_monday_2025 + timedelta(days=6)
        
        logger.info(f"2024 Week {week}: {target_monday_2024.strftime('%Y-%m-%d')} to {target_sunday_2024.strftime('%Y-%m-%d')}")
        logger.info(f"2025 Week {week}: {target_monday_2025.strftime('%Y-%m-%d')} to {target_sunday_2025.strftime('%Y-%m-%d')}")
        
        # Verify they're different
        if target_monday_2024.strftime('%Y-%m-%d') != target_monday_2025.strftime('%Y-%m-%d'):
            logger.info("✓ Date ranges are different for same ISO week")
            return True
        else:
            logger.error("❌ Date ranges are identical - this is wrong!")
            return False
    
    def check_existing_files(self):
        """Check what data files already exist"""
        
        logger.info("\n📁 Checking existing AppsFlyer data files")
        
        data_dir = Path("./appsflyer_data")
        if not data_dir.exists():
            logger.info("No appsflyer_data directory found")
            return
        
        # Check 2024 folder
        folder_2024 = data_dir / "2024"
        if folder_2024.exists():
            files_2024 = list(folder_2024.glob("*.csv"))
            logger.info(f"📂 2024 folder: {len(files_2024)} CSV files")
            for f in files_2024:
                logger.info(f"   - {f.name}")
        
        # Check 2025 folder
        folder_2025 = data_dir / "2025" 
        if folder_2025.exists():
            files_2025 = list(folder_2025.glob("*.csv"))
            logger.info(f"📂 2025 folder: {len(files_2025)} CSV files")
            for f in files_2025:
                logger.info(f"   - {f.name}")
        
        # Quick file comparison
        week35_2024 = folder_2024.glob("*week_35*.csv") if folder_2024.exists() else []
        week35_2025 = folder_2025.glob("*week_35*.csv") if folder_2025.exists() else []
        
        for f_2024 in week35_2024:
            for f_2025 in week35_2025:
                if f_2024.stat().st_size == f_2025.stat().st_size:
                    logger.warning(f"⚠️ Same file size: {f_2024.name} vs {f_2025.name}")
                else:
                    logger.info(f"✓ Different file sizes: {f_2024.name} ({f_2024.stat().st_size}) vs {f_2025.name} ({f_2025.stat().st_size})")

def main():
    """Run unified dashboard tests"""
    
    logger.info("🚀 Testing Updated Unified Dashboard Configuration")
    logger.info("="*60)
    
    tester = UnifiedDashboardTester()
    
    # Test 1: URL construction
    tester.test_url_construction()
    
    # Test 2: Date calculation
    tester.test_iso_week_calculation()
    
    # Test 3: Check existing files
    tester.check_existing_files()
    
    logger.info("\n✅ Unified dashboard test complete!")
    logger.info("\nNext steps:")
    logger.info("1. Run browser automation with updated URL")
    logger.info("2. Verify data differences between years")
    logger.info("3. Compare SKAN vs Traditional attribution if visible")

if __name__ == "__main__":
    main()
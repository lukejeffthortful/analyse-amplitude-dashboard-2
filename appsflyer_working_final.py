#!/usr/bin/env python3
"""
AppsFlyer Working Export - Based on Successful Debug
"""

import os
import re
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerExporter:
    def __init__(self, download_dir="./appsflyer_exports"):
        self.username = os.getenv('APPSFLYER_USERNAME')
        self.password = os.getenv('APPSFLYER_PASSWORD')
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    async def export_date_range(self, start_date, end_date, headless=False):
        """Export CSV for a specific date range"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                downloads_path=str(self.download_dir)
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Login (exactly as recorded)
                logger.info("Logging in to AppsFlyer...")
                await page.goto("https://hq1.appsflyer.com/auth/login")
                
                await page.get_by_role("textbox", name="user-email").click()
                await page.get_by_role("textbox", name="user-email").fill(self.username)
                await page.get_by_role("textbox", name="user-email").press("Tab")
                await page.get_by_role("textbox", name="Password").fill(self.password)
                await page.get_by_role("button", name="login").click()
                
                # Wait for login
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                logger.info("✓ Login successful")
                
                # Step 2: Navigate to Marketing Overview (exactly as recorded)
                logger.info("Navigating to Marketing Overview...")
                await page.get_by_role("link", name="Marketing Overview").click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                logger.info("✓ Marketing Overview loaded")
                
                # Step 3: Open date picker (based on what we see in the screenshot)
                logger.info(f"Setting date range: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
                
                # Look for the date range button (visible in screenshot: "Last 30 days Aug 5, 2025 - Sep 3, 2025")
                date_button = page.locator('button:has-text("Last"):has-text("days"):has-text("Aug"):has-text("2025")')
                
                if not await date_button.is_visible():
                    # Alternative: any button with current date range
                    date_button = page.locator('button:has-text("Aug"):has-text("2025")')
                
                if not await date_button.is_visible():
                    # Fallback: generic date picker button
                    date_button = page.locator('button[aria-label*="date"], [data-qa-id*="date"]').first
                
                await date_button.click()
                await asyncio.sleep(1)
                logger.info("✓ Date picker opened")
                
                # Step 4: Select specific dates (like in recording)
                start_day = str(start_date.day)
                end_day = str(end_date.day)
                
                # Click start date
                await page.get_by_role("gridcell", name=start_day).first.click()
                logger.info(f"✓ Selected start date: {start_day}")
                await asyncio.sleep(0.5)
                
                # Click end date
                await page.get_by_role("gridcell", name=end_day).first.click() 
                logger.info(f"✓ Selected end date: {end_day}")
                await asyncio.sleep(0.5)
                
                # Apply date range
                await page.get_by_role("button", name="Apply").click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                logger.info("✓ Date range applied")
                
                # Step 5: Export CSV (exactly as recorded)
                logger.info("Initiating CSV export...")
                
                # Click the dots menu on the platform chart widget
                await page.get_by_test_id("platform-chart:7").get_by_role("button", name="dots icon").click()
                await asyncio.sleep(1)
                
                # Export CSV with download handling
                async with page.expect_download() as download_info:
                    await page.get_by_text("Export CSV").click()
                    logger.info("✓ Export clicked, waiting for download...")
                
                download = await download_info.value
                
                # Save with meaningful filename
                filename = f"appsflyer_marketing_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                save_path = self.download_dir / filename
                await download.save_as(save_path)
                
                logger.info(f"✅ CSV exported successfully: {save_path}")
                return save_path
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                await page.screenshot(path=self.download_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                raise
                
            finally:
                await context.close()
                await browser.close()
    
    async def export_last_week(self, headless=False):
        """Export data for the previous week (Monday to Sunday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        return await self.export_date_range(last_monday, last_sunday, headless)

async def test_export():
    """Test the export functionality"""
    exporter = AppsFlyerExporter()
    
    # Test with last week
    try:
        logger.info("\n🚀 Testing AppsFlyer automated export...")
        csv_path = await exporter.export_last_week(headless=False)
        
        if csv_path and csv_path.exists():
            file_size = csv_path.stat().st_size
            logger.info(f"\n✅ SUCCESS! Export completed:")
            logger.info(f"   File: {csv_path}")
            logger.info(f"   Size: {file_size:,} bytes")
            
            # Show first few lines
            with open(csv_path, 'r') as f:
                lines = f.readlines()[:3]
                logger.info(f"   Content preview:")
                for line in lines:
                    logger.info(f"     {line.strip()}")
        
    except Exception as e:
        logger.error(f"\n❌ Export failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_export())
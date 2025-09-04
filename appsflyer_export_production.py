#!/usr/bin/env python3
"""
AppsFlyer Automated CSV Export - Production Version
Based on recorded user interaction
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, expect
import logging
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerExporter:
    def __init__(self, download_dir="./appsflyer_exports"):
        self.username = os.getenv('APPSFLYER_USERNAME')
        self.password = os.getenv('APPSFLYER_PASSWORD')
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    async def export_date_range(self, start_date, end_date, headless=True):
        """Export CSV for a specific date range"""
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=headless,
                downloads_path=str(self.download_dir)
            )
            
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Step 1: Login
                logger.info("Navigating to AppsFlyer login...")
                await page.goto("https://hq1.appsflyer.com/auth/login")
                
                # Use the exact selectors from recording
                await page.get_by_role("textbox", name="user-email").click()
                await page.get_by_role("textbox", name="user-email").fill(self.username)
                await page.get_by_role("textbox", name="user-email").press("Tab")
                await page.get_by_role("textbox", name="Password").fill(self.password)
                await page.get_by_role("button", name="login").click()
                
                # Wait for login to complete
                logger.info("Logging in...")
                await page.wait_for_load_state('networkidle')
                
                # Step 2: Navigate to Marketing Overview
                logger.info("Navigating to Marketing Overview...")
                await page.get_by_role("link", name="Marketing Overview").click()
                await page.wait_for_load_state('networkidle')
                
                # Step 3: Open date picker
                logger.info(f"Setting date range: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
                
                # Click on the date range button (it has dynamic text, so we use a partial match)
                date_button = page.get_by_role("button", name=re.compile(r"Last \d+ days"))
                if not await date_button.is_visible():
                    # Fallback: look for button containing date text
                    date_button = page.locator('button:has-text("Aug"):has-text("2025")')
                
                await date_button.click()
                await asyncio.sleep(1)  # Wait for calendar to open
                
                # Step 4: Select dates dynamically
                start_day = str(start_date.day)
                end_day = str(end_date.day)
                
                # Click start date - use first occurrence
                await page.get_by_role("gridcell", name=start_day).first.click()
                logger.info(f"Selected start date: {start_day}")
                await asyncio.sleep(0.5)
                
                # Click end date - use first occurrence  
                await page.get_by_role("gridcell", name=end_day).first.click()
                logger.info(f"Selected end date: {end_day}")
                await asyncio.sleep(0.5)
                
                # Apply date range
                await page.get_by_role("button", name="Apply").click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)  # Wait for data to load
                
                # Step 5: Export CSV
                logger.info("Initiating CSV export...")
                
                # Use the exact selector from your recording
                widget_menu = page.get_by_test_id("platform-chart:7").get_by_role("button", name="dots icon")
                
                if await widget_menu.is_visible():
                    await widget_menu.click()
                    await asyncio.sleep(1)
                    
                    # Click Export CSV with download handling
                    async with page.expect_download() as download_info:
                        await page.get_by_text("Export CSV").click()
                        logger.info("Export clicked, waiting for download...")
                    
                    download = await download_info.value
                    
                    # Save with meaningful filename
                    filename = f"appsflyer_marketing_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                    save_path = self.download_dir / filename
                    await download.save_as(save_path)
                    
                    logger.info(f"✓ CSV exported successfully: {save_path}")
                    return save_path
                else:
                    # Fallback: try other widget menus
                    logger.info("Primary widget menu not found, trying alternatives...")
                    all_dots_buttons = await page.get_by_role("button", name="dots icon").all()
                    
                    for i, button in enumerate(all_dots_buttons[:3]):  # Try first 3
                        try:
                            if await button.is_visible():
                                await button.click()
                                await asyncio.sleep(1)
                                
                                if await page.get_by_text("Export CSV").is_visible():
                                    async with page.expect_download() as download_info:
                                        await page.get_by_text("Export CSV").click()
                                    
                                    download = await download_info.value
                                    filename = f"appsflyer_marketing_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                                    save_path = self.download_dir / filename
                                    await download.save_as(save_path)
                                    
                                    logger.info(f"✓ CSV exported successfully: {save_path}")
                                    return save_path
                                else:
                                    # Close menu and try next
                                    await page.click('body', position={'x': 100, 'y': 100})
                        except:
                            continue
                    
                    raise Exception("Could not find any widget with export option")
                    
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                await page.screenshot(path=self.download_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                raise
                
            finally:
                await context.close()
                await browser.close()
    
    async def export_last_week(self, headless=True):
        """Export data for the previous week (Monday to Sunday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        return await self.export_date_range(last_monday, last_sunday, headless)
    
    async def export_custom_week(self, year, month, start_day, end_day, headless=True):
        """Export data for a custom date range"""
        start_date = datetime(year, month, start_day)
        end_date = datetime(year, month, end_day)
        
        return await self.export_date_range(start_date, end_date, headless)

async def main():
    """Test the export with different date ranges"""
    exporter = AppsFlyerExporter()
    
    print("\nAppsFlyer Export Options:")
    print("1. Export last week")
    print("2. Export Aug 25-31, 2025 (from recording)")
    print("3. Export custom date range")
    
    # For automated testing, let's export last week
    try:
        logger.info("Starting export for last week...")
        csv_path = await exporter.export_last_week(headless=False)  # Set to True for production
        logger.info(f"\n✅ Export complete! CSV saved to: {csv_path}")
        
        # Check file size
        file_size = csv_path.stat().st_size
        logger.info(f"File size: {file_size:,} bytes")
        
    except Exception as e:
        logger.error(f"\n❌ Export failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
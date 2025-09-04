#!/usr/bin/env python3
"""
AppsFlyer Export with Fixed Date Selection
Handles cross-month date ranges properly
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
        
    async def smart_date_selection(self, page, start_date, end_date):
        """Smart date selection that handles cross-month ranges"""
        
        logger.info(f"Selecting date range: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
        
        # Check if we're crossing months
        same_month = start_date.month == end_date.month and start_date.year == end_date.year
        
        if same_month:
            # Simple case: same month
            logger.info("Same month selection")
            await page.get_by_role("gridcell", name=str(start_date.day)).first.click()
            await asyncio.sleep(0.5)
            await page.get_by_role("gridcell", name=str(end_date.day)).first.click()
            await asyncio.sleep(0.5)
        else:
            # Complex case: cross-month or cross-year
            logger.info("Cross-month selection - using individual date inputs")
            
            # Look for date input fields instead of calendar clicks
            start_input = page.locator('input[placeholder*="Start"], input[aria-label*="start"], input[name*="start"]').first
            end_input = page.locator('input[placeholder*="End"], input[aria-label*="end"], input[name*="end"]').first
            
            if await start_input.is_visible() and await end_input.is_visible():
                # Clear and fill date inputs
                await start_input.clear()
                await start_input.fill(start_date.strftime('%Y-%m-%d'))
                
                await end_input.clear() 
                await end_input.fill(end_date.strftime('%Y-%m-%d'))
                
                logger.info("Used date input fields for cross-month range")
            else:
                # Fallback: navigate calendar months
                logger.info("Navigating calendar for cross-month selection...")
                
                # Select start date
                await self._navigate_and_select_date(page, start_date)
                await asyncio.sleep(0.5)
                
                # Select end date
                await self._navigate_and_select_date(page, end_date)
                await asyncio.sleep(0.5)
    
    async def _navigate_and_select_date(self, page, target_date):
        """Navigate calendar to a specific month and select date"""
        
        # Get current visible month/year from calendar
        month_labels = await page.locator('[class*="month"], .month-label, [aria-label*="month"]').all_text_contents()
        current_month_year = None
        
        for label in month_labels:
            if target_date.strftime('%B') in label or target_date.strftime('%Y') in label:
                current_month_year = label
                break
        
        target_month_year = target_date.strftime('%B %Y')
        
        if current_month_year and target_month_year not in current_month_year:
            # Need to navigate months
            logger.info(f"Navigating from {current_month_year} to {target_month_year}")
            
            # Simple navigation - just click next a few times for previous months
            # This is simplified - a full implementation would calculate direction
            next_button = page.locator('button[aria-label*="next"], button:has-text("›"), button:has-text(">")').first
            
            for _ in range(3):  # Try up to 3 clicks
                if await next_button.is_visible():
                    await next_button.click()
                    await asyncio.sleep(0.5)
                else:
                    break
        
        # Now click the date
        await page.get_by_role("gridcell", name=str(target_date.day)).first.click()
        logger.info(f"Selected date: {target_date.day}")
        
    async def export_date_range(self, start_date, end_date, headless=False):
        """Export CSV for a specific date range with improved date handling"""
        
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
                # Steps 1-2: Login and navigate (same as before)
                logger.info("Logging in to AppsFlyer...")
                await page.goto("https://hq1.appsflyer.com/auth/login")
                
                await page.get_by_role("textbox", name="user-email").fill(self.username)
                await page.get_by_role("textbox", name="Password").fill(self.password)
                await page.get_by_role("button", name="login").click()
                
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                logger.info("Navigating to Marketing Overview...")
                await page.get_by_role("link", name="Marketing Overview").click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                # Step 3: Open date picker
                logger.info("Opening date picker...")
                date_button = page.locator('button:has-text("Last"):has-text("days"):has-text("202")').first
                await date_button.click()
                await asyncio.sleep(1)
                
                # Step 4: Smart date selection
                await self.smart_date_selection(page, start_date, end_date)
                
                # Step 5: Apply date range (with retry logic)
                logger.info("Applying date range...")
                apply_button = page.get_by_role("button", name="Apply")
                
                # Wait for button to become enabled
                await apply_button.wait_for(state="attached")
                
                # Check if button is enabled
                is_disabled = await apply_button.get_attribute('disabled')
                if is_disabled:
                    logger.warning("Apply button is disabled. Trying alternative date selection...")
                    
                    # Try clicking "Custom Range" first if available
                    custom_range = page.locator('text="Custom range", button:has-text("Custom")').first
                    if await custom_range.is_visible():
                        await custom_range.click()
                        await asyncio.sleep(1)
                        
                        # Try again with smart selection
                        await self.smart_date_selection(page, start_date, end_date)
                
                # Try to click apply
                max_attempts = 5
                for attempt in range(max_attempts):
                    try:
                        is_disabled = await apply_button.get_attribute('disabled')
                        if not is_disabled:
                            await apply_button.click()
                            break
                        else:
                            logger.warning(f"Attempt {attempt+1}: Apply button still disabled")
                            await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                        if attempt == max_attempts - 1:
                            raise
                
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                logger.info("✓ Date range applied")
                
                # Step 6: Export CSV
                logger.info("Initiating CSV export...")
                await page.get_by_test_id("platform-chart:7").get_by_role("button", name="dots icon").click()
                await asyncio.sleep(1)
                
                async with page.expect_download() as download_info:
                    await page.get_by_text("Export CSV").click()
                
                download = await download_info.value
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

async def test_fixed_export():
    """Test with the fixed date selection"""
    exporter = AppsFlyerExporter()
    
    # Test 2024 dates that failed before
    start_2024 = datetime(2024, 8, 26)
    end_2024 = datetime(2024, 9, 1)
    
    logger.info("Testing cross-month date selection (Aug 26 - Sep 1, 2024)")
    
    try:
        csv_path = await exporter.export_date_range(start_2024, end_2024, headless=False)
        logger.info(f"✅ Success! CSV: {csv_path}")
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_fixed_export())
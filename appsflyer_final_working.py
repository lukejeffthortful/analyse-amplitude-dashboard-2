#!/usr/bin/env python3
"""
AppsFlyer Final Working Export - Using Direct Date Input
Based on corrected date input method
"""

import os
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
        """Export CSV for a specific date range using direct date input"""
        
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
                # Step 1: Login
                logger.info("Logging in to AppsFlyer...")
                await page.goto("https://hq1.appsflyer.com/auth/login")
                
                await page.get_by_role("textbox", name="user-email").fill(self.username)
                await page.get_by_role("textbox", name="Password").fill(self.password)
                await page.get_by_role("button", name="login").click()
                
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                logger.info("✓ Login successful")
                
                # Step 2: Navigate to Marketing Overview
                logger.info("Navigating to Marketing Overview...")
                await page.get_by_role("link", name="Marketing Overview").click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                logger.info("✓ Marketing Overview loaded")
                
                # Step 3: Open date picker using the correct button pattern
                logger.info(f"Setting date range: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
                
                # Click the date range button (pattern: "Last week Aug 25, 2025 - Aug 31,")
                # Use a more flexible selector to find the current date range button
                date_range_selectors = [
                    page.get_by_role("button", name="Last week"),
                    page.get_by_role("button", name="Last 7 days"),
                    page.locator('button:has-text("Last"):has-text("202")'),  # Contains "Last" and a year
                    page.locator('button[aria-label*="date"]').first
                ]
                
                date_button_clicked = False
                for selector in date_range_selectors:
                    try:
                        if await selector.is_visible():
                            await selector.click()
                            date_button_clicked = True
                            logger.info("✓ Date picker opened")
                            break
                    except:
                        continue
                
                if not date_button_clicked:
                    raise Exception("Could not find date range button")
                
                await asyncio.sleep(1)
                
                # Step 4: Use direct date input (MM/DD/YYYY format)
                logger.info("Filling date inputs...")
                
                # Format dates as MM/DD/YY (note the 2-digit year as shown in your example)
                start_date_str = start_date.strftime("%m/%d/%y")
                end_date_str = end_date.strftime("%m/%d/%y")
                
                logger.info(f"Start date input: {start_date_str}")
                logger.info(f"End date input: {end_date_str}")
                
                # Fill start date (first textbox)
                await page.get_by_role("textbox", name="MM/DD/YYYY").first.click()
                await page.get_by_role("textbox", name="MM/DD/YYYY").first.fill(start_date_str)
                await asyncio.sleep(0.5)
                
                # Fill end date (second textbox)
                await page.get_by_role("textbox", name="MM/DD/YYYY").nth(1).click()
                await page.get_by_role("textbox", name="MM/DD/YYYY").nth(1).fill(end_date_str)
                await asyncio.sleep(0.5)
                
                # Apply date range
                await page.get_by_role("button", name="Apply").click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                logger.info("✓ Date range applied")
                
                # Step 5: Export CSV
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
    
    async def export_last_week(self, headless=False):
        """Export data for the previous week (Monday to Sunday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        return await self.export_date_range(last_monday, last_sunday, headless)
    
    async def export_custom_dates(self, start_date_str, end_date_str, headless=False):
        """Export for custom date strings (YYYY-MM-DD format)"""
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        return await self.export_date_range(start_date, end_date, headless)

async def test_cross_year_export():
    """Test the improved date input with cross-year range"""
    exporter = AppsFlyerExporter()
    
    # Test different date ranges
    test_cases = [
        ("2025-08-25", "2025-08-31", "Current week 2025"),
        ("2024-08-25", "2024-08-31", "Same week 2024"),
        ("2024-08-26", "2024-09-01", "Cross-month 2024")
    ]
    
    for start, end, description in test_cases:
        logger.info(f"\n🚀 Testing: {description} ({start} to {end})")
        
        try:
            csv_path = await exporter.export_custom_dates(start, end, headless=False)
            file_size = csv_path.stat().st_size if csv_path.exists() else 0
            logger.info(f"✅ Success! File: {csv_path.name} ({file_size:,} bytes)")
            
            # Brief pause between tests
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Failed: {str(e)}")
            continue

async def main():
    """Main test function"""
    logger.info("🎯 Testing improved AppsFlyer date input method")
    
    # Run the cross-year test
    await test_cross_year_export()
    
    logger.info("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
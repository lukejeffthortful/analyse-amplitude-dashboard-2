#!/usr/bin/env python3
"""
AppsFlyer Automated CSV Export - Final Production Version
Based on actual dashboard navigation flow
"""

import os
import json
import base64
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Page
import logging
from pathlib import Path
from dotenv import load_dotenv
import time

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
        
    def encode_date_query(self, start_date, end_date):
        """Encode date range into AppsFlyer query parameter format"""
        query_obj = {
            "view_type": "unified",
            "date": [
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            ],
            "isSsot": False,
            "isPerWidget": False
        }
        
        # Convert to JSON and base64 encode
        json_str = json.dumps(query_obj, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        
        return encoded
    
    async def wait_for_download_complete(self, page, timeout=60):
        """Wait for CSV download to complete"""
        downloads_before = set(self.download_dir.glob("*.csv"))
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            downloads_after = set(self.download_dir.glob("*.csv"))
            new_downloads = downloads_after - downloads_before
            
            if new_downloads:
                # Wait a bit more to ensure download is complete
                await asyncio.sleep(2)
                return list(new_downloads)[0]
            
            await asyncio.sleep(1)
        
        return None
        
    async def export_date_range(self, start_date, end_date):
        """Export CSV for a specific date range"""
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=False,  # Set to True for production
                downloads_path=str(self.download_dir)
            )
            
            context = await browser.new_context(
                accept_downloads=True,
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Login
                logger.info("Logging in to AppsFlyer...")
                await page.goto("https://hq1.appsflyer.com/auth/login")
                
                await page.fill('input[type="email"]', self.username)
                await page.fill('input[type="password"]', self.password)
                await page.click('button[type="submit"]')
                
                # Wait for login to complete
                await page.wait_for_function(
                    "url => !url.includes('auth/login')",
                    arg=page.url,
                    timeout=30000
                )
                await page.wait_for_load_state('networkidle')
                logger.info("✓ Successfully logged in")
                
                # Step 2: Navigate to dashboard with date range
                encoded_query = self.encode_date_query(start_date, end_date)
                dashboard_url = f"https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&q={encoded_query}&v=LTU%3D"
                
                logger.info(f"Navigating to dashboard for dates: {start_date} to {end_date}")
                await page.goto(dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Give the dashboard time to load data
                await asyncio.sleep(5)
                
                # Step 3: Export CSV
                logger.info("Initiating CSV export...")
                
                # Look for the export button - try multiple selectors
                export_selectors = [
                    '[data-qa-id="export-widget"]',
                    'li[optionid="exportWidget"]',
                    'text="Export CSV"',
                    '[data-qa-id="typography"]:has-text("Export CSV")'
                ]
                
                export_clicked = False
                for selector in export_selectors:
                    try:
                        # First check if we need to open a menu
                        menu_button = await page.locator('button[aria-label*="more"]').first
                        if await menu_button.is_visible():
                            await menu_button.click()
                            await asyncio.sleep(1)
                        
                        # Try to click export
                        export_element = page.locator(selector).first
                        if await export_element.is_visible():
                            await export_element.click()
                            export_clicked = True
                            logger.info(f"Clicked export with selector: {selector}")
                            break
                    except:
                        continue
                
                if not export_clicked:
                    # Take screenshot for debugging
                    await page.screenshot(path=self.download_dir / "export_error.png")
                    raise Exception("Could not find export button")
                
                # Wait for download
                logger.info("Waiting for CSV download...")
                downloaded_file = await self.wait_for_download_complete(page)
                
                if downloaded_file:
                    # Rename to meaningful name
                    new_name = self.download_dir / f"appsflyer_export_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                    downloaded_file.rename(new_name)
                    logger.info(f"✓ CSV exported successfully: {new_name}")
                    return new_name
                else:
                    raise Exception("Download timeout - no CSV file detected")
                    
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                await page.screenshot(path=self.download_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                raise
                
            finally:
                await browser.close()
    
    async def export_last_week(self):
        """Export data for the previous week (Monday to Sunday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        return await self.export_date_range(last_monday, last_sunday)
    
    async def export_week(self, week_number, year=None):
        """Export data for a specific ISO week"""
        if year is None:
            year = datetime.now().year
            
        # Get the first day of the year
        jan_1 = datetime(year, 1, 1)
        
        # Find the Monday of week 1
        days_to_monday = (7 - jan_1.weekday()) % 7
        if days_to_monday == 0 and jan_1.weekday() != 0:
            days_to_monday = 7
        
        week_1_monday = jan_1 + timedelta(days=days_to_monday)
        
        # Calculate the Monday of the target week
        target_monday = week_1_monday + timedelta(weeks=week_number - 1)
        target_sunday = target_monday + timedelta(days=6)
        
        return await self.export_date_range(target_monday, target_sunday)

async def main():
    """Example usage"""
    exporter = AppsFlyerExporter()
    
    # Export last week's data
    try:
        csv_path = await exporter.export_last_week()
        logger.info(f"\nExport complete! CSV saved to: {csv_path}")
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
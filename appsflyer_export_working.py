#!/usr/bin/env python3
"""
AppsFlyer Automated CSV Export - Working Version
Using the correct widget dropdown button selector
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
                downloads_path=str(self.download_dir),
                slow_mo=200  # Remove for production
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
                
                # Step 2: First navigate to the dashboard, then set date range
                logger.info("Navigating to unified-ltv dashboard...")
                await page.goto("https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779")
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                # Step 3: Now navigate with date range query
                encoded_query = self.encode_date_query(start_date, end_date)
                dashboard_url = f"https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&q={encoded_query}&v=LTU%3D"
                
                logger.info(f"Setting date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                await page.goto(dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Give the dashboard time to load data
                await asyncio.sleep(5)
                
                # Step 4: Export CSV from first widget
                logger.info("Looking for widget dropdown buttons...")
                
                # Find widget dropdown buttons using the specific selector
                widget_dropdowns = await page.locator('[data-qa-id="widget-dropdown-button"]').all()
                logger.info(f"Found {len(widget_dropdowns)} widget dropdown buttons")
                
                if not widget_dropdowns:
                    # Try alternative selectors
                    widget_dropdowns = await page.locator('button[aria-label="3 dots icon"]').all()
                    logger.info(f"Found {len(widget_dropdowns)} widget dropdowns (alt selector)")
                
                export_successful = False
                
                # Try each widget until we find one with export option
                for i, dropdown in enumerate(widget_dropdowns[:5]):  # Try first 5 widgets
                    try:
                        if await dropdown.is_visible():
                            logger.info(f"Clicking dropdown {i+1}...")
                            await dropdown.click()
                            await asyncio.sleep(1)
                            
                            # Look for export option in the menu
                            export_selectors = [
                                'text="Export CSV"',
                                'text="Export"',
                                '[data-qa-id="export-widget"]',
                                'li[optionid="exportWidget"]'
                            ]
                            
                            for selector in export_selectors:
                                export_element = page.locator(selector).first
                                if await export_element.is_visible():
                                    logger.info(f"Found export option: {selector}")
                                    await export_element.click()
                                    export_successful = True
                                    break
                            
                            if export_successful:
                                break
                            else:
                                # Close menu by clicking outside
                                await page.click('body', position={'x': 100, 'y': 100})
                                
                    except Exception as e:
                        logger.debug(f"Error with dropdown {i}: {str(e)}")
                        continue
                
                if not export_successful:
                    raise Exception("Could not find export option in any widget")
                
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

async def test_export():
    """Test the export functionality"""
    exporter = AppsFlyerExporter()
    
    # Test with a specific date range
    start_date = datetime(2025, 8, 18)
    end_date = datetime(2025, 8, 24)
    
    try:
        csv_path = await exporter.export_date_range(start_date, end_date)
        logger.info(f"\n✅ Export successful! CSV saved to: {csv_path}")
        
        # Check file size
        file_size = csv_path.stat().st_size
        logger.info(f"File size: {file_size:,} bytes")
        
    except Exception as e:
        logger.error(f"\n❌ Export failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_export())
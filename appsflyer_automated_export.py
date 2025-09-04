#!/usr/bin/env python3
"""
AppsFlyer Automated CSV Export
Automates the CSV export process from AppsFlyer dashboard using Playwright
"""

import os
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerAutomatedExporter:
    def __init__(self, username, password, download_dir="./appsflyer_exports"):
        self.username = username
        self.password = password
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    async def export_weekly_data(self, start_date, end_date):
        """Export CSV data for a specific date range"""
        async with async_playwright() as p:
            # Launch browser in headless mode for automation
            browser = await p.chromium.launch(
                headless=True,  # Set to False for debugging
                downloads_path=str(self.download_dir)
            )
            
            context = await browser.new_context(
                accept_downloads=True,
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Login to AppsFlyer
                logger.info("Logging in to AppsFlyer...")
                await page.goto("https://hq1.appsflyer.com/auth/login")
                
                # Fill login form
                await page.fill('input[type="email"]', self.username)
                await page.fill('input[type="password"]', self.password)
                await page.click('button[type="submit"]')
                
                # Wait for dashboard to load
                await page.wait_for_url("**/dashboard/**", timeout=30000)
                logger.info("Successfully logged in")
                
                # Navigate to Partners report
                logger.info("Navigating to Partners report...")
                await page.goto("https://hq1.appsflyer.com/partners/overview")
                
                # Set date range
                logger.info(f"Setting date range: {start_date} to {end_date}")
                await page.click('[data-test="date-picker-trigger"]')
                await page.click('[data-test="date-range-custom"]')
                
                # Clear and fill start date
                await page.fill('input[data-test="start-date"]', '')
                await page.fill('input[data-test="start-date"]', start_date.strftime('%Y-%m-%d'))
                
                # Clear and fill end date
                await page.fill('input[data-test="end-date"]', '')
                await page.fill('input[data-test="end-date"]', end_date.strftime('%Y-%m-%d'))
                
                await page.click('button[data-test="apply-date-range"]')
                
                # Wait for data to load
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)  # Additional wait for data
                
                # Export CSV
                logger.info("Initiating CSV export...")
                
                # Start download
                async with page.expect_download() as download_info:
                    await page.click('[data-test="export-button"]')
                    await page.click('[data-test="export-csv"]')
                    
                download = await download_info.value
                
                # Save with meaningful filename
                filename = f"appsflyer_partners_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                save_path = self.download_dir / filename
                await download.save_as(save_path)
                
                logger.info(f"CSV exported successfully to: {save_path}")
                return save_path
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                # Take screenshot for debugging
                await page.screenshot(path=self.download_dir / "error_screenshot.png")
                raise
                
            finally:
                await browser.close()
    
    async def export_last_week(self):
        """Export data for the previous week (Monday to Sunday)"""
        today = datetime.now()
        # Find last Monday
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        return await self.export_weekly_data(last_monday, last_sunday)

async def main():
    """Example usage"""
    # Get credentials from environment
    username = os.getenv('APPSFLYER_USERNAME')
    password = os.getenv('APPSFLYER_PASSWORD')
    
    if not username or not password:
        logger.error("Please set APPSFLYER_USERNAME and APPSFLYER_PASSWORD environment variables")
        return
    
    exporter = AppsFlyerAutomatedExporter(username, password)
    
    # Export last week's data
    csv_path = await exporter.export_last_week()
    logger.info(f"Export complete: {csv_path}")

if __name__ == "__main__":
    asyncio.run(main())
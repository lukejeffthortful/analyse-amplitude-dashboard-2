#!/usr/bin/env python3
"""
AppsFlyer Export Using URL Method
Bypasses date picker fragility by constructing URLs directly
"""

import os
import json
import base64
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerURLExporter:
    def __init__(self, download_dir="./appsflyer_exports"):
        self.username = os.getenv('APPSFLYER_USERNAME')
        self.password = os.getenv('APPSFLYER_PASSWORD')
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.base_url = "https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&v=NTE5ODM3"
        
    def build_date_url(self, start_date, end_date):
        """Build AppsFlyer URL with encoded date range"""
        
        # Create the query object (same structure as the example)
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
        encoded_query = base64.urlsafe_b64encode(json_str.encode()).decode()
        
        # Build full URL
        full_url = f"{self.base_url}&q={encoded_query}&v=LTU%3D"
        
        logger.info(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Encoded query: {encoded_query}")
        logger.info(f"Full URL: {full_url}")
        
        return full_url
    
    async def export_date_range(self, start_date, end_date, headless=False):
        """Export CSV for a specific date range using direct URL navigation"""
        
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
                
                # Step 2: Navigate directly to URL with date range
                logger.info("Navigating directly to dashboard with date range...")
                dashboard_url = self.build_date_url(start_date, end_date)
                
                await page.goto(dashboard_url)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(5)  # Wait for data to load
                logger.info("✓ Dashboard loaded with date range")
                
                # Step 3: Export CSV
                logger.info("Initiating CSV export...")
                
                # Try multiple widget selectors in case the test-id changes
                export_selectors = [
                    page.get_by_test_id("platform-chart:7").get_by_role("button", name="dots icon"),
                    page.get_by_role("button", name="dots icon").first,
                    page.locator('[data-qa-id="widget-dropdown-button"]').first
                ]
                
                export_successful = False
                for i, selector in enumerate(export_selectors):
                    try:
                        if await selector.is_visible():
                            logger.info(f"Clicking export menu {i+1}...")
                            await selector.click()
                            await asyncio.sleep(1)
                            
                            if await page.get_by_text("Export CSV").is_visible():
                                async with page.expect_download() as download_info:
                                    await page.get_by_text("Export CSV").click()
                                    logger.info("✓ Export clicked, waiting for download...")
                                
                                download = await download_info.value
                                filename = f"appsflyer_url_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                                save_path = self.download_dir / filename
                                await download.save_as(save_path)
                                
                                logger.info(f"✅ CSV exported successfully: {save_path}")
                                export_successful = True
                                return save_path
                    except Exception as e:
                        logger.debug(f"Export selector {i} failed: {str(e)}")
                        continue
                
                if not export_successful:
                    raise Exception("Could not find any working export option")
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                await page.screenshot(path=self.download_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                raise
                
            finally:
                await context.close()
                await browser.close()
    
    async def export_yoy_comparison(self, start_date_2025, end_date_2025, start_date_2024, end_date_2024, headless=False):
        """Export data for year-over-year comparison"""
        
        logger.info("🚀 Starting Year-over-Year Export with URL Method")
        
        try:
            # Export 2025 data
            logger.info(f"\n📊 Exporting 2025 data: {start_date_2025} to {end_date_2025}")
            csv_2025 = await self.export_date_range(start_date_2025, end_date_2025, headless)
            
            # Wait between exports
            await asyncio.sleep(3)
            
            # Export 2024 data
            logger.info(f"\n📊 Exporting 2024 data: {start_date_2024} to {end_date_2024}")
            csv_2024 = await self.export_date_range(start_date_2024, end_date_2024, headless)
            
            logger.info(f"\n✅ Both exports completed!")
            logger.info(f"   2025 file: {csv_2025}")
            logger.info(f"   2024 file: {csv_2024}")
            
            return csv_2025, csv_2024
            
        except Exception as e:
            logger.error(f"❌ YoY export failed: {str(e)}")
            raise

async def test_url_method():
    """Test the URL method with year-over-year comparison"""
    exporter = AppsFlyerURLExporter()
    
    # Define date ranges for comparison
    start_2025 = datetime(2025, 8, 25)
    end_2025 = datetime(2025, 8, 31)
    
    start_2024 = datetime(2024, 8, 25)
    end_2024 = datetime(2024, 8, 31)
    
    try:
        # Test the URL method
        csv_2025, csv_2024 = await exporter.export_yoy_comparison(
            start_2025, end_2025, start_2024, end_2024, headless=False
        )
        
        # Quick analysis
        if csv_2025.exists() and csv_2024.exists():
            import pandas as pd
            
            df_2025 = pd.read_csv(csv_2025)
            df_2024 = pd.read_csv(csv_2024)
            
            total_2025 = df_2025['installs appsflyer'].sum() if 'installs appsflyer' in df_2025.columns else 0
            total_2024 = df_2024['installs appsflyer'].sum() if 'installs appsflyer' in df_2024.columns else 0
            
            change = total_2025 - total_2024
            percent = (change / total_2024 * 100) if total_2024 > 0 else 0
            
            logger.info(f"\n📈 Quick Comparison:")
            logger.info(f"   2025 total: {total_2025:,}")
            logger.info(f"   2024 total: {total_2024:,}")
            logger.info(f"   Change: {change:+,} ({percent:+.1f}%)")
            
            # Check if data is different (should be!)
            if total_2025 == total_2024:
                logger.warning("⚠️  Data appears identical - may need to verify date ranges")
            else:
                logger.info("✅ Data shows differences - YoY comparison working!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_url_method())
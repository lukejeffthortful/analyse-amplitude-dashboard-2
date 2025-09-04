#!/usr/bin/env python3
"""
AppsFlyer Optimized Export - Single Browser Session
Reuses browser session for multiple exports
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

class AppsFlyerOptimizedExporter:
    def __init__(self, download_dir="./appsflyer_exports"):
        self.username = os.getenv('APPSFLYER_USERNAME')
        self.password = os.getenv('APPSFLYER_PASSWORD')
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.base_url = "https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&v=NTE5ODM3"
        
        # Browser session state
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False
        
    def build_date_url(self, start_date, end_date):
        """Build AppsFlyer URL with encoded date range"""
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
        encoded_query = base64.urlsafe_b64encode(json_str.encode()).decode()
        full_url = f"{self.base_url}&q={encoded_query}&v=LTU%3D"
        
        return full_url, encoded_query
    
    async def start_session(self, headless=False):
        """Start browser session and login once"""
        if self.browser is not None:
            logger.info("Browser session already active")
            return
            
        logger.info("Starting new browser session...")
        
        playwright = await async_playwright().__aenter__()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            downloads_path=str(self.download_dir)
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = await self.context.new_page()
        
        # Login once
        logger.info("Logging in to AppsFlyer...")
        await self.page.goto("https://hq1.appsflyer.com/auth/login")
        
        await self.page.get_by_role("textbox", name="user-email").fill(self.username)
        await self.page.get_by_role("textbox", name="Password").fill(self.password)
        await self.page.get_by_role("button", name="login").click()
        
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        self.logged_in = True
        logger.info("✅ Browser session started and logged in")
    
    async def export_date_range(self, start_date, end_date):
        """Export CSV for a specific date range (reusing existing session)"""
        if not self.logged_in:
            raise Exception("Must call start_session() first")
        
        try:
            # Navigate directly to URL with date range
            dashboard_url, encoded_query = self.build_date_url(start_date, end_date)
            
            logger.info(f"📅 Exporting: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            logger.info(f"🔗 Navigating to dashboard with date range...")
            
            await self.page.goto(dashboard_url)
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)  # Wait for data to load
            
            # Export CSV
            logger.info("📊 Initiating CSV export...")
            
            # Try multiple selectors for the export menu
            export_selectors = [
                self.page.get_by_test_id("platform-chart:7").get_by_role("button", name="dots icon"),
                self.page.get_by_role("button", name="dots icon").first,
                self.page.locator('[data-qa-id="widget-dropdown-button"]').first
            ]
            
            for i, selector in enumerate(export_selectors):
                try:
                    if await selector.is_visible():
                        await selector.click()
                        await asyncio.sleep(1)
                        
                        if await self.page.get_by_text("Export CSV").is_visible():
                            async with self.page.expect_download() as download_info:
                                await self.page.get_by_text("Export CSV").click()
                            
                            download = await download_info.value
                            filename = f"appsflyer_opt_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                            save_path = self.download_dir / filename
                            await download.save_as(save_path)
                            
                            logger.info(f"✅ Export successful: {save_path.name}")
                            return save_path
                except Exception as e:
                    logger.debug(f"Export method {i} failed: {str(e)}")
                    continue
            
            raise Exception("Could not find working export option")
            
        except Exception as e:
            logger.error(f"❌ Export failed for {start_date} to {end_date}: {str(e)}")
            await self.page.screenshot(path=self.download_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            raise
    
    async def export_multiple_ranges(self, date_ranges):
        """Export multiple date ranges in sequence using the same session"""
        results = []
        
        for i, (start_date, end_date, label) in enumerate(date_ranges):
            try:
                logger.info(f"\n🚀 Export {i+1}/{len(date_ranges)}: {label}")
                csv_path = await self.export_date_range(start_date, end_date)
                results.append({
                    'label': label,
                    'start_date': start_date,
                    'end_date': end_date,
                    'csv_path': csv_path,
                    'success': True
                })
                
                # Brief pause between exports
                if i < len(date_ranges) - 1:  # Don't wait after last export
                    logger.info("⏳ Brief pause before next export...")
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Failed {label}: {str(e)}")
                results.append({
                    'label': label,
                    'start_date': start_date,
                    'end_date': end_date,
                    'csv_path': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def close_session(self):
        """Close the browser session"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
            self.logged_in = False
            logger.info("🔒 Browser session closed")

async def test_optimized_yoy():
    """Test optimized year-over-year comparison with single session"""
    exporter = AppsFlyerOptimizedExporter()
    
    # Define multiple date ranges to test
    date_ranges = [
        (datetime(2025, 8, 25), datetime(2025, 8, 31), "2025 Aug 25-31"),
        (datetime(2024, 8, 25), datetime(2024, 8, 31), "2024 Aug 25-31"),
        (datetime(2024, 8, 18), datetime(2024, 8, 24), "2024 Aug 18-24"),  # Previous week
    ]
    
    try:
        # Start session once
        await exporter.start_session(headless=False)
        
        # Export all ranges using the same session
        logger.info(f"🎯 Starting batch export of {len(date_ranges)} date ranges...")
        results = await exporter.export_multiple_ranges(date_ranges)
        
        # Analyze results
        logger.info(f"\n📊 Export Results Summary:")
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        logger.info(f"   ✅ Successful: {len(successful)}/{len(results)}")
        logger.info(f"   ❌ Failed: {len(failed)}/{len(results)}")
        
        # Quick comparison if we have data
        if len(successful) >= 2:
            try:
                import pandas as pd
                
                csv_2025 = next(r['csv_path'] for r in successful if '2025' in r['label'])
                csv_2024 = next(r['csv_path'] for r in successful if '2024 Aug 25-31' in r['label'])
                
                df_2025 = pd.read_csv(csv_2025)
                df_2024 = pd.read_csv(csv_2024)
                
                total_2025 = df_2025['installs appsflyer'].sum() if 'installs appsflyer' in df_2025.columns else 0
                total_2024 = df_2024['installs appsflyer'].sum() if 'installs appsflyer' in df_2024.columns else 0
                
                change = total_2025 - total_2024
                percent = (change / total_2024 * 100) if total_2024 > 0 else 0
                
                logger.info(f"\n📈 Year-over-Year Comparison:")
                logger.info(f"   2025: {total_2025:,} installs")
                logger.info(f"   2024: {total_2024:,} installs")
                logger.info(f"   Change: {change:+,} ({percent:+.1f}%)")
                
            except Exception as e:
                logger.warning(f"Comparison analysis failed: {str(e)}")
        
        for result in successful:
            file_size = result['csv_path'].stat().st_size if result['csv_path'].exists() else 0
            logger.info(f"   📁 {result['label']}: {result['csv_path'].name} ({file_size:,} bytes)")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        
    finally:
        # Always close session
        await exporter.close_session()
        logger.info("\n✅ Optimized export test complete!")

if __name__ == "__main__":
    asyncio.run(test_optimized_yoy())
#!/usr/bin/env python3
"""
Find the export button on AppsFlyer dashboard
"""

import asyncio
import os
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
from appsflyer_export_final import AppsFlyerExporter

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_export_options():
    """Search for export options systematically"""
    
    exporter = AppsFlyerExporter()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=200
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Login
            logger.info("Logging in...")
            await page.goto("https://hq1.appsflyer.com/auth/login")
            await page.fill('input[type="email"]', exporter.username)
            await page.fill('input[type="password"]', exporter.password)
            await page.click('button[type="submit"]')
            
            await page.wait_for_function(
                "url => !url.includes('auth/login')",
                arg=page.url,
                timeout=30000
            )
            
            # Navigate to dashboard
            encoded = exporter.encode_date_query(
                datetime(2025, 8, 18),
                datetime(2025, 8, 24)
            )
            dashboard_url = f"https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&q={encoded}&v=LTU%3D"
            
            await page.goto(dashboard_url)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)
            
            logger.info("\nSearching for export options...")
            
            # Strategy 1: Look for three-dot menus on widgets
            logger.info("\n1. Looking for widget menu buttons...")
            widget_menus = await page.locator('button[aria-label*="More"], button[data-qa-id*="more"], svg[data-testid*="MoreVert"], button:has(svg[data-testid*="MoreVert"])').all()
            logger.info(f"Found {len(widget_menus)} widget menu buttons")
            
            # Try each menu
            for i, menu in enumerate(widget_menus[:5]):  # Try first 5
                try:
                    if await menu.is_visible():
                        logger.info(f"\nClicking menu button {i+1}...")
                        await menu.click()
                        await asyncio.sleep(1)
                        
                        # Check for export options
                        export_options = [
                            'text="Export CSV"',
                            'text="Export"',
                            'text="Download"',
                            '[data-qa-id="export-widget"]',
                            'li:has-text("Export")'
                        ]
                        
                        for option in export_options:
                            if await page.locator(option).is_visible():
                                logger.info(f"✓ Found export option: {option}")
                                await page.screenshot(path=f"test_downloads/export_found_{i}.png")
                                
                                # Click outside to close menu
                                await page.click('body', position={'x': 100, 'y': 100})
                                break
                        
                except Exception as e:
                    logger.debug(f"Error with menu {i}: {str(e)}")
                    continue
            
            # Strategy 2: Look for global export button
            logger.info("\n2. Looking for global export buttons...")
            global_export_selectors = [
                'button:has-text("Export")',
                'button:has-text("Download")',
                'a:has-text("Export")',
                '[aria-label*="export"]',
                '[title*="export"]'
            ]
            
            for selector in global_export_selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    logger.info(f"Found {count} elements matching: {selector}")
            
            # Take final screenshot
            await page.screenshot(path="test_downloads/export_search_final.png")
            logger.info("\nScreenshots saved to test_downloads/")
            
            # Keep browser open for manual inspection
            logger.info("\nBrowser will stay open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            await page.screenshot(path="test_downloads/export_search_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(find_export_options())
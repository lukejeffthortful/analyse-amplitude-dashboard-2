#!/usr/bin/env python3
"""
Test AppsFlyer Navigation - Verify the dashboard URL approach works
"""

import asyncio
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
from appsflyer_export_final import AppsFlyerExporter

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_navigation():
    """Test navigation to dashboard with encoded dates"""
    
    exporter = AppsFlyerExporter()
    
    # Test date encoding
    start_date = datetime(2025, 8, 18)
    end_date = datetime(2025, 8, 24)
    encoded = exporter.encode_date_query(start_date, end_date)
    
    logger.info(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Encoded query: {encoded}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Watch it happen
            slow_mo=500      # Slow down for visibility
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Login
            logger.info("Step 1: Logging in...")
            await page.goto("https://hq1.appsflyer.com/auth/login")
            
            await page.fill('input[type="email"]', exporter.username)
            await page.fill('input[type="password"]', exporter.password)
            await page.click('button[type="submit"]')
            
            # Wait for redirect
            await page.wait_for_function(
                "url => !url.includes('auth/login')",
                arg=page.url,
                timeout=30000
            )
            
            logger.info("✓ Login successful")
            
            # Navigate to dashboard
            logger.info("\nStep 2: Navigating to dashboard with date range...")
            dashboard_url = f"https://hq1.appsflyer.com/unified-ltv/dashboard#appIds=com.thortful.app,id1041914779&q={encoded}&v=LTU%3D"
            
            await page.goto(dashboard_url)
            await page.wait_for_load_state('networkidle')
            
            # Wait for data to load
            await asyncio.sleep(5)
            
            logger.info("✓ Dashboard loaded")
            
            # Look for export options
            logger.info("\nStep 3: Looking for export options...")
            
            # Check for menu buttons (three dots, etc)
            menu_buttons = await page.locator('button[aria-label*="more"], button[aria-label*="menu"], button[aria-haspopup="menu"]').all()
            logger.info(f"Found {len(menu_buttons)} potential menu buttons")
            
            # Try clicking the first menu button if found
            if menu_buttons:
                logger.info("Clicking menu button...")
                await menu_buttons[0].click()
                await asyncio.sleep(2)
                
                # Look for export option
                export_visible = await page.locator('text="Export CSV"').is_visible()
                if export_visible:
                    logger.info("✓ Found 'Export CSV' option!")
                else:
                    logger.info("✗ 'Export CSV' not visible in menu")
            
            # Take screenshot
            await page.screenshot(path="test_downloads/navigation_test.png")
            logger.info("\nScreenshot saved to test_downloads/navigation_test.png")
            
            logger.info("\nPress Enter to close browser...")
            input()
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            await page.screenshot(path="test_downloads/navigation_error.png")
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_navigation())
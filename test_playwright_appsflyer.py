#!/usr/bin/env python3
"""
Playwright POC Test for AppsFlyer Export
Tests the automation approach with safety checks
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlaywrightAppsFlyerTest:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode
        self.username = os.getenv('APPSFLYER_USERNAME', 'demo@example.com')
        self.password = os.getenv('APPSFLYER_PASSWORD', 'demo_password')
        self.download_dir = Path("./test_downloads")
        self.download_dir.mkdir(exist_ok=True)
        
    async def run_test(self):
        """Run the full test flow"""
        logger.info(f"Starting Playwright test (demo_mode={self.demo_mode})")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=False,  # Set to False so you can watch
                slow_mo=500      # Slow down actions for visibility
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                accept_downloads=True
            )
            
            page = await context.new_page()
            
            try:
                if self.demo_mode:
                    await self._run_demo_test(page)
                else:
                    await self._run_real_test(page)
                    
            except Exception as e:
                logger.error(f"Test failed: {str(e)}")
                # Take screenshot for debugging
                await page.screenshot(path=self.download_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                raise
                
            finally:
                await browser.close()
                
    async def _run_demo_test(self, page):
        """Demo test without actual login"""
        logger.info("Running in DEMO mode - will test navigation without real credentials")
        
        # Test 1: Navigate to AppsFlyer
        logger.info("Test 1: Navigating to AppsFlyer login page...")
        await page.goto("https://hq1.appsflyer.com/auth/login")
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot
        screenshot_path = self.download_dir / "1_login_page.png"
        await page.screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Test 2: Check for login elements
        logger.info("Test 2: Checking for login form elements...")
        
        # Check for email field
        email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            'input[placeholder*="email" i]',
            'input[id*="email" i]'
        ]
        
        email_found = False
        for selector in email_selectors:
            count = await page.locator(selector).count()
            if count > 0:
                logger.info(f"✓ Found email field with selector: {selector}")
                email_found = True
                break
        
        if not email_found:
            logger.warning("✗ Could not find email field")
            
        # Check for password field
        password_found = await page.locator('input[type="password"]').count() > 0
        logger.info(f"{'✓' if password_found else '✗'} Password field found")
        
        # Check for login button
        button_selectors = [
            'button[type="submit"]',
            'button:has-text("Log in")',
            'button:has-text("Sign in")',
            'button:has-text("Login")'
        ]
        
        button_found = False
        for selector in button_selectors:
            count = await page.locator(selector).count()
            if count > 0:
                logger.info(f"✓ Found login button with selector: {selector}")
                button_found = True
                break
                
        # Test 3: Fill form (demo only)
        if email_found and password_found:
            logger.info("Test 3: Testing form fill (demo values)...")
            
            # Fill email
            await page.locator(email_selectors[0]).fill(self.username)
            logger.info("✓ Filled email field")
            
            # Fill password  
            await page.locator('input[type="password"]').fill("*" * len(self.password))
            logger.info("✓ Filled password field")
            
            # Take screenshot of filled form
            await page.screenshot(path=self.download_dir / "2_filled_form.png")
            
        logger.info("\nDemo test complete! Ready for real test with actual credentials.")
        logger.info("To run real test: Set demo_mode=False and ensure credentials are in .env")
        
    async def _run_real_test(self, page):
        """Real test with actual login"""
        logger.info("Running REAL test with actual credentials...")
        
        # Check credentials
        if self.username == 'demo@example.com':
            raise ValueError("Please set real APPSFLYER_USERNAME in .env file")
            
        # Navigate to login
        logger.info("Navigating to AppsFlyer...")
        await page.goto("https://hq1.appsflyer.com/auth/login")
        
        # Login
        logger.info("Logging in...")
        await page.fill('input[type="email"]', self.username)
        await page.fill('input[type="password"]', self.password)
        
        # Click login
        await page.click('button[type="submit"]')
        
        # Wait for navigation - AppsFlyer uses different URL patterns
        logger.info("Waiting for dashboard...")
        try:
            # Wait for URL to change from login page
            await page.wait_for_function(
                "url => !url.includes('auth/login')",
                arg=page.url,
                timeout=30000
            )
            
            # Wait for page to stabilize
            await page.wait_for_load_state('networkidle')
            
            current_url = page.url
            logger.info(f"✓ Successfully logged in! Current URL: {current_url}")
            
        except Exception as e:
            logger.error(f"✗ Login failed - {str(e)}")
            raise
            
        # Navigate to Partners report
        logger.info("Navigating to Partners report...")
        await page.goto("https://hq1.appsflyer.com/partners/overview")
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot
        await page.screenshot(path=self.download_dir / "3_partners_page.png")
        logger.info("✓ Partners page loaded")
        
        # Test date picker and export button presence
        logger.info("Checking for key elements...")
        
        # Look for date picker
        date_picker_selectors = [
            '[data-test="date-picker-trigger"]',
            'button[aria-label*="date"]',
            '.date-picker-trigger',
            'button:has-text("Last")'
        ]
        
        for selector in date_picker_selectors:
            if await page.locator(selector).count() > 0:
                logger.info(f"✓ Found date picker: {selector}")
                break
                
        # Look for export button
        export_selectors = [
            '[data-test="export-button"]',
            'button:has-text("Export")',
            'button[aria-label*="export"]',
            '.export-button'
        ]
        
        for selector in export_selectors:
            if await page.locator(selector).count() > 0:
                logger.info(f"✓ Found export button: {selector}")
                break
                
        logger.info("\nReal test complete! AppsFlyer automation is feasible.")

async def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("AppsFlyer Playwright Automation POC")
    print("="*60 + "\n")
    
    # Check if we should run in demo mode
    demo_mode = input("Run in demo mode? (y/n) [y]: ").lower() != 'n'
    
    if not demo_mode:
        print("\nReal mode requires valid AppsFlyer credentials in .env file:")
        print("APPSFLYER_USERNAME=your_email@company.com")
        print("APPSFLYER_PASSWORD=your_password")
        
        confirm = input("\nHave you set up credentials? (y/n): ")
        if confirm.lower() != 'y':
            print("Please set up credentials first.")
            return
            
    # Run test
    tester = PlaywrightAppsFlyerTest(demo_mode=demo_mode)
    
    try:
        await tester.run_test()
        print("\n✅ Test completed successfully!")
        print(f"Screenshots saved in: {tester.download_dir}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check the screenshots in test_downloads/ for debugging")

if __name__ == "__main__":
    asyncio.run(main())
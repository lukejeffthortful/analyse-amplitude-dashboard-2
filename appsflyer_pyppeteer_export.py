#!/usr/bin/env python3
"""
AppsFlyer Pyppeteer-based CSV Export
Using Pyppeteer (Python port of Puppeteer) for automation
"""

import os
import asyncio
from datetime import datetime, timedelta
from pyppeteer import launch
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerPyppeteerExporter:
    def __init__(self, username, password, download_dir="./appsflyer_exports"):
        self.username = username
        self.password = password
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    async def export_weekly_data(self, start_date, end_date):
        """Export CSV data for a specific date range"""
        # Configure browser with stealth settings
        browser = await launch({
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            ],
            'dumpio': True
        })
        
        page = await browser.newPage()
        
        # Set viewport and user agent to appear more natural
        await page.setViewport({'width': 1920, 'height': 1080})
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Remove webdriver property
        await page.evaluateOnNewDocument('''() => {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        }''')
        
        try:
            # Add delays to mimic human behavior
            logger.info("Accessing AppsFlyer...")
            await page.goto("https://hq1.appsflyer.com/auth/login", {'waitUntil': 'networkidle2'})
            await asyncio.sleep(2)  # Human-like delay
            
            # Login with typing delays
            logger.info("Logging in...")
            await page.type('input[type="email"]', self.username, {'delay': 100})
            await asyncio.sleep(0.5)
            await page.type('input[type="password"]', self.password, {'delay': 100})
            await asyncio.sleep(1)
            
            await page.click('button[type="submit"]')
            await page.waitForNavigation({'waitUntil': 'networkidle2'})
            
            # Rest of implementation similar to Playwright version
            # ... (date selection, export, etc.)
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            await page.screenshot({'path': str(self.download_dir / 'error.png')})
            raise
        finally:
            await browser.close()

# Note: Pyppeteer has some limitations compared to Playwright:
# 1. Less actively maintained (last update 2021)
# 2. Based on older Puppeteer version
# 3. Some compatibility issues with newer Chrome versions
# 4. Less robust download handling
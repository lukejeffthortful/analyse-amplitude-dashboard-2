#!/usr/bin/env python3
"""
Debug AppsFlyer navigation issues
"""

import asyncio
import re
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_navigation():
    """Debug step by step to find where it fails"""
    
    username = os.getenv('APPSFLYER_USERNAME')
    password = os.getenv('APPSFLYER_PASSWORD')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000  # Very slow for debugging
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Step 1: Login
            logger.info("Step 1: Navigating to login page...")
            await page.goto("https://hq1.appsflyer.com/auth/login")
            await page.wait_for_load_state('networkidle')
            
            # Take screenshot
            await page.screenshot(path="debug_1_login_page.png")
            logger.info("Screenshot: debug_1_login_page.png")
            
            # Fill login form
            logger.info("Step 2: Filling login form...")
            await page.get_by_role("textbox", name="user-email").fill(username)
            await page.get_by_role("textbox", name="Password").fill(password)
            
            await page.screenshot(path="debug_2_filled_form.png")
            logger.info("Screenshot: debug_2_filled_form.png")
            
            # Click login
            logger.info("Step 3: Clicking login...")
            await page.get_by_role("button", name="login").click()
            
            # Wait for page to load after login
            await asyncio.sleep(5)
            await page.wait_for_load_state('networkidle')
            
            current_url = page.url
            logger.info(f"Current URL after login: {current_url}")
            
            await page.screenshot(path="debug_3_after_login.png")
            logger.info("Screenshot: debug_3_after_login.png")
            
            # Step 4: Look for Marketing Overview link
            logger.info("Step 4: Looking for Marketing Overview link...")
            
            # Try multiple ways to find it
            marketing_selectors = [
                page.get_by_role("link", name="Marketing Overview"),
                page.locator('a:has-text("Marketing Overview")'),
                page.locator('[href*="marketing"]'),
                page.locator('a:has-text("Marketing")')
            ]
            
            marketing_link = None
            for i, selector in enumerate(marketing_selectors):
                try:
                    count = await selector.count()
                    if count > 0:
                        logger.info(f"Found Marketing Overview with selector {i}: {count} elements")
                        marketing_link = selector.first
                        break
                except Exception as e:
                    logger.debug(f"Selector {i} failed: {str(e)}")
            
            if not marketing_link:
                # Look for any navigation links
                logger.info("Marketing Overview not found. Looking for all navigation links...")
                all_links = await page.locator('a').all()
                
                link_texts = []
                for link in all_links[:20]:  # Check first 20 links
                    try:
                        text = await link.text_content()
                        href = await link.get_attribute('href')
                        if text and text.strip():
                            link_texts.append(f"'{text.strip()}' -> {href}")
                    except:
                        continue
                
                logger.info("Available links:")
                for text in link_texts:
                    logger.info(f"  {text}")
                
                await page.screenshot(path="debug_4_no_marketing_link.png")
                raise Exception("Could not find Marketing Overview link")
            
            # Click Marketing Overview
            logger.info("Step 5: Clicking Marketing Overview...")
            await marketing_link.click()
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            current_url = page.url
            logger.info(f"URL after clicking Marketing Overview: {current_url}")
            
            await page.screenshot(path="debug_5_marketing_page.png")
            logger.info("Screenshot: debug_5_marketing_page.png")
            
            # Step 6: Look for date picker
            logger.info("Step 6: Looking for date picker...")
            
            date_selectors = [
                page.get_by_role("button", name=re.compile(r"Last \d+ days")),
                page.locator('button:has-text("Last")'),
                page.locator('button:has-text("202")'),  # Year in button
                page.locator('[aria-label*="date"]')
            ]
            
            for i, selector in enumerate(date_selectors):
                try:
                    count = await selector.count()
                    if count > 0:
                        logger.info(f"Found date picker with selector {i}: {count} elements")
                except:
                    continue
            
            logger.info("\nDebug complete! Check screenshots to see where the issue is.")
            logger.info("Screenshots saved:")
            logger.info("  debug_1_login_page.png")
            logger.info("  debug_2_filled_form.png") 
            logger.info("  debug_3_after_login.png")
            logger.info("  debug_5_marketing_page.png (if reached)")
            
            # Keep browser open for manual inspection
            logger.info("\nBrowser will stay open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Debug failed at: {str(e)}")
            await page.screenshot(path="debug_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_navigation())
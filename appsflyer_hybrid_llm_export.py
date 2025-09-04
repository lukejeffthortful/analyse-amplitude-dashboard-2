#!/usr/bin/env python3
"""
Hybrid LLM-Assisted AppsFlyer Export
Uses traditional automation with LLM fallback for resilience
"""

import os
import base64
from typing import Optional
from playwright.async_api import Page, Locator
import openai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LLMBrowserHelper:
    """LLM-assisted browser automation with fallback logic"""
    
    def __init__(self, api_key: str):
        self.client = openai.Client(api_key=api_key)
        self.use_llm_fallback = True
        
    async def find_element(self, page: Page, description: str, selectors: list[str]) -> Optional[Locator]:
        """Try traditional selectors first, fall back to LLM if needed"""
        
        # Step 1: Try traditional selectors (fast & reliable)
        for selector in selectors:
            try:
                element = page.locator(selector)
                if await element.count() > 0:
                    logger.info(f"Found element with selector: {selector}")
                    return element
            except:
                continue
        
        # Step 2: Only use LLM if traditional approach fails
        if self.use_llm_fallback:
            logger.warning(f"Traditional selectors failed, using LLM for: {description}")
            return await self._llm_find_element(page, description)
        
        return None
    
    async def _llm_find_element(self, page: Page, description: str) -> Optional[Locator]:
        """Use LLM to find element by description"""
        
        # Take screenshot
        screenshot = await page.screenshot()
        base64_image = base64.b64encode(screenshot).decode('utf-8')
        
        # Ask LLM to find element
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Find the {description} in this screenshot. Return ONLY the CSS selector or text to click on. If not found, return 'NOT_FOUND'."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }],
            max_tokens=100
        )
        
        selector = response.choices[0].message.content.strip()
        
        if selector != "NOT_FOUND":
            try:
                # Try to use LLM's suggestion
                element = page.locator(selector)
                if await element.count() > 0:
                    return element
                    
                # If CSS selector fails, try text-based search
                element = page.get_by_text(selector)
                if await element.count() > 0:
                    return element
            except:
                logger.error(f"LLM suggestion failed: {selector}")
        
        return None

class ResilientAppsFlyerExporter:
    """Main exporter with hybrid approach"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.llm_helper = LLMBrowserHelper(os.getenv('OPENAI_API_KEY'))
        
    async def login(self, page: Page):
        """Login with resilient element finding"""
        
        # Define multiple selectors for each element
        email_input = await self.llm_helper.find_element(
            page,
            "email input field",
            [
                'input[type="email"]',
                'input[name="email"]',
                '#email',
                'input[placeholder*="email"]'
            ]
        )
        
        if email_input:
            await email_input.fill(self.username)
        else:
            raise Exception("Could not find email input")
        
        # Similar approach for password and login button
        password_input = await self.llm_helper.find_element(
            page,
            "password input field", 
            [
                'input[type="password"]',
                'input[name="password"]',
                '#password'
            ]
        )
        
        if password_input:
            await password_input.fill(self.password)
            
        login_button = await self.llm_helper.find_element(
            page,
            "login or sign in button",
            [
                'button[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'input[type="submit"]'
            ]
        )
        
        if login_button:
            await login_button.click()
            
    async def export_with_monitoring(self, page: Page):
        """Export with anomaly detection"""
        
        # Take screenshot before action
        before_screenshot = await page.screenshot()
        
        # Perform export
        export_button = await self.llm_helper.find_element(
            page,
            "export or download button",
            [
                '[data-test="export-button"]',
                'button:has-text("Export")',
                'button[aria-label*="export"]',
                '.export-button'
            ]
        )
        
        if export_button:
            await export_button.click()
            
            # Check if anything unexpected happened
            await self._check_for_anomalies(page)
            
    async def _check_for_anomalies(self, page: Page):
        """Use LLM to check for unexpected popups or errors"""
        
        # Only check if we see signs of potential issues
        error_indicators = [
            'text=/error/i',
            'text=/failed/i', 
            'text=/denied/i',
            '.modal',
            '.popup',
            '[role="alert"]'
        ]
        
        for indicator in error_indicators:
            if await page.locator(indicator).count() > 0:
                # Use LLM to understand the issue
                logger.warning("Detected potential issue, analyzing with LLM")
                await self._analyze_error(page)
                break
                
    async def _analyze_error(self, page: Page):
        """Have LLM analyze and suggest resolution"""
        screenshot = await page.screenshot()
        # Send to LLM for analysis...

# Usage example
async def main():
    # Check if we should use LLM fallback
    use_llm = os.getenv('USE_LLM_FALLBACK', 'false').lower() == 'true'
    
    if use_llm and not os.getenv('OPENAI_API_KEY'):
        logger.warning("LLM fallback requested but no API key provided")
        use_llm = False
    
    exporter = ResilientAppsFlyerExporter(
        os.getenv('APPSFLYER_USERNAME'),
        os.getenv('APPSFLYER_PASSWORD')
    )
    
    # Disable LLM if not needed (saves money)
    exporter.llm_helper.use_llm_fallback = use_llm
    
    # Run export...
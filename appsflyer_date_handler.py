#!/usr/bin/env python3
"""
AppsFlyer Date Selection Handler
Handles complex date picking scenarios
"""

from datetime import datetime, timedelta
import calendar
import asyncio
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)

class DatePickerHandler:
    """Handles date selection in AppsFlyer's calendar widget"""
    
    @staticmethod
    async def select_date_range(page: Page, start_date: datetime, end_date: datetime):
        """
        Select a date range in AppsFlyer's date picker
        Handles cross-month selections
        """
        
        # Click the current date range button to open picker
        logger.info("Opening date picker...")
        
        # Find and click the date button (it shows current range)
        date_buttons = await page.locator('button:has-text("202"):has-text("-")').all()
        if not date_buttons:
            # Fallback patterns
            date_buttons = await page.locator('button[class*="date"]:has-text("Last")').all()
        
        if date_buttons:
            await date_buttons[0].click()
        else:
            raise Exception("Could not find date picker button")
        
        # Wait for calendar to open
        await asyncio.sleep(1)
        
        # Helper function to click a date
        async def click_date(date: datetime):
            day = str(date.day)
            month_year = date.strftime("%B %Y")  # e.g., "August 2025"
            
            # Check if we need to navigate months
            current_month_labels = await page.locator('.month-label, [class*="month"]:has-text("2025")').all_text_contents()
            
            if current_month_labels and month_year not in ' '.join(current_month_labels):
                # Need to navigate to correct month
                logger.info(f"Navigating to {month_year}")
                
                # Click next/previous month buttons as needed
                # This is simplified - you might need more complex navigation
                if date > datetime.now():
                    # Click next button
                    next_btn = await page.locator('button[aria-label*="Next"], button:has-text("›")').first
                    if await next_btn.is_visible():
                        await next_btn.click()
                        await asyncio.sleep(0.5)
            
            # Now click the date
            # Get all cells with this day number
            day_cells = await page.get_by_role("gridcell", name=day).all()
            
            # Try to find the right one (usually first is current month)
            clicked = False
            for i, cell in enumerate(day_cells):
                try:
                    # Check if cell is enabled (not grayed out)
                    is_disabled = await cell.get_attribute('aria-disabled')
                    if is_disabled != 'true':
                        await cell.click()
                        clicked = True
                        logger.info(f"Clicked date: {day}")
                        break
                except:
                    continue
            
            if not clicked:
                logger.warning(f"Could not click date: {day}")
            
            return clicked
        
        # Click start date
        logger.info(f"Selecting start date: {start_date.strftime('%Y-%m-%d')}")
        await click_date(start_date)
        await asyncio.sleep(0.5)
        
        # Click end date
        logger.info(f"Selecting end date: {end_date.strftime('%Y-%m-%d')}")
        await click_date(end_date)
        await asyncio.sleep(0.5)
        
        # Click Apply button
        apply_buttons = await page.get_by_role("button", name="Apply").all()
        if not apply_buttons:
            apply_buttons = await page.locator('button:has-text("Apply")').all()
        
        if apply_buttons:
            await apply_buttons[0].click()
            logger.info("Date range applied")
        else:
            logger.warning("Could not find Apply button")
        
        # Wait for page to update
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
    
    @staticmethod
    def get_week_dates(week_number: int, year: int = None):
        """Get Monday and Sunday dates for a given ISO week number"""
        if year is None:
            year = datetime.now().year
        
        # Find first Thursday of the year (ISO week 1 contains first Thursday)
        jan1 = datetime(year, 1, 1)
        first_thursday = jan1 + timedelta(days=(3 - jan1.weekday() + 7) % 7)
        
        # Calculate start of week 1
        week1_monday = first_thursday - timedelta(days=3)
        
        # Calculate target week
        target_monday = week1_monday + timedelta(weeks=week_number - 1)
        target_sunday = target_monday + timedelta(days=6)
        
        return target_monday, target_sunday
    
    @staticmethod
    def get_last_complete_week():
        """Get the last complete week (Monday to Sunday)"""
        today = datetime.now()
        # Go to last Sunday
        days_since_sunday = (today.weekday() + 1) % 7
        last_sunday = today - timedelta(days=days_since_sunday)
        last_monday = last_sunday - timedelta(days=6)
        
        # If today is Sunday, go to previous week
        if today.weekday() == 6:
            last_sunday = last_sunday - timedelta(days=7)
            last_monday = last_monday - timedelta(days=7)
        
        return last_monday, last_sunday
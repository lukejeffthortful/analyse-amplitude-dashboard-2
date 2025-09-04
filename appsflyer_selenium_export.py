#!/usr/bin/env python3
"""
AppsFlyer Selenium-based CSV Export (Alternative)
Uses Selenium WebDriver for broader compatibility
"""

import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppsFlyerSeleniumExporter:
    def __init__(self, username, password, download_dir="./appsflyer_exports"):
        self.username = username
        self.password = password
        self.download_dir = Path(download_dir).absolute()
        self.download_dir.mkdir(exist_ok=True)
        
    def setup_driver(self, headless=True):
        """Setup Chrome driver with download preferences"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set download directory
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        return driver
    
    def wait_for_download(self, timeout=60):
        """Wait for download to complete"""
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < timeout:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(self.download_dir):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds < timeout
    
    def export_weekly_data(self, start_date, end_date):
        """Export CSV data for a specific date range"""
        driver = self.setup_driver(headless=False)  # Set to True for production
        wait = WebDriverWait(driver, 20)
        
        try:
            # Login
            logger.info("Logging in to AppsFlyer...")
            driver.get("https://hq1.appsflyer.com/auth/login")
            
            # Wait for and fill email
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            email_field.send_keys(self.username)
            
            # Fill password
            password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.send_keys(self.password)
            
            # Click login
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            # Wait for dashboard
            wait.until(EC.url_contains("dashboard"))
            logger.info("Successfully logged in")
            
            # Navigate to Partners report
            logger.info("Navigating to Partners report...")
            driver.get("https://hq1.appsflyer.com/partners/overview")
            
            # Wait for page to load
            time.sleep(5)
            
            # Open date picker
            logger.info(f"Setting date range: {start_date} to {end_date}")
            date_picker = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="date-picker-trigger"]')))
            date_picker.click()
            
            # Select custom range
            custom_range = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="date-range-custom"]')))
            custom_range.click()
            
            # Set dates
            start_input = driver.find_element(By.CSS_SELECTOR, 'input[data-test="start-date"]')
            start_input.clear()
            start_input.send_keys(start_date.strftime('%Y-%m-%d'))
            
            end_input = driver.find_element(By.CSS_SELECTOR, 'input[data-test="end-date"]')
            end_input.clear()
            end_input.send_keys(end_date.strftime('%Y-%m-%d'))
            
            # Apply date range
            apply_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test="apply-date-range"]')
            apply_button.click()
            
            # Wait for data to load
            time.sleep(5)
            
            # Export CSV
            logger.info("Initiating CSV export...")
            export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="export-button"]')))
            export_button.click()
            
            csv_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="export-csv"]')))
            csv_option.click()
            
            # Wait for download
            logger.info("Waiting for download to complete...")
            if self.wait_for_download():
                logger.info("CSV exported successfully")
                
                # Find the downloaded file
                files = sorted(self.download_dir.glob("*.csv"), key=os.path.getmtime, reverse=True)
                if files:
                    latest_file = files[0]
                    # Rename to meaningful name
                    new_name = self.download_dir / f"appsflyer_partners_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                    latest_file.rename(new_name)
                    logger.info(f"Saved as: {new_name}")
                    return new_name
            else:
                logger.error("Download timeout")
                return None
                
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            driver.save_screenshot(str(self.download_dir / "error_screenshot.png"))
            raise
            
        finally:
            driver.quit()
    
    def export_last_week(self):
        """Export data for the previous week (Monday to Sunday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        return self.export_weekly_data(last_monday, last_sunday)

def main():
    """Example usage"""
    username = os.getenv('APPSFLYER_USERNAME')
    password = os.getenv('APPSFLYER_PASSWORD')
    
    if not username or not password:
        logger.error("Please set APPSFLYER_USERNAME and APPSFLYER_PASSWORD environment variables")
        return
    
    exporter = AppsFlyerSeleniumExporter(username, password)
    csv_path = exporter.export_last_week()
    
    if csv_path:
        logger.info(f"Export complete: {csv_path}")

if __name__ == "__main__":
    main()
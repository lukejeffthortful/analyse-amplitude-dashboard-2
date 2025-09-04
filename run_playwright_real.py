#!/usr/bin/env python3
"""
Run Playwright Test with Real Credentials
"""

import asyncio
import sys
import os
from test_playwright_appsflyer import PlaywrightAppsFlyerTest
from dotenv import load_dotenv

# Load environment variables
load_dotenv(verbose=True)

async def main():
    """Run real test automatically"""
    print("\n" + "="*60)
    print("AppsFlyer Playwright Automation - Real Test")
    print("="*60 + "\n")
    
    # Check credentials
    username = os.getenv('APPSFLYER_USERNAME')
    password = os.getenv('APPSFLYER_PASSWORD')
    
    if not username or not password:
        print("❌ Error: AppsFlyer credentials not found in .env file")
        print("Please ensure you have set:")
        print("  APPSFLYER_USERNAME=your_email@company.com")
        print("  APPSFLYER_PASSWORD=your_password")
        sys.exit(1)
    
    print(f"✓ Found credentials for: {username}")
    print("Starting real test...\n")
    
    # Run test in real mode
    tester = PlaywrightAppsFlyerTest(demo_mode=False)
    
    try:
        await tester.run_test()
        print("\n✅ Real test completed successfully!")
        print(f"Screenshots saved in: {tester.download_dir}")
        print("\nNext steps:")
        print("1. Check screenshots to verify successful navigation")
        print("2. Implement full export functionality")
        print("3. Test CSV download")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check the screenshots in test_downloads/ for debugging")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
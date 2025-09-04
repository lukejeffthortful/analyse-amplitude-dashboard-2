#!/usr/bin/env python3
"""
Run Playwright POC Test in Demo Mode
"""

import asyncio
import sys
from test_playwright_appsflyer import PlaywrightAppsFlyerTest

async def main():
    """Run demo test automatically"""
    print("\n" + "="*60)
    print("AppsFlyer Playwright Automation POC - Demo Mode")
    print("="*60 + "\n")
    
    # Run test in demo mode
    tester = PlaywrightAppsFlyerTest(demo_mode=True)
    
    try:
        await tester.run_test()
        print("\n✅ Demo test completed successfully!")
        print(f"Screenshots saved in: {tester.download_dir}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Check the screenshots in test_downloads/ for debugging")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
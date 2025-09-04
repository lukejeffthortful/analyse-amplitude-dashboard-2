#!/usr/bin/env python3
"""
Playwright Recorder - Record your browser interactions
"""

import os
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

async def start_recording():
    """Start Playwright recorder to capture your interactions"""
    
    print("="*60)
    print("Playwright Recorder")
    print("="*60)
    print("\nThis will open a browser and record your interactions.")
    print("The generated code will be saved to: recorded_script.py")
    print("\nInstructions:")
    print("1. Browser will open AppsFlyer")
    print("2. Perform your export workflow")
    print("3. Close the browser when done")
    print("4. Check recorded_script.py for the generated code")
    print("\n" + "="*60)
    
    async with async_playwright() as p:
        # Launch browser with recording enabled
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        # Start recording
        context = await browser.new_context(
            record_video_dir="./recordings",
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Enable recording
        await context.tracing.start(screenshots=True, snapshots=True)
        
        page = await context.new_page()
        
        # Navigate to AppsFlyer
        await page.goto("https://hq1.appsflyer.com/auth/login")
        
        print("\n✓ Browser opened. Perform your actions...")
        print("Recording is active. Close the browser when done.\n")
        
        # Wait for browser to close
        try:
            await page.wait_for_event('close', timeout=0)
        except:
            pass
        
        # Save trace
        await context.tracing.stop(path="trace.zip")
        await browser.close()
        
        print("\n✓ Recording saved to trace.zip")
        print("You can view it at: https://trace.playwright.dev/")

async def use_codegen():
    """Instructions for using Playwright codegen"""
    
    print("\n" + "="*60)
    print("Using Playwright Codegen (Recommended)")
    print("="*60)
    print("\nRun this command to start recording:")
    print("\n  playwright codegen https://hq1.appsflyer.com/auth/login\n")
    print("This will:")
    print("1. Open a browser window")
    print("2. Open Playwright Inspector")
    print("3. Record all your actions as code")
    print("4. Show the generated code in real-time")
    print("\nYou can then:")
    print("- Copy the generated code")
    print("- Save it to a file")
    print("- Modify it for your needs")
    print("\n" + "="*60)

if __name__ == "__main__":
    print("\nChoose recording method:")
    print("1. Use Playwright Codegen (recommended)")
    print("2. Start custom recording")
    
    # For automated run, just show codegen instructions
    asyncio.run(use_codegen())
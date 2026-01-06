#!/usr/bin/env python3
"""
E2E Test via CDP - Connects to existing Chrome/Edge browser
Prerequisites: Start browser with --remote-debugging-port=9222
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "d:/VMs/Projetos/Sharepoint_JIRA/test_screenshots"
CDP_URL = "http://127.0.0.1:9222"

async def connect_and_test():
    """Connect to existing browser and run E2 test"""
    print("=" * 60)
    print("E2E TEST VIA CDP - Connecting to existing browser")
    print("=" * 60)
    
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async with async_playwright() as p:
        try:
            # Connect to existing browser via CDP
            print(f"Connecting to browser at {CDP_URL}...")
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print("Connected successfully!")
            
            # Get all contexts and pages
            contexts = browser.contexts
            print(f"Found {len(contexts)} browser contexts")
            
            for i, ctx in enumerate(contexts):
                pages = ctx.pages
                print(f"  Context {i}: {len(pages)} pages")
                for j, page in enumerate(pages):
                    print(f"    Page {j}: {page.url[:80]}...")
            
            # Find Teams page
            teams_page = None
            for ctx in contexts:
                for page in ctx.pages:
                    if "teams.microsoft.com" in page.url:
                        teams_page = page
                        break
                if teams_page:
                    break
            
            if teams_page:
                print(f"\nFound Teams page: {teams_page.url}")
                
                # Take screenshot
                ss_path = f"{SCREENSHOT_DIR}/e2_cdp_{timestamp}.png"
                await teams_page.screenshot(path=ss_path)
                print(f"Screenshot saved: {ss_path}")
                
                # Now we can interact with the page
                print("\nReady to execute E2 test on connected Teams page")
                
            else:
                print("\nNo Teams page found. Please open Teams in browser first.")
                print("Then run this script again.")
            
        except Exception as e:
            print(f"\nError: {e}")
            print("\n*** SETUP REQUIRED ***")
            print("1. Close all Chrome/Edge windows")
            print("2. Run this command to start browser with debugging:")
            print('   "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --remote-debugging-port=9222')
            print("3. Login to Teams in that browser")
            print("4. Run this script again")

if __name__ == "__main__":
    asyncio.run(connect_and_test())

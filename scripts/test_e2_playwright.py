#!/usr/bin/env python3
"""
E2E Test: E2 - Reunião unchecked → submit allowed
Uses Playwright to connect to Teams and execute the test
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "d:/VMs/Projetos/Sharepoint_JIRA/test_screenshots"
TEAMS_URL = "https://teams.microsoft.com"

async def run_test_e2():
    """E2: Meeting checkbox unchecked → submit should succeed without date"""
    print("=" * 60)
    print("TEST E2: Reuniao com cliente UNCHECKED -> submit allowed")
    print("=" * 60)
    
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async with async_playwright() as p:
        # Launch browser with visible UI (headless=False)
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=300  # Slow down for visibility
        )
        
        # Create context with persistent storage
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        page = await context.new_page()
        
        print(f"[{datetime.now().isoformat()}] Navigating to Teams...")
        await page.goto(TEAMS_URL)
        
        # Wait for page load
        await page.wait_for_load_state("networkidle", timeout=60000)
        
        # Take initial screenshot
        await page.screenshot(path=f"{SCREENSHOT_DIR}/e2_initial_{timestamp}.png")
        print(f"[{datetime.now().isoformat()}] Initial screenshot saved")
        
        # Wait for login - user needs to login manually if not authenticated
        print("\n*** WAITING FOR USER TO LOGIN TO TEAMS ***")
        print("*** Once logged in, the test will continue automatically ***\n")
        
        # Wait for Teams chat to load (look for Workflows or a chat element)
        try:
            await page.wait_for_selector('[data-tid="chat-list"]', timeout=120000)
            print("[OK] Teams chat list detected")
        except:
            print("[WARN] Could not detect chat list, continuing anyway...")
        
        # Take screenshot after login
        await page.screenshot(path=f"{SCREENSHOT_DIR}/e2_logged_in_{timestamp}.png")
        print(f"[{datetime.now().isoformat()}] Logged in screenshot saved")
        
        # Search for Workflows chat
        print("\nSearching for Workflows chat...")
        search_box = await page.query_selector('[data-tid="search-input"]')
        if search_box:
            await search_box.fill("Workflows")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000)
        
        await page.screenshot(path=f"{SCREENSHOT_DIR}/e2_search_{timestamp}.png")
        
        print("\n*** MANUAL STEP REQUIRED ***")
        print("1. Navigate to a VIVO card")
        print("2. Set Status: Verde")
        print("3. Set Status Atual: Em Análise")
        print("4. Set Tipo: Oferta")
        print("5. UNCHECK 'Houve reunião com cliente'")
        print("6. Leave date EMPTY")
        print("7. Click 'Enviar Status Report'")
        print("8. EXPECTED: Submission succeeds")
        print("\nPress Enter when done...")
        
        # Keep browser open for manual testing
        await page.wait_for_timeout(300000)  # 5 minutes
        
        # Final screenshot
        await page.screenshot(path=f"{SCREENSHOT_DIR}/e2_final_{timestamp}.png")
        print(f"\n[{datetime.now().isoformat()}] Final screenshot saved")
        
        await browser.close()
        print("\nTest E2 complete!")

if __name__ == "__main__":
    asyncio.run(run_test_e2())

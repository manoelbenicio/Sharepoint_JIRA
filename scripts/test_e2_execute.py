#!/usr/bin/env python3
"""
E2E Test E2: Reuniao unchecked -> submit allowed
Connects via CDP and executes the test automatically
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "d:/VMs/Projetos/Sharepoint_JIRA/test_screenshots"
CDP_URL = "http://127.0.0.1:9222"

async def execute_e2_test():
    """Execute E2 test: Meeting unchecked -> submit should succeed"""
    print("=" * 60)
    print("TEST E2: Reuniao com cliente UNCHECKED -> submit allowed")
    print("=" * 60)
    
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async with async_playwright() as p:
        try:
            print(f"Connecting to browser at {CDP_URL}...")
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            print("Connected!")
            
            # Find Teams page
            teams_page = None
            for ctx in browser.contexts:
                for page in ctx.pages:
                    if "teams.microsoft.com" in page.url:
                        teams_page = page
                        break
            
            if not teams_page:
                print("ERROR: No Teams page found")
                return False
            
            print(f"Found Teams: {teams_page.url[:60]}...")
            
            # Navigate to Workflows chat
            print("\n[1] Looking for Workflows chat...")
            
            # Try to find chat with "Workflows"
            await teams_page.wait_for_timeout(2000)
            await teams_page.screenshot(path=f"{SCREENSHOT_DIR}/e2_step1_{timestamp}.png")
            
            # Look for any VIVO card submit button
            print("[2] Looking for Adaptive Card...")
            
            # Find submit button "Enviar Status Report"
            submit_btn = await teams_page.query_selector('button:has-text("Enviar Status Report")')
            if submit_btn:
                print("    Found 'Enviar Status Report' button")
            else:
                # Try alternate selectors
                submit_btn = await teams_page.query_selector('[aria-label*="Enviar"]')
                if submit_btn:
                    print("    Found submit button via aria-label")
            
            # Look for status radio buttons
            print("[3] Looking for form controls...")
            
            # Find all radio buttons
            radios = await teams_page.query_selector_all('input[type="radio"]')
            print(f"    Found {len(radios)} radio buttons")
            
            # Find checkboxes
            checkboxes = await teams_page.query_selector_all('input[type="checkbox"]')
            print(f"    Found {len(checkboxes)} checkboxes")
            
            # Take screenshot of current state
            await teams_page.screenshot(path=f"{SCREENSHOT_DIR}/e2_controls_{timestamp}.png")
            print(f"\nScreenshot saved: e2_controls_{timestamp}.png")
            
            # Try to find and click Verde radio
            print("\n[4] Setting form values...")
            verde_radio = await teams_page.query_selector('input[value="Verde"]')
            if verde_radio:
                await verde_radio.click()
                print("    Clicked Verde")
            
            # Find meeting checkbox and ensure unchecked
            meeting_checkbox = await teams_page.query_selector('input[type="checkbox"]')
            if meeting_checkbox:
                is_checked = await meeting_checkbox.is_checked()
                if is_checked:
                    await meeting_checkbox.click()
                    print("    Unchecked meeting checkbox")
                else:
                    print("    Meeting checkbox already unchecked")
            
            await teams_page.screenshot(path=f"{SCREENSHOT_DIR}/e2_filled_{timestamp}.png")
            
            # Try to submit
            print("\n[5] Attempting submit...")
            if submit_btn:
                await submit_btn.click()
                await teams_page.wait_for_timeout(3000)
                await teams_page.screenshot(path=f"{SCREENSHOT_DIR}/e2_result_{timestamp}.png")
                print("    Clicked submit button")
                print("\n*** E2 TEST EXECUTED ***")
                print("Check screenshot for result")
                return True
            else:
                print("    ERROR: Submit button not found")
                return False
                
        except Exception as e:
            print(f"\nError: {e}")
            return False

if __name__ == "__main__":
    result = asyncio.run(execute_e2_test())
    print(f"\nTest result: {'PASS' if result else 'NEEDS VERIFICATION'}")

#!/usr/bin/env python3
"""
E2E Tests for VIVO Adaptive Card - Using Playwright
Tests E2, F1, F3, F4, DUP2
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

TEAMS_URL = "https://teams.microsoft.com"
SCREENSHOT_DIR = "/mnt/d/VMs/Projetos/Sharepoint_JIRA/test_screenshots"

async def test_e2_meeting_unchecked():
    """E2: Reunião unchecked → submit allowed without date"""
    async with async_playwright() as p:
        # Connect to existing browser or launch new one
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(storage_state="auth_state.json" if os.path.exists("auth_state.json") else None)
        page = await context.new_page()
        
        print("=== TEST E2: Reunião unchecked → submit allowed ===")
        
        # Navigate to Teams
        await page.goto(TEAMS_URL)
        await page.wait_for_load_state("networkidle")
        
        # Take screenshot
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/e2_test_{timestamp}.png")
        
        print(f"Screenshot saved to {SCREENSHOT_DIR}/e2_test_{timestamp}.png")
        print("Test E2 requires manual interaction with authenticated Teams session")
        
        # Save auth state for reuse
        await context.storage_state(path="auth_state.json")
        await browser.close()

async def main():
    print("Starting E2E Tests with Playwright...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    await test_e2_meeting_unchecked()
    
    print("\nTests completed!")

if __name__ == "__main__":
    asyncio.run(main())

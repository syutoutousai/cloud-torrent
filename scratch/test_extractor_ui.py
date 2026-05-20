import time
from playwright.sync_api import sync_playwright

def main():
    print("[*] Starting Playwright browser automation...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 800, "height": 900})
        
        print("[*] Navigating to http://localhost:3006...")
        page.goto("http://localhost:3006")
        page.wait_for_load_state("load")
        
        # Wait specifically for the magic icon to be loaded
        print("[*] Waiting for magic icon selector...")
        page.wait_for_selector(".title .status .magic.icon", timeout=5000)
        time.sleep(1)
        
        # 1. Take a screenshot of the initial homepage
        initial_img = "/home/naruto/.gemini/antigravity-cli/brain/1f83126f-7d83-45ca-acdd-2b7183c34d97/extractor_initial.jpg"
        page.screenshot(path=initial_img)
        print(f"[+] Captured initial homepage screenshot: {initial_img}")
        
        # 2. Toggle the Automated Seed Extractor Panel (click the magic icon)
        magic_icon = page.locator(".title .status .magic.icon")
        print("[*] Clicking magic icon to expand Automated Seed Extractor...")
        magic_icon.click()
        
        # Wait for the extractor panel template to load and render
        page.wait_for_selector(".seed-extractor-panel", timeout=5000)
        time.sleep(1)
        
        # 3. Take a screenshot of the expanded Extractor panel (Tab 1: Search Auto-Extract)
        panel_expanded_img = "/home/naruto/.gemini/antigravity-cli/brain/1f83126f-7d83-45ca-acdd-2b7183c34d97/extractor_expanded_search.jpg"
        page.screenshot(path=panel_expanded_img)
        print(f"[+] Captured expanded search extractor panel screenshot: {panel_expanded_img}")
        
        # 4. Click on the "Enrich & Audit Seed" tab
        enrich_tab = page.locator("text=Enrich & Audit Seed")
        print("[*] Switching to Enrich & Audit Seed tab...")
        enrich_tab.click()
        time.sleep(0.5)
        
        # 5. Type a raw 40-char infohash
        input_field = page.locator("input[placeholder*='Paste a 40-char infohash']")
        test_infohash = "45008e48c8800b7d7643337b2e70a634e4c69f6a"
        print(f"[*] Typing infohash: {test_infohash}...")
        input_field.focus()
        input_field.type(test_infohash)
        page.evaluate("document.querySelector('input[placeholder*=\"Paste a 40-char infohash\"]').dispatchEvent(new Event('input', { bubbles: true }));")
        time.sleep(1.5) # wait for angular ng-change audit trigger
        
        # 6. Capture screenshot of the active Dev State Quality Audit panel
        audit_panel_img = "/home/naruto/.gemini/antigravity-cli/brain/1f83126f-7d83-45ca-acdd-2b7183c34d97/extractor_audit_panel.jpg"
        page.screenshot(path=audit_panel_img)
        print(f"[+] Captured active Dev State Quality Audit panel screenshot: {audit_panel_img}")
        
        # 7. Click the "Enrich & Load Seed" button
        print("[*] Clicking 'Enrich & Load Seed' button via JS...")
        page.evaluate("document.querySelector('div[ng-click=\"enrichAndLoad()\"]').click()")
        time.sleep(3) # wait for API call and success message
        
        # 8. Capture screenshot of successful ingestion and confirmation alert
        success_img = "/home/naruto/.gemini/antigravity-cli/brain/1f83126f-7d83-45ca-acdd-2b7183c34d97/extractor_success_notification.jpg"
        page.screenshot(path=success_img)
        print(f"[+] Captured success alert screenshot: {success_img}")
        
        browser.close()
    print("[*] Playwright automation completed successfully.")

if __name__ == "__main__":
    main()

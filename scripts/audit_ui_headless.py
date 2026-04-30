from playwright.sync_api import sync_playwright
import time
import os

def run_playwright_screenshots():
    print("🚀 STARTING PLAYWRIGHT SCREENSHOTS...")
    os.makedirs("docs/assets/manual", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})

        print("Navigating to app...")
        page.goto("http://localhost:8501")
        page.wait_for_selector("text=Login", timeout=10000)
        page.screenshot(path="docs/assets/manual/screen_login.png")

        print("Logging in...")
        # Just try to click a user and login
        page.locator("text=Elisa Fosco").click()
        page.locator("text=START SHIFT").click()
        time.sleep(3)
        page.screenshot(path="docs/assets/manual/screen_dashboard.png")

        print("Navigating via Sidebar...")
        links = ["New Intake", "Observations", "Settings", "Reports"]
        for link in links:
            try:
                page.locator(f"text={link}").first.click()
                time.sleep(2) # wait for render
                page.screenshot(path=f"docs/assets/manual/screen_{link.lower().replace(' ', '_')}.png")
                print(f"Screenshot {link} done.")
            except Exception as e:
                print(f"Could not click {link}: {e}")
        browser.close()

if __name__ == "__main__":
    run_playwright_screenshots()

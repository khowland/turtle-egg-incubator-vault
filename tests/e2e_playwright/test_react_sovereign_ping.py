import pytest
from playwright.sync_api import Page, expect

# --- CONFIG ---
REACT_URL = "http://localhost:5173"

@pytest.mark.react_sanity
def test_react_app_is_sovereign(page: Page):
    """
    Sovereign React Sanity Test:
    1. Verify React app is listening on port 5173.
    2. Verify 'Today's Summary' heading exists (Dashboard).
    3. Verify Sidebar contains clinical navigation.
    4. Verify Version 'v9.6.6' is present.
    """
    # 1. Navigate
    print(f"\n[QA] Navigating to {REACT_URL}...")
    page.goto(REACT_URL, wait_until="networkidle")
    
    # 2. Check Heading
    print("[QA] Verifying Dashboard Heading...")
    heading = page.locator("h1:has-text(\"Today's Summary\")")
    expect(heading).to_be_visible(timeout=10000)
    
    # 3. Check Sidebar
    print("[QA] Verifying Sidebar Navigation...")
    sidebar = page.locator(".sidebar")
    expect(sidebar).to_be_visible()
    
    intake_link = sidebar.locator("a:has-text(\"New Intake\")")
    expect(intake_link).to_be_visible()
    
    # 4. Check Version
    print("[QA] Verifying System Version (v9.6.6)...")
    version = page.locator(".version-tag")
    expect(version).to_have_text("v9.6.6")
    
    # 5. Check KPI Metric (Still Incubating)
    print("[QA] Verifying KPI Metric Rendering...")
    metric = page.locator(".metric-card >> label:has-text(\"Still Incubating\")")
    expect(metric).to_be_visible()
    
    print("[QA] React Sovereignty Confirmed.")

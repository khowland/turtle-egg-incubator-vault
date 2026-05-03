from e2e_selectors import HEADING_INTAKE, HEADING_OBSERVATIONS, NAV_INTAKE, NAV_OBSERVATIONS
import pytest
from playwright.sync_api import Page, expect
from utils.db import get_supabase

# =============================================================================
# ENTERPRISE QA SCRIPT: Intake Workflow (Phase 3)
# Goal: 100% Mock-Free UI Interaction & DB Validation Pincer
# =============================================================================

@pytest.mark.e2e
def test_intake_hp_01_standard_bin(page: Page, login):
    """
    Test ID: INT-HP-01
    Validates a standard new intake workflow with zero mocking.
    """
    # 1. Clean Room Setup (Ensure test data is cleared first)
    sb = get_supabase()
    # Cleanup any previous failed runs for this specific test case
    sb.table("intake").update({"is_deleted": True}).eq("intake_name", "2026-TEST-HP01").execute()

    # 2. UI Automation (Playwright)
    login()
    page.locator(NAV_INTAKE).first.click()
    
    # Wait for DOM to stabilize
    expect(page.get_by_role("heading", name=HEADING_INTAKE)).to_be_visible(timeout=10000)

    # Fill out the form as a human would
    page.get_by_label("WINC Case #").fill("2026-TEST-HP01")
    page.get_by_role("textbox", name="Finder").fill("Jane Doe Automation")
    page.get_by_label("Days in Care").fill("3")

    # Fill ALL required intake form fields (8 total, not just 3)
    # Species selectbox — required; st.stop() if empty
    page.locator("[data-testid='stSelectbox']:has-text('Species')").click()
    page.wait_for_timeout(500)
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    page.wait_for_timeout(300)

    # Condition selectbox
    page.locator("[data-testid='stSelectbox']:has-text('Condition')").click()
    page.wait_for_timeout(300)
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Alive')").click()
    page.wait_for_timeout(300)

    # Egg Collection Method selectbox
    page.locator("[data-testid='stSelectbox']:has-text('Egg Collection Method')").click()
    page.wait_for_timeout(300)
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Natural')").click()
    page.wait_for_timeout(300)

    # Intake Circumstances
    page.get_by_role("textbox", name="Intake Circumstances").fill("Test intake for QA automation")
    
    # Set the egg count (Locate the New Eggs column in the data editor)
    # Streamlit data editors can be tricky; we click the cell and type.
    cell = page.locator("div[data-testid='stDataFrame']").locator("div.dvn-cell").filter(has_text="1").first
    cell.dblclick()
    page.keyboard.press("Backspace")
    page.keyboard.type("5")
    page.keyboard.press("Enter")

    # Save
    page.get_by_role("button", name="SAVE").click()

    # 3. Navigate to Observations manually (st.switch_page not always detected in Playwright)
    page.wait_for_timeout(2000)
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=10000)

    # 4. DB VERIFICATION PINCER (The Enterprise Mandate)
    # We do NOT trust the UI success. We query the DB to prove it.
    res_intake = sb.table("intake").select("intake_id").eq("intake_name", "2026-TEST-HP01").execute()
    assert len(res_intake.data) == 1, "FATAL: Intake row was not created in the database."
    intake_id = res_intake.data[0]["intake_id"]

    res_bins = sb.table("bin").select("bin_id, egg_count").eq("intake_id", intake_id).execute()
    assert len(res_bins.data) == 1, "FATAL: Bin row was not created in the database."
    assert res_bins.data[0]["egg_count"] == 5, "FATAL: Bin egg_count does not match UI input."

    res_eggs = sb.table("egg").select("egg_id").eq("bin_id", res_bins.data[0]["bin_id"]).execute()
    assert len(res_eggs.data) == 5, f"FATAL: Expected 5 eggs, found {len(res_eggs.data)} in database."

    # 5. Clean Room Teardown
    sb.table("intake").update({"is_deleted": True}).eq("intake_id", intake_id).execute()

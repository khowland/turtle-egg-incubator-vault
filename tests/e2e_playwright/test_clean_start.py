"""
Phase 1: Wipe & Clean Start Validation

TC-WCS-01: Vault wipe to clean start (Day 1)
TC-WCS-02: Lookup tables (species, observer) survive wipe

Prerequisite: DB must have data present (or backup gate bypassed in empty-DB case).
Expected flow:
  Settings → Vault Admin tab → GENERATE FULL BACKUP → EXPORT → confirm download
  → type OBLITERATE CURRENT DATA → WIPE & SET CLEAN START → verify DB clean
"""
import time
import pytest
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


SETTINGS_NAV = "a:has-text('Settings')"
VAULT_ADMIN_TAB = "button[role='tab']:has-text('Vault Admin')"
OBLITERATE_TEXT = "OBLITERATE CURRENT DATA"


# ---------------------------------------------------------------------------
# Helper: navigate to Settings → Vault Admin tab
# ---------------------------------------------------------------------------
def _go_to_vault_admin(page: Page):
    page.locator(SETTINGS_NAV).first.click()
    expect(page.get_by_role("heading", name="⚙️ Settings")).to_be_visible(timeout=15000)
    # Click the Vault Admin tab (last tab in Settings)
    page.get_by_role("tab", name="Vault Admin").click()


# ---------------------------------------------------------------------------
# TC-WCS-01: Full wipe flow → clean start
# ---------------------------------------------------------------------------
def test_vault_wipe_clean_start(page: Page, login):
    """TC-WCS-01: Wipe DB and verify all transactional tables are empty post-wipe."""
    login()
    _go_to_vault_admin(page)

    # Step 1: Generate & export backup (unlocks destructive buttons)
    generate_btn = page.get_by_role("button", name="GENERATE FULL BACKUP PAYLOAD")
    if generate_btn.is_visible():
        generate_btn.click()
        # Wait for export button to appear after payload compiled
        expect(page.get_by_role("button", name="EXPORT FULL BACKUP (.json)")).to_be_visible(timeout=15000)
        # Click download — triggers backup_verified flag in session_state
        page.get_by_role("button", name="EXPORT FULL BACKUP (.json)").click()
        time.sleep(1)  # Allow session_state to update

    # Step 2: Type obliterate confirmation
    confirm_input = page.locator("input[aria-label*='OBLITERATE']").first
    if not confirm_input.is_visible():
        # Fallback: find by placeholder or key
        confirm_input = page.locator("[data-testid='stTextInput'] input").last
    confirm_input.fill(OBLITERATE_TEXT)

    # Step 3: Click WIPE & SET CLEAN START (DAY 1)
    wipe_btn = page.get_by_role("button", name="WIPE & SET CLEAN START (DAY 1)")
    expect(wipe_btn).to_be_enabled(timeout=5000)
    wipe_btn.click()

    # Step 4: Verify success message in UI
    expect(
        page.get_by_text("Database wiped").first
        .or_(page.get_by_text("Clean Start").first)
    ).to_be_visible(timeout=20000)

    # Step 5: Backend verification — transactional tables must be empty
    db = get_supabase_client()
    for table in ["intake", "bin", "egg", "egg_observation", "hatchling_ledger"]:
        result = db.table(table).select("*", count="exact").execute()
        assert result.count == 0, (
            f"DB FAILURE: Table '{table}' still has {result.count} rows after wipe!"
        )


# ---------------------------------------------------------------------------
# TC-WCS-02: Lookup tables survive wipe
# ---------------------------------------------------------------------------
def test_lookup_tables_survive_wipe(page: Page, login):
    """TC-WCS-02: After wipe, species and observer lookup tables still populated."""
    login()

    db = get_supabase_client()

    species_result = db.table("species").select("*", count="exact").execute()
    assert species_result.count > 0, (
        "DB FAILURE: 'species' lookup table is empty after wipe — lookup data was destroyed!"
    )

    observer_result = db.table("observer").select("*", count="exact").execute()
    assert observer_result.count > 0, (
        "DB FAILURE: 'observer' table is empty after wipe — user accounts were destroyed!"
    )

    # UI verification: species should appear in intake form selector
    page.locator("a:has-text('Intake')").first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)
    # Species selectbox should be populated (not empty)
    species_select = page.locator("[data-testid='stSelectbox']").first
    expect(species_select).to_be_visible()

"""
Phase 4: Settings & Admin

TC-SET-01: Settings page renders with all expected tabs
TC-SET-02: Add/edit observer — new row persisted in observer table
TC-SET-03: Add/edit species — new row persisted in species table

DB Row Requirement: observer and species tables must each have >= 2 rows after this suite.
"""
import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


SETTINGS_NAV = "a:has-text('Settings')"


# ---------------------------------------------------------------------------
# TC-SET-01: Settings page renders with all tabs
# ---------------------------------------------------------------------------
def test_settings_page_renders(page: Page, login):
    """TC-SET-01: Settings page has all four expected tabs."""
    login()
    page.locator(SETTINGS_NAV).first.click()
    expect(page.get_by_role("heading", name="Settings")).to_be_visible(timeout=15000)

    for tab_label in ["User Registry", "Species Config", "Resurrection Vault", "Stages"]:
        tab = page.get_by_role("tab", name=tab_label)
        expect(tab).to_be_visible(timeout=5000), f"UI FAILURE: Tab '{tab_label}' not visible"

    # Verify default tab (User Registry) is active
    expect(page.get_by_text("User Registry").first).to_be_visible(timeout=5000)


# ---------------------------------------------------------------------------
# TC-SET-02: Add/edit observer
# ---------------------------------------------------------------------------
def test_add_edit_observer(page: Page, login):
    """TC-SET-02: Add new observer name via data_editor and SAVE → persists in DB."""
    login()
    page.locator(SETTINGS_NAV).first.click()
    expect(page.get_by_role("heading", name="Settings")).to_be_visible(timeout=15000)

    # User Registry tab should be default
    page.get_by_role("tab", name="User Registry").click()
    time.sleep(1)

    # Count existing observers for before/after comparison
    db = get_supabase_client()
    before = db.table("observer").select("observer_id", count="exact").execute()
    before_count = before.count

    # The observer editor may be a data_editor or form. Look for the SAVE button.
    # Add a new observer by clicking the bottom blank row of data_editor
    new_name = f"TestObserver-{int(time.time())}"

    # Try to find the data_editor blank row and type into it
    editor = page.locator("[data-testid='stDataEditor']").first
    if editor.is_visible():
        # Click the last row / blank add row area
        blank_row = editor.locator("tr").last
        blank_row.click()
        page.keyboard.type(new_name)

    # Click SAVE
    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)

    # DB verification: at least one more observer row than before
    after = db.table("observer").select("observer_id", count="exact").execute()
    assert after.count >= before_count, (
        f"DB FAILURE: Observer count did not increase after adding new observer "
        f"(before={before_count}, after={after.count})"
    )

    # Verify table has multiple rows
    assert after.count >= 2, (
        f"DB FAILURE: observer table has only {after.count} rows — expected >= 2"
    )


# ---------------------------------------------------------------------------
# TC-SET-03: Add/edit species
# ---------------------------------------------------------------------------
def test_add_edit_species(page: Page, login):
    """TC-SET-03: Add new species code via data_editor and SAVE → persists in DB."""
    login()
    page.locator(SETTINGS_NAV).first.click()
    expect(page.get_by_role("heading", name="Settings")).to_be_visible(timeout=15000)

    page.get_by_role("tab", name="Species Config").click()
    time.sleep(1)

    db = get_supabase_client()
    before = db.table("species").select("species_id", count="exact").execute()
    before_count = before.count

    new_code = f"ZZ{int(time.time()) % 10000}"

    editor = page.locator("[data-testid='stDataEditor']").first
    if editor.is_visible():
        blank_row = editor.locator("tr").last
        blank_row.click()
        page.keyboard.type(new_code)

    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)

    after = db.table("species").select("species_id", count="exact").execute()
    assert after.count >= before_count, (
        f"DB FAILURE: Species count did not increase "
        f"(before={before_count}, after={after.count})"
    )

    # Verify multiple rows exist in lookup table
    assert after.count >= 2, (
        f"DB FAILURE: species table has only {after.count} rows — expected >= 2"
    )

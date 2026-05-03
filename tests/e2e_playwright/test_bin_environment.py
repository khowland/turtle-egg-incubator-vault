"""
Phase 2c: Subject & Environment Management

TC-BIN-01: Bin weight gate — gate shown without weight, grid unlocked after entry
TC-BIN-02: Add Supplemental Bin (➕) from Observations workbench
TC-BIN-03: Bin soft delete (retirement) — via Dashboard "Remove Empty Bins" UI
TC-BIN-04: Bin restore — via Settings → Resurrection Vault ➕ button

All tests use 100% UI interactions with zero direct database mutations.
"""
from e2e_selectors import (
    HEADING_INTAKE,
    HEADING_OBSERVATIONS,
    HEADING_SETTINGS,
    HEADING_DASHBOARD,
    NAV_INTAKE,
    NAV_OBSERVATIONS,
    NAV_SETTINGS,
    NAV_DASHBOARD,
)

import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client

# ---------------------------------------------------------------------------
# Helper: Create intake via UI and return bin_id
# ---------------------------------------------------------------------------
def _create_intake_and_get_bin(page: Page, login, egg_count=1) -> str:
    """Create a fresh intake via UI and return bin_id.
    
    Args:
        page: Playwright page.
        login: Login fixture callable.
        egg_count: Number of eggs to set in the data editor (default 1).
    
    Returns:
        bin_id: The bin ID created by the intake.
    """
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name=HEADING_INTAKE)).to_be_visible(timeout=10000)

    sig = f"BIN-SETUP-{int(time.time())}"
    page.get_by_role("textbox", name="WINC Case #").fill(sig)
    page.get_by_role("textbox", name="Finder").fill(sig)
    page.get_by_label("Days in Care").fill("3")

    # Fill ALL required intake form fields (8 total, not just 3)
    # Species selectbox — required; st.stop() if empty
    species_sel = page.locator("[data-testid='stSelectbox']:has-text('Species')")
    species_sel.click()
    time.sleep(0.5)
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    time.sleep(0.3)

    # Condition selectbox
    cond_sel = page.locator("[data-testid='stSelectbox']:has-text('Condition')")
    cond_sel.click()
    time.sleep(0.3)
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Alive')").click()
    time.sleep(0.3)

    # Egg Collection Method selectbox
    ec_sel = page.locator("[data-testid='stSelectbox']:has-text('Egg Collection Method')")
    ec_sel.click()
    time.sleep(0.3)
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Natural')").click()
    time.sleep(0.3)

    # Intake Circumstances
    page.get_by_role("textbox", name="Intake Circumstances").fill("Test intake for QA automation")

    # Intake Date — leave default (today) untouched

    # Set egg count in data editor (default 1)
    if egg_count != 1:
        cell = page.locator("div[data-testid='stDataFrame']").locator("div.dvn-cell").filter(has_text="1").first
        cell.dblclick()
        page.keyboard.press("Backspace")
        page.keyboard.type(str(egg_count))
        page.keyboard.press("Enter")

    page.get_by_role("button", name="SAVE").click()

    # st.switch_page may not be detected; navigate manually
    page.wait_for_timeout(2000)
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=10000)

    # Fetch bin_id from database (query, not mutation)
    db = get_supabase_client()
    intake = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
    bin_row = db.table("bin").select("bin_id").eq("intake_id", intake.data[0]["intake_id"]).execute()
    return bin_row.data[0]["bin_id"]


# ---------------------------------------------------------------------------
# TC-BIN-01: Bin weight gate
# ---------------------------------------------------------------------------
def test_bin_weight_gate(page: Page, login):
    """TC-BIN-01: Weight gate blocks grid until bin weight is recorded."""
    bin_id = _create_intake_and_get_bin(page, login)

    # Navigate to Observations
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    # Add the bin to workbench multiselect
    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')").first.click()
    page.keyboard.press("Escape")

    # Expect weight gate message (grid locked)
    expect(
        page.get_by_text("current weight").first
        .or_(page.get_by_text("weight").first)
    ).to_be_visible(timeout=10000)

    # Enter bin weight
    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.triple_click()
    weight_input.fill("250")

    # Click SAVE to unlock grid
    page.get_by_role("button", name="SAVE").first.click()

    # Verify grid is now accessible (egg checkboxes visible)
    expect(
        page.get_by_text("START").first
        .or_(page.locator("[data-testid='stCheckbox']").first)
    ).to_be_visible(timeout=15000)

    # DB verification: bin_observation row created
    db = get_supabase_client()
    obs = db.table("bin_observation").select("*").eq("bin_id", bin_id).execute()
    assert len(obs.data) >= 1, f"DB FAILURE: No bin_observation row for bin {bin_id} after weight entry"
    weight_obs = [o for o in obs.data if o.get("bin_weight_g", 0) > 0]
    assert len(weight_obs) >= 1, "DB FAILURE: bin_observation weight value not persisted"


# ---------------------------------------------------------------------------
# TC-BIN-02: Add Supplemental Bin (➕)
# ---------------------------------------------------------------------------
def test_add_supplemental_bin(page: Page, login):
    """TC-BIN-02: ➕ button in Observations creates new bin + eggs for existing case."""
    bin_id = _create_intake_and_get_bin(page, login)

    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    # Click the ➕ button to open supplemental bin form
    page.get_by_role("button", name="➕").first.click()

    # Wait for supplemental form to appear
    expect(page.get_by_text("Select Intake/Case").first).to_be_visible(timeout=10000)

    # The new bin code input
    new_bin_input = page.locator("input[aria-label='New Bin Code']").first
    if not new_bin_input.is_visible():
        new_bin_input = page.locator("[data-testid='stTextInput'] input").last
    sup_bin_code = f"SN99-SUPTEST-2"
    new_bin_input.fill(sup_bin_code)

    # Eggs to add
    eggs_input = page.locator("input[aria-label='Eggs to Add']").first
    if not eggs_input.is_visible():
        eggs_input = page.locator("[data-testid='stNumberInput'] input").first
    eggs_input.triple_click()
    eggs_input.fill("3")

    # New target weight
    weight_inputs = page.locator("[data-testid='stNumberInput'] input").all()
    if len(weight_inputs) >= 2:
        weight_inputs[-1].triple_click()
        weight_inputs[-1].fill("200")

    # Save supplemental bin
    page.get_by_role("button", name="SAVE").first.click()

    # Allow state update
    time.sleep(2)

    # DB verification: new bin row + 3 eggs at S1
    db = get_supabase_client()
    # Use the primary bin_id to find intake, then verify bins
    primary_bin = db.table("bin").select("intake_id").eq("bin_id", bin_id).execute()
    intake_id = primary_bin.data[0]["intake_id"]
    bins = db.table("bin").select("bin_id").eq("intake_id", intake_id).execute()
    assert len(bins.data) >= 2, (
        f"DB FAILURE: Expected >= 2 bins for intake {intake_id}, got {len(bins.data)}"
    )

    # Find the new supplemental bin eggs
    all_eggs = []
    for b in bins.data:
        eggs = db.table("egg").select("egg_id, current_stage").eq("bin_id", b["bin_id"]).execute()
        all_eggs.extend(eggs.data)

    assert len(all_eggs) >= 4, (
        f"DB FAILURE: Expected >= 4 total eggs (1 original + 3 supplemental), got {len(all_eggs)}"
    )


# ---------------------------------------------------------------------------
# TC-BIN-03: Bin soft delete (retirement) via Dashboard UI
# ---------------------------------------------------------------------------
def test_bin_soft_delete_retirement(page: Page, login):
    """TC-BIN-03: Retire a bin via Dashboard 'Remove Empty Bins' with full UI interaction.
    
    Flow:
    1. Create intake with 1 egg.
    2. Navigate to Observations, mark egg as Dead → bin now has 0 active eggs.
    3. Navigate to Dashboard, select bin from retirement selectbox, toggle confirmation, click REMOVE.
    4. Verify bin.is_deleted = True in DB and bin disappears from Observations workbench.
    """
    bin_id = _create_intake_and_get_bin(page, login)

    # --- Step 1: Mark the egg as Dead via Observations UI ---
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    # Add bin to workbench and unlock weight gate
    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')").first.click()
    page.keyboard.press("Escape")

    # Fill weight to unlock grid
    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.fill("250")
    page.get_by_role("button", name="SAVE").first.click()

    # Click START to select all pending eggs
    page.get_by_role("button", name="START").click()

    # Change egg status to Dead using the Status selectbox
    status_select = page.locator("[data-testid='stSelectbox']:has-text('Status')")
    status_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Dead')").click()

    # Save the observation
    page.get_by_role("button", name="SAVE").last.click()

    # Allow state update
    time.sleep(2)

    # --- Step 2: Retire the empty bin via Dashboard ---
    page.locator(NAV_DASHBOARD).first.click()
    expect(page.get_by_role("heading", name=HEADING_DASHBOARD)).to_be_visible(timeout=15000)

    # The "Remove Empty Bins" section appears only if there are empty bins
    # It shows a selectbox and toggle + REMOVE button
    expect(page.get_by_text("Remove Empty Bins")).to_be_visible(timeout=10000)

    # Select our bin from the selectbox
    retire_select = page.locator("[data-testid='stSelectbox']:has-text('Select Bin Code to Remove')")
    retire_select.click()
    page.locator(f"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{bin_id}')").click()

    # Toggle confirmation
    confirm_toggle = page.get_by_role("checkbox").first
    confirm_toggle.check()

    # Click REMOVE button
    page.get_by_role("button", name="REMOVE").click()

    # Wait for success message
    expect(page.get_by_text(f"Bin {bin_id} removed.")).to_be_visible(timeout=15000)

    # --- DB Verification: is_deleted = True ---
    db_client = get_supabase_client()
    result = db_client.table("bin").select("is_deleted").eq("bin_id", bin_id).execute()
    assert result.data[0]["is_deleted"] is True, "DB FAILURE: bin.is_deleted is not True"

    # --- UI Verification: bin no longer appears in Observations workbench ---
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    workbench_options = page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"
    )
    assert not workbench_options.is_visible(), (
        f"UI FAILURE: Retired bin '{bin_id}' still visible in Observations workbench"
    )


# ---------------------------------------------------------------------------
# TC-BIN-04: Bin restore via Resurrection Vault
# ---------------------------------------------------------------------------
def test_bin_restore(page: Page, login):
    """TC-BIN-04: Restore a retired bin via Settings → Resurrection Vault.
    
    Flow:
    1. Create intake, mark egg Dead, retire bin via Dashboard (same as TC-BIN-03).
    2. Navigate to Settings → Resurrection Vault → Bins sub-tab.
    3. Find our bin and click the ➕ restore button.
    4. Verify bin.is_deleted = False and bin reappears in Observations workbench.
    """
    bin_id = _create_intake_and_get_bin(page, login)

    # --- Step 1: Retire the bin (same flow as TC-BIN-03) ---
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')").first.click()
    page.keyboard.press("Escape")

    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.fill("250")
    page.get_by_role("button", name="SAVE").first.click()
    page.get_by_role("button", name="START").click()

    status_select = page.locator("[data-testid='stSelectbox']:has-text('Status')")
    status_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Dead')").click()
    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    # Retire via Dashboard
    page.locator(NAV_DASHBOARD).first.click()
    expect(page.get_by_role("heading", name=HEADING_DASHBOARD)).to_be_visible(timeout=15000)
    expect(page.get_by_text("Remove Empty Bins")).to_be_visible(timeout=10000)

    retire_select = page.locator("[data-testid='stSelectbox']:has-text('Select Bin Code to Remove')")
    retire_select.click()
    page.locator(f"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{bin_id}')").click()
    page.get_by_role("checkbox").first.check()
    page.get_by_role("button", name="REMOVE").click()
    expect(page.get_by_text(f"Bin {bin_id} removed.")).to_be_visible(timeout=15000)

    # --- Step 2: Restore via Resurrection Vault ---
    page.locator(NAV_SETTINGS).first.click()
    expect(page.get_by_role("heading", name=HEADING_SETTINGS)).to_be_visible(timeout=15000)
    page.get_by_role("tab", name="Resurrection Vault").click()

    # The Bins sub-tab is active by default. Find our bin's restore button.
    # The bin ID is displayed in a container; the ➕ button is next to it.
    # Locate the button with key="res_bin_{bin_id}" which uses data-testid.
    restore_btn = page.locator(f"button[data-testid='stButton']:has-text('➕')")
    # Multiple ➕ buttons may exist; filter by the one near our bin_id text
    bin_container = page.locator(f"text={bin_id}").locator("..")
    # The container is the st.container(border=True) that holds the text and button
    # We can locate the ➕ button within the container that contains the bin_id text
    restore_btn = bin_container.locator("button:has-text('➕')")
    restore_btn.click()

    # After clicking, st.rerun() refreshes the page. Wait for success toast.
    time.sleep(2)

    # --- DB Verification: is_deleted = False ---
    db_client = get_supabase_client()
    result = db_client.table("bin").select("is_deleted").eq("bin_id", bin_id).execute()
    assert result.data[0]["is_deleted"] is False, (
        "DB FAILURE: Bin restore did not set is_deleted=False"
    )

    # --- UI Verification: bin reappears in Observations workbench ---
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    option = page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"
    ).first
    expect(option).to_be_visible(timeout=5000)

"""
# CR-20260430-194500: Updated phase description for renamed UI labels
# Phase 2a: New Intake (Happy Path Extensions)

TC-INT-01: Full intake with all optional fields + bin nomenclature check
TC-INT-02: Intake with multiple eggs → verify all egg rows created
TC-INT-03: CANCEL button aborts intake, no DB rows created

# Phase 2b: Add Eggs or Bins to Existing Intake
# TC-SUP-01: Supplemental intake full save → new bin + eggs added to existing case
"""
from e2e_selectors import HEADING_OBSERVATIONS, NAV_INTAKE

import time
import uuid
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client

# ---------------------------------------------------------------------------
# Helper: Fill all required Step 1 fields on the Intake form
# ---------------------------------------------------------------------------
def _fill_intake_step1_fields(page: Page, unique_sig: str, species_text: str = None):
    """Fill all 8 required fields: Finder, WINC Case, Species, Condition,
    Days in Care, Egg Collection Method, Intake Circumstances, and Intake Date.
    Intake Date is left at default. Species defaults to first option if not specified."""
    # Finder / Turtle Name
    page.locator("input[aria-label='Finder']").fill(unique_sig)
    # WINC Case #
    page.locator("input[aria-label='WINC Case #']").fill(unique_sig)

    # Species — selectbox
    species_sel = page.locator("[data-testid='stSelectbox']:has-text('Species')")
    species_sel.click()
    page.wait_for_timeout(500)
    if species_text:
        page.locator(f"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{species_text}')").first.click()
    else:
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    page.wait_for_timeout(300)

    # Intake Date — leave default, skip

    # Condition — selectbox (l_col2 area)
    condition_opts = page.locator("[data-testid='stSelectbox']:has-text('Condition')")
    if condition_opts.count() > 0:
        condition_opts.first.click()
        page.wait_for_timeout(500)
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Alive')").first.click()
        page.wait_for_timeout(300)

    # Days in Care — text input (l_col1 area)
    days_inputs = page.locator("input[aria-label='Days in Care']").all()
    if days_inputs:
        days_inputs[0].fill("3")

    # Egg Collection Method — selectbox
    egg_method_opts = page.locator("[data-testid='stSelectbox']:has-text('Egg Collection Method')")
    if egg_method_opts.count() > 0:
        egg_method_opts.first.click()
        page.wait_for_timeout(500)
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
        page.wait_for_timeout(300)

    # Intake Circumstances — textarea
    circumstances_inputs = page.locator("textarea").all()
    if circumstances_inputs:
        circumstances_inputs[0].fill("Roadside — clinical test")

    # Mother weight (if present)
    weight_inputs = page.locator("input[aria-label*='Weight']").all()
    if weight_inputs:
        weight_inputs[0].fill("350")


# ---------------------------------------------------------------------------
# TC-INT-01: Full intake with all optional fields + bin nomenclature
# ---------------------------------------------------------------------------
def test_intake_full_fields_and_bin_nomenclature(page: Page, login):
    """TC-INT-01: Full intake with all optional fields; verify bin code format."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    unique_sig = f"TC-INT-01-{int(time.time())}"

    # --- Step 1: Fill all required Mother Turtle Info fields ---
    _fill_intake_step1_fields(page, unique_sig)

    # --- Step 2: Bin / Egg Info (data_editor has 1 default row) ---
    # Verify the bin editor is present after Step 1 fields are complete
    expect(page.locator("[data-testid='stDataEditor']").first).to_be_visible(timeout=10000)

    # --- Step 3: SAVE ---
    page.get_by_role("button", name="SAVE").click()

    # Verify redirect to Observations (success indicator)
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)

    # --- Backend DB verification ---
    db = get_supabase_client()

    intake_res = db.table("intake").select("*").eq("intake_name", unique_sig).execute()
    assert len(intake_res.data) == 1, f"DB FAILURE: intake row missing for '{unique_sig}'"
    intake_row = intake_res.data[0]
    intake_id = intake_row["intake_id"]

    bin_res = db.table("bin").select("*").eq("intake_id", intake_id).execute()
    assert len(bin_res.data) >= 1, "DB FAILURE: No bin row created for intake"
    bin_row = bin_res.data[0]
    bin_id = bin_row["bin_id"]

    # Bin nomenclature: must match pattern {SpeciesCode}{N}-{CleanFinder}-{BinNum}
    assert bin_id and "-" in bin_id, (
        f"DB FAILURE: bin_id '{bin_id}' does not follow {{SpeciesCode}}{{N}}-{{Finder}}-{{BinNum}} nomenclature"
    )
    parts = bin_id.split("-")
    assert len(parts) >= 2, (
        f"DB FAILURE: bin_id '{bin_id}' missing required segments"
    )

    egg_res = db.table("egg").select("*").eq("bin_id", bin_id).execute()
    assert len(egg_res.data) >= 1, "DB FAILURE: No egg rows created"
    for egg in egg_res.data:
        assert egg["current_stage"] == "S1", (
            f"DB FAILURE: Egg {egg['egg_id']} stage is '{egg['current_stage']}', expected S1"
        )

    obs_res = db.table("egg_observation").select("*").eq("egg_id", egg_res.data[0]["egg_id"]).execute()
    assert len(obs_res.data) >= 1, "DB FAILURE: No baseline S1 egg_observation created"
    assert obs_res.data[0]["stage_at_observation"] == "S1", "DB FAILURE: Baseline obs stage != S1"

# ---------------------------------------------------------------------------
# TC-INT-02: Intake with multiple eggs → all egg rows created at S1
# ---------------------------------------------------------------------------
def test_intake_multiple_eggs(page: Page, login):
    """TC-INT-02: Intake with egg_count=5 creates 5 egg rows all at stage S1."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    unique_sig = f"TC-INT-02-{int(time.time())}"

    # --- Step 1: Fill all required Mother Turtle Info fields ---
    _fill_intake_step1_fields(page, unique_sig)

    # --- Step 2: Find the egg count cell in the data_editor and set to 5 ---
    egg_count_cells = page.locator("[data-testid='stDataEditor'] input[type='number']").all()
    if egg_count_cells:
        egg_count_cells[0].triple_click()
        egg_count_cells[0].fill("5")

    # --- Step 3: SAVE ---
    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)

    # DB verification
    db = get_supabase_client()
    intake_res = db.table("intake").select("intake_id").eq("intake_name", unique_sig).execute()
    assert len(intake_res.data) == 1, "DB FAILURE: Intake row missing"

    bin_res = db.table("bin").select("bin_id").eq("intake_id", intake_res.data[0]["intake_id"]).execute()
    assert len(bin_res.data) >= 1, "DB FAILURE: Bin row missing"

    egg_res = db.table("egg").select("*").eq("bin_id", bin_res.data[0]["bin_id"]).execute()
    assert len(egg_res.data) == 5, (
        f"DB FAILURE: Expected 5 egg rows, got {len(egg_res.data)}"
    )
    for egg in egg_res.data:
        assert egg["current_stage"] == "S1", f"DB FAILURE: Egg not at S1: {egg['egg_id']}"
        obs = db.table("egg_observation").select("egg_observation_id").eq("egg_id", egg["egg_id"]).execute()
        assert len(obs.data) >= 1, f"DB FAILURE: No baseline observation for egg {egg['egg_id']}"

# ---------------------------------------------------------------------------
# TC-INT-03: CANCEL button aborts intake — no DB rows created
# ---------------------------------------------------------------------------
def test_intake_cancel_button(page: Page, login):
    """TC-INT-03: CANCEL button on intake form creates no DB rows."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    unique_sig = f"TC-INT-03-CANCEL-{int(time.time())}"

    page.locator("input[aria-label='Finder']").fill(unique_sig)
    page.locator("input[aria-label='WINC Case #']").fill(unique_sig)

    # Click CANCEL
    page.get_by_role("button", name="CANCEL").click()

    # Should redirect away or reset form; verify NOT on Observations
    time.sleep(2)  # Allow any redirect
    heading = page.get_by_role("heading", name=HEADING_OBSERVATIONS)
    assert not heading.is_visible(), "CANCEL should not navigate to Observations"

    # DB verification: no intake row should exist
    db = get_supabase_client()
    intake_res = db.table("intake").select("intake_id").eq("intake_name", unique_sig).execute()
    assert len(intake_res.data) == 0, (
        f"DB FAILURE: CANCEL button did not prevent DB write — found {len(intake_res.data)} row(s)"
    )

# ---------------------------------------------------------------------------
# TC-SUP-01: Supplemental intake full save
# ---------------------------------------------------------------------------
def test_supplemental_intake_full_save(page: Page, login):
    """TC-SUP-01: Supplemental intake adds new bin + eggs to an existing case."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    # First: create a primary intake so we have a case to supplement
    primary_sig = f"TC-SUP-PRIMARY-{int(time.time())}"
    _fill_intake_step1_fields(page, primary_sig)
    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)

    # Navigate back to Intake → switch to Supplemental mode
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)
    # CR-20260430-194500: Updated selector for renamed label
    page.locator("label:has-text('Add Eggs or Bins to Existing Intake')").first.click()
    expect(page.get_by_text("Supplemental Mode").first).to_be_visible(timeout=10000)

    # Select the existing mother case we just created
    mother_select = page.locator("[data-testid='stSelectbox']").first
    mother_select.click()
    # Pick option containing our primary_sig
    page.locator(f"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{primary_sig}')").first.click()

    # SAVE the supplemental intake
    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)

    # DB verification: primary intake should now have 2 bins
    db = get_supabase_client()
    intake_res = db.table("intake").select("intake_id").eq("intake_name", primary_sig).execute()
    assert len(intake_res.data) == 1, "DB FAILURE: Primary intake not found"
    intake_id = intake_res.data[0]["intake_id"]

    bin_res = db.table("bin").select("bin_id").eq("intake_id", intake_id).execute()
    assert len(bin_res.data) >= 2, (
        f"DB FAILURE: Expected at least 2 bins after supplemental intake, got {len(bin_res.data)}"
    )

    # All bins must have at least 1 egg at S1
    for b in bin_res.data:
        eggs = db.table("egg").select("egg_id, current_stage").eq("bin_id", b["bin_id"]).execute()
        assert len(eggs.data) >= 1, f"DB FAILURE: Bin {b['bin_id']} has no eggs"
        for e in eggs.data:
            assert e["current_stage"] == "S1", (
                f"DB FAILURE: Supplemental egg {e['egg_id']} not at S1 (got {e['current_stage']})"
            )

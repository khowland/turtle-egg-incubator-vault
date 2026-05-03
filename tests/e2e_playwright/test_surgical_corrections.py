"""
Phase 3: Clinical Corrections (Surgical / Correction Mode)

TC-VOID-01: Enable Correction Mode toggle → surgical panel visible
TC-VOID-02: Void latest observation → stage rollback + is_deleted=true
TC-VOID-03: Void reason required (empty reason blocks or errors)
TC-VOID-04: Only latest observation is voidable (older rows disabled)
TC-VOID-05: RESTORE voided observation → is_deleted=false, stage restored
TC-VOID-06: S6 rollback voids hatchling_ledger (atomic integrity ISS-3)

DB Row Requirement: After suite, egg_observation table must have rows with
is_deleted=true (voided) AND is_deleted=false (active) — mixed state validated.
"""
from e2e_selectors import HEADING_OBSERVATIONS, NAV_INTAKE, NAV_OBSERVATIONS

import time
import uuid
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


# ---------------------------------------------------------------------------
# Helper: create intake via UI and return context dict
# ---------------------------------------------------------------------------
def _make_intake(page: Page, login, sig: str = None) -> dict:
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)
    sig = sig or f"VOID-SETUP-{int(time.time())}"
    page.locator("input[aria-label='Finder']").fill(sig)
    page.locator("input[aria-label='WINC Case #']").fill(sig)
    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)
    db = get_supabase_client()
    intake = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
    bin_row = db.table("bin").select("bin_id").eq(
        "intake_id", intake.data[0]["intake_id"]
    ).execute()
    bin_id = bin_row.data[0]["bin_id"]
    eggs = db.table("egg").select("egg_id").eq("bin_id", bin_id).execute()
    return {"bin_id": bin_id, "egg_ids": [e["egg_id"] for e in eggs.data], "sig": sig}

def _add_observation(db, egg_id: str, stage: str) -> str:
    """Insert an observation row directly (setup helper, not under test)."""
    obs_id = str(uuid.uuid4())
    db.table("egg_observation").insert({
        "egg_observation_id": obs_id,
        "egg_id": egg_id,
        "stage_at_observation": stage,
        "is_deleted": False,
    }).execute()
    db.table("egg").update({"current_stage": stage}).eq("egg_id", egg_id).execute()
    return obs_id

def _go_to_obs_correction_mode(page: Page, bin_id: str):
    """Navigate to Observations, add bin to workbench, pass weight gate, enable Correction Mode."""
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    wb = page.locator("[data-testid='stMultiSelect']").first
    wb.click()
    page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"
    ).first.click()
    page.keyboard.press("Escape")
    time.sleep(1)

    wi = page.locator("[data-testid='stNumberInput'] input").first
    wi.triple_click()
    wi.fill("300")
    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)

    # Enable Correction Mode toggle
    correction_toggle = page.locator("[data-testid='stToggle']:has-text('Correction Mode')").first
    if not correction_toggle.is_visible():
        correction_toggle = page.get_by_label("🛠️ Correction Mode").first
    correction_toggle.click()
    time.sleep(1)

# ---------------------------------------------------------------------------
# TC-VOID-01: Correction Mode toggle shows surgical panel
# ---------------------------------------------------------------------------
def test_correction_mode_toggle(page: Page, login):
    """TC-VOID-01: Enabling Correction Mode toggle reveals surgical search panel."""
    ctx = _make_intake(page, login)
    _go_to_obs_correction_mode(page, ctx["bin_id"])

    # Verify surgical panel visible: egg search select + void reason input
    expect(
        page.get_by_text("Select Egg for Surgery").first
        .or_(page.get_by_text("Surgery").first)
    ).to_be_visible(timeout=5000)

# ---------------------------------------------------------------------------
# TC-VOID-02: Void latest observation → is_deleted=true, stage rollback
# ---------------------------------------------------------------------------
def test_void_latest_observation(page: Page, login):
    """TC-VOID-02: Voiding latest obs sets is_deleted=true and rolls egg stage back."""
    ctx = _make_intake(page, login)
    egg_id = ctx["egg_ids"][0]
    db = get_supabase_client()

    # Add a second observation (S2) on top of the baseline S1
    obs_id_s2 = _add_observation(db, egg_id, "S2")

    _go_to_obs_correction_mode(page, ctx["bin_id"])

    # Select the egg in the surgery dropdown
    surgery_select = page.locator("[data-testid='stSelectbox']").first
    surgery_select.click()
    page.locator(
        f"[data-testid='stSelectboxVirtualDropdown'] li"
    ).first.click()  # First egg in list
    time.sleep(1)

    # Enter a void reason
    reason_input = page.locator("input[aria-label*='Void']").first
    if not reason_input.is_visible():
        reason_input = page.locator("[data-testid='stTextInput'] input").last
    reason_input.fill("TC-VOID-02: duplicate entry test")

    # Click the 🗑️ delete button on the latest (S2) observation row
    void_btn = page.locator("button:has-text('🗑️')").first
    expect(void_btn).to_be_visible(timeout=5000)
    void_btn.click()
    time.sleep(2)

    # DB verification: S2 obs is now soft-deleted
    obs = db.table("egg_observation").select(
        "is_deleted, void_reason"
    ).eq("egg_observation_id", obs_id_s2).execute()
    assert len(obs.data) >= 1, "DB FAILURE: obs_id_s2 not found"
    assert obs.data[0]["is_deleted"] is True, (
        "DB FAILURE: Voided observation is_deleted != True"
    )
    assert obs.data[0].get("void_reason"), "DB FAILURE: void_reason not persisted"

    # Egg stage should roll back to S1
    egg = db.table("egg").select("current_stage").eq("egg_id", egg_id).execute()
    assert egg.data[0]["current_stage"] == "S1", (
        f"DB FAILURE: Egg stage not rolled back to S1 after void (got {egg.data[0]['current_stage']})"
    )

    # Verify mixed state: is_deleted rows exist in table
    voided = db.table("egg_observation").select("egg_observation_id").eq(
        "is_deleted", True
    ).execute()
    assert len(voided.data) >= 1, "DB FAILURE: No voided rows found in egg_observation"

# ---------------------------------------------------------------------------
# TC-VOID-03: Void reason required
# ---------------------------------------------------------------------------
def test_void_reason_required(page: Page, login):
    """TC-VOID-03: Attempting to void without reason should show error or be blocked."""
    ctx = _make_intake(page, login)
    egg_id = ctx["egg_ids"][0]
    db = get_supabase_client()
    _add_observation(db, egg_id, "S2")

    _go_to_obs_correction_mode(page, ctx["bin_id"])

    # Select egg, leave reason EMPTY
    surgery_select = page.locator("[data-testid='stSelectbox']").first
    surgery_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    time.sleep(1)

    # Do NOT fill in void reason — attempt void
    void_btn = page.locator("button:has-text('🗑️')").first
    expect(void_btn).to_be_visible(timeout=5000)
    void_btn.click()
    time.sleep(1)

    # The S2 obs should NOT have been voided (reason was blank)
    obs = db.table("egg_observation").select(
        "is_deleted"
    ).eq("egg_id", egg_id).eq("stage_at_observation", "S2").execute()
    if obs.data:
        still_active = [o for o in obs.data if o["is_deleted"] is False]
        assert len(still_active) >= 1, (
            "DB FAILURE: Observation was voided without a reason — void reason gate failed"
        )

# ---------------------------------------------------------------------------
# TC-VOID-04: Only latest observation is voidable (older rows disabled)
# ---------------------------------------------------------------------------
def test_only_latest_obs_is_voidable(page: Page, login):
    """TC-VOID-04: With 3 observations, only the most recent 🗑️ button is enabled."""
    ctx = _make_intake(page, login)
    egg_id = ctx["egg_ids"][0]
    db = get_supabase_client()

    # Add S2 and S3S on top of baseline S1
    _add_observation(db, egg_id, "S2")
    time.sleep(0.1)
    _add_observation(db, egg_id, "S3S")

    _go_to_obs_correction_mode(page, ctx["bin_id"])

    surgery_select = page.locator("[data-testid='stSelectbox']").first
    surgery_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    time.sleep(1)

    # Collect all void buttons
    void_btns = page.locator("button:has-text('🗑️')").all()
    assert len(void_btns) >= 2, (
        f"UI FAILURE: Expected >= 2 void buttons for 3 observations, got {len(void_btns)}"
    )

    # Only the first (latest) should be enabled; older should be disabled
    enabled_btns = [b for b in void_btns if b.is_enabled()]
    disabled_btns = [b for b in void_btns if not b.is_enabled()]
    assert len(enabled_btns) == 1, (
        f"UI FAILURE: Expected exactly 1 enabled void button, got {len(enabled_btns)}"
    )
    assert len(disabled_btns) >= 1, (
        "UI FAILURE: Expected older observations to have disabled void buttons"
    )

# ---------------------------------------------------------------------------
# TC-VOID-05: RESTORE voided observation
# ---------------------------------------------------------------------------
def test_restore_voided_observation(page: Page, login):
    """TC-VOID-05: RESTORE button un-voids an observation (is_deleted=false)."""
    ctx = _make_intake(page, login)
    egg_id = ctx["egg_ids"][0]
    db = get_supabase_client()

    obs_id = _add_observation(db, egg_id, "S2")

    # Soft-delete the obs directly for setup
    db.table("egg_observation").update({
        "is_deleted": True,
        "void_reason": "Setup void for restore test"
    }).eq("egg_observation_id", obs_id).execute()

    _go_to_obs_correction_mode(page, ctx["bin_id"])

    surgery_select = page.locator("[data-testid='stSelectbox']").first
    surgery_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    time.sleep(1)

    # The RESTORE button should be visible for the voided record
    restore_btn = page.get_by_role("button", name="RESTORE").first
    expect(restore_btn).to_be_visible(timeout=5000)
    restore_btn.click()
    time.sleep(2)

    # DB verification: is_deleted should now be False
    obs = db.table("egg_observation").select(
        "is_deleted"
    ).eq("egg_observation_id", obs_id).execute()
    assert obs.data[0]["is_deleted"] is False, (
        "DB FAILURE: RESTORE did not set is_deleted=False"
    )

# ---------------------------------------------------------------------------
# TC-VOID-06: S6 rollback voids hatchling_ledger (ISS-3)
# ---------------------------------------------------------------------------
def test_s6_rollback_voids_ledger(page: Page, login):
    """TC-VOID-06: Voiding a Hatched (S6) observation also voids hatchling_ledger."""
    ctx = _make_intake(page, login)
    egg_id = ctx["egg_ids"][0]
    db = get_supabase_client()

    # Setup: advance to S5 then S6, insert hatchling_ledger row
    _add_observation(db, egg_id, "S5")
    s6_obs_id = _add_observation(db, egg_id, "S6")
    db.table("egg").update({"status": "Transferred"}).eq("egg_id", egg_id).execute()
    ledger_id = str(uuid.uuid4())
    db.table("hatchling_ledger").insert({
        "hatchling_ledger_id": ledger_id,
        "egg_id": egg_id,
        "is_deleted": False,
        "notes": "Auto-recorded on S6 batch transition",
    }).execute()

    _go_to_obs_correction_mode(page, ctx["bin_id"])

    surgery_select = page.locator("[data-testid='stSelectbox']").first
    surgery_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
    time.sleep(1)

    reason_input = page.locator("[data-testid='stTextInput'] input").last
    reason_input.fill("TC-VOID-06: S6 rollback test")

    void_btn = page.locator("button:has-text('🗑️')").first
    expect(void_btn).to_be_visible(timeout=5000)
    void_btn.click()
    time.sleep(3)

    # DB: S6 observation should be voided
    obs = db.table("egg_observation").select(
        "is_deleted"
    ).eq("egg_observation_id", s6_obs_id).execute()
    assert obs.data[0]["is_deleted"] is True, (
        "DB FAILURE: S6 observation not voided"
    )

    # DB: hatchling_ledger row should be soft-deleted (atomic rollback ISS-3)
    ledger = db.table("hatchling_ledger").select(
        "is_deleted"
    ).eq("hatchling_ledger_id", ledger_id).execute()
    assert len(ledger.data) >= 1, "DB FAILURE: hatchling_ledger row disappeared"
    assert ledger.data[0]["is_deleted"] is True, (
        "DB FAILURE: hatchling_ledger not voided during S6 rollback (ISS-3 atomic integrity failed)"
    )

    # Egg stage should revert to S5
    egg = db.table("egg").select("current_stage").eq("egg_id", egg_id).execute()
    assert egg.data[0]["current_stage"] == "S5", (
        f"DB FAILURE: Egg not reverted to S5 after S6 rollback (got {egg.data[0]['current_stage']})"
    )

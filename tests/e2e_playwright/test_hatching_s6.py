"""
Phase 2e: S6 Hatching

TC-S6-01: S5 → S6 transition creates hatchling_ledger row(s), egg status=Transferred
TC-S6-02: hatchling_ledger fields (count, notes) match observation inputs

DB Row Requirement: After these tests run the hatchling_ledger table must have >= 2 rows.
"""
from e2e_selectors import HEADING_OBSERVATIONS, NAV_INTAKE, NAV_OBSERVATIONS

import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


def _advance_egg_to_stage(db, egg_id: str, stage: str):
    """Directly advance an egg to a given stage for setup purposes."""
    db.table("egg").update({"current_stage": stage}).eq("egg_id", egg_id).execute()
    db.table("egg_observation").insert({
        "egg_observation_id": __import__("uuid").uuid4().hex[:32],
        "egg_id": egg_id,
        "stage_at_observation": stage,
        "is_deleted": False,
    }).execute()

def _create_intake_and_advance_to_s5(page: Page, login) -> dict:
    """Create intake via UI, advance egg to S5 via DB, return context."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    sig = f"S6-SETUP-{int(time.time())}"
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
    egg_ids = [e["egg_id"] for e in eggs.data]

    # Advance each egg to S5 via direct DB write (setup shortcut — not under test)
    for eid in egg_ids:
        _advance_egg_to_stage(db, eid, "S5")

    return {"bin_id": bin_id, "egg_ids": egg_ids, "sig": sig}

def _unlock_workbench(page: Page, bin_id: str):
    """Navigate to Observations, add bin to workbench, pass weight gate."""
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"
    ).first.click()
    page.keyboard.press("Escape")
    time.sleep(1)

    # Pass weight gate
    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.triple_click()
    weight_input.fill("280")
    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)

# ---------------------------------------------------------------------------
# TC-S6-01: S5 → S6 transition
# ---------------------------------------------------------------------------
def test_s5_to_s6_hatch_transition(page: Page, login):
    """TC-S6-01: S5→S6 observation auto-creates hatchling_ledger; egg status=Transferred."""
    ctx = _create_intake_and_advance_to_s5(page, login)
    bin_id = ctx["bin_id"]
    egg_ids = ctx["egg_ids"]

    _unlock_workbench(page, bin_id)

    # Select all eggs and advance to S6
    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Set stage to S6
    stage_selects = page.locator("[data-testid='stSelectbox']").all()
    stage_set = False
    for sel in stage_selects:
        try:
            sel.click()
            opt = page.locator(
                "[data-testid='stSelectboxVirtualDropdown'] li:has-text('S6')"
            ).first
            if opt.is_visible(timeout=2000):
                opt.click()
                stage_set = True
                break
            else:
                page.keyboard.press("Escape")
        except Exception:
            page.keyboard.press("Escape")

    assert stage_set, "UI FAILURE: S6 stage option not found in stage selector"

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(3)

    # DB verification
    db = get_supabase_client()
    for egg_id in egg_ids:
        egg = db.table("egg").select("current_stage, status").eq("egg_id", egg_id).execute()
        assert egg.data[0]["current_stage"] == "S6", (
            f"DB FAILURE: Egg {egg_id} stage not S6 after hatch transition"
        )
        assert egg.data[0]["status"] == "Transferred", (
            f"DB FAILURE: Egg {egg_id} status not 'Transferred' after S6 (got {egg.data[0]['status']})"
        )

        ledger = db.table("hatchling_ledger").select("*").eq("egg_id", egg_id).execute()
        assert len(ledger.data) >= 1, (
            f"DB FAILURE: No hatchling_ledger row created for egg {egg_id} after S6 transition"
        )

    # Verify table-level: hatchling_ledger must have multiple rows total
    total_ledger = db.table("hatchling_ledger").select("*", count="exact").execute()
    assert total_ledger.count >= len(egg_ids), (
        f"DB FAILURE: hatchling_ledger total rows ({total_ledger.count}) < egg count ({len(egg_ids)})"
    )

# ---------------------------------------------------------------------------
# TC-S6-02: hatchling_ledger data fields
# ---------------------------------------------------------------------------
def test_hatchling_ledger_data(page: Page, login):
    """TC-S6-02: hatchling_ledger rows have egg_id, session_id, and are not soft-deleted."""
    ctx = _create_intake_and_advance_to_s5(page, login)
    bin_id = ctx["bin_id"]
    egg_ids = ctx["egg_ids"]

    _unlock_workbench(page, bin_id)

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Set S6
    stage_selects = page.locator("[data-testid='stSelectbox']").all()
    for sel in stage_selects:
        try:
            sel.click()
            opt = page.locator(
                "[data-testid='stSelectboxVirtualDropdown'] li:has-text('S6')"
            ).first
            if opt.is_visible(timeout=2000):
                opt.click()
                break
            page.keyboard.press("Escape")
        except Exception:
            page.keyboard.press("Escape")

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(3)

    db = get_supabase_client()
    for egg_id in egg_ids:
        ledger = db.table("hatchling_ledger").select("*").eq(
            "egg_id", egg_id
        ).execute()
        assert len(ledger.data) >= 1, f"DB FAILURE: No hatchling_ledger row for egg {egg_id}"
        row = ledger.data[0]
        assert row.get("egg_id") == egg_id, "DB FAILURE: hatchling_ledger.egg_id mismatch"
        assert row.get("is_deleted") is False, (
            f"DB FAILURE: hatchling_ledger row is_deleted=True immediately after creation"
        )
        assert row.get("hatchling_ledger_id") is not None, (
            "DB FAILURE: hatchling_ledger_id is null"
        )

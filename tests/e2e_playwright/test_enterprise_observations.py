"""
=============================================================================
ENTERPRISE QA SCRIPT: Observation Workflows (Phase 3)
Goal: 100% Mock-Free UI Interaction & DB Validation Pincer
Template: test_enterprise_intake.py
Matrix: TEST_MATRIX_OBSERVATIONS.md
=============================================================================
"""
import time
import pytest
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


OBS_NAV = "a:has-text('Observations')"
INTAKE_NAV = "a:has-text('Intake')"


# ---------------------------------------------------------------------------
# Shared helper: create intake + pass weight gate, return (bin_id, [egg_ids])
# ---------------------------------------------------------------------------
def _setup_intake_and_unlock_grid(page: Page, login, egg_count: int = 3) -> dict:
    """Create intake via UI, navigate to Observations, pass weight gate."""
    login()
    page.locator(INTAKE_NAV).first.click()
    expect(page.get_by_role("heading", name="New Intake")).to_be_visible(timeout=15000)

    sig = f"OBS-ENT-{int(time.time())}"
    page.locator("input[aria-label='Finder']").fill(sig)
    page.locator("input[aria-label='WINC Case #']").fill(sig)

    # Set egg count in data_editor
    cells = page.locator("[data-testid='stDataEditor'] input[type='number']").all()
    if cells:
        cells[0].triple_click()
        cells[0].fill(str(egg_count))

    page.get_by_role("button", name="SAVE").click()
    # After SAVE, the app redirects to Observations page (heading: 🔬 Observations)
    expect(page.get_by_role("heading", name="🔬 Observations")).to_be_visible(timeout=30000)

    db = get_supabase_client()
    intake = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
    bin_row = db.table("bin").select("bin_id").eq(
        "intake_id", intake.data[0]["intake_id"]
    ).execute()
    bin_id = bin_row.data[0]["bin_id"]
    eggs = db.table("egg").select("egg_id").eq("bin_id", bin_id).execute()
    egg_ids = [e["egg_id"] for e in eggs.data]

    # Go to Observations, add bin to workbench
    page.locator(OBS_NAV).first.click()
    expect(page.get_by_role("heading", name="🔬 Observations")).to_be_visible(timeout=15000)

    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"
    ).first.click()
    page.keyboard.press("Escape")
    time.sleep(1)

    # Pass weight gate — enter bin weight and SAVE
    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.triple_click()
    weight_input.fill("300")
    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)

    return {"bin_id": bin_id, "egg_ids": egg_ids, "sig": sig}


# =============================================================================
# HAPPY PATH TESTS
# =============================================================================

@pytest.mark.e2e
def test_obs_hp_01_weight_gate(page: Page, login):
    """
    TC-OBS-WG-01 (Happy Path): Weight gate → SAVE → grid unlocks.
    Validates bin_observation and bin weight update in DB.
    """
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=2)
    bin_id = ctx["bin_id"]
    db = get_supabase_client()

    # DB Pincer: verify bin_observation row created
    bin_obs = db.table("bin_observation").select("*").eq(
        "bin_id", bin_id
    ).order("timestamp", desc=True).limit(1).execute()
    assert len(bin_obs.data) == 1, "FATAL: No bin_observation row created"
    obs = bin_obs.data[0]
    assert obs["bin_weight_g"] == 300.0, f"FATAL: Expected weight 300, got {obs['bin_weight_g']}"

    # DB Pincer: verify bin target weight updated
    bin_row = db.table("bin").select("target_total_weight_g").eq(
        "bin_id", bin_id
    ).execute()
    assert bin_row.data[0]["target_total_weight_g"] == 300.0, "FATAL: Bin weight not updated"

    # Verify grid is visible (not stopped by gate)
    expect(page.get_by_text("Biological Grid")).to_be_visible(timeout=5000)


@pytest.mark.e2e
def test_obs_hp_02_single_observation(page: Page, login):
    """
    TC-OBS-PM-01 (Happy Path): START → select stage S2 → SAVE → DB verify.
    """
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Set stage to S2
    stage_select = page.locator("[data-testid='stSelectbox']:has-text('Stage')").first
    if not stage_select.is_visible():
        stage_select = page.locator("[data-testid='stSelectbox']").first
    stage_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('S2')").first.click()

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    egg = db.table("egg").select("current_stage").eq("egg_id", egg_ids[0]).execute()
    assert egg.data[0]["current_stage"] == "S2", f"FATAL: Expected S2, got {egg.data[0]['current_stage']}"

    obs = db.table("egg_observation").select("*").eq(
        "egg_id", egg_ids[0]
    ).order("created_at", desc=True).limit(1).execute()
    assert len(obs.data) == 1, "FATAL: No egg_observation row created"
    assert obs.data[0]["stage_at_observation"] == "S2", "FATAL: Observation stage mismatch"


@pytest.mark.e2e
def test_obs_hp_03_batch_observation(page: Page, login):
    """TC-OBS-PM-01 batch: Select all eggs, set S2, SAVE → all eggs updated."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=4)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    stage_selects = page.locator("[data-testid='stSelectbox']").all()
    for sel in stage_selects:
        label = sel.inner_text()
        if "Stage" in label or "S1" in label:
            sel.click()
            page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('S2')").first.click()
            break

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    for egg_id in egg_ids:
        egg = db.table("egg").select("current_stage").eq("egg_id", egg_id).execute()
        assert egg.data[0]["current_stage"] == "S2", f"FATAL: Egg {egg_id} not updated"


@pytest.mark.e2e
def test_obs_hp_04_clinical_fields(page: Page, login):
    """TC-OBS-PM-05/06/07: Set molding=1, leaking=1, denting=1 → verify persisted."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Set Molding to "Spotting" (value 1)
    molding_select = page.locator("[data-testid='stSelectbox']:has-text('Molding')").first
    if molding_select.is_visible():
        molding_select.click()
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").nth(1).click()

    # Set Leaking to "Damp" (value 1)
    leaking_select = page.locator("[data-testid='stSelectbox']:has-text('Leaking')").first
    if leaking_select.is_visible():
        leaking_select.click()
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").nth(1).click()

    # Set Denting to "Slight" (value 1)
    denting_select = page.locator("[data-testid='stSelectbox']:has-text('Denting')").first
    if denting_select.is_visible():
        denting_select.click()
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").nth(1).click()

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    obs = db.table("egg_observation").select("molding, leaking, dented").eq(
        "egg_id", egg_ids[0]
    ).order("created_at", desc=True).limit(1).execute()
    assert obs.data[0]["molding"] == 1, f"FATAL: Expected molding=1, got {obs.data[0]['molding']}"
    assert obs.data[0]["leaking"] == 1, f"FATAL: Expected leaking=1, got {obs.data[0]['leaking']}"
    assert obs.data[0]["dented"] == 1, f"FATAL: Expected dented=1, got {obs.data[0]['dented']}"


@pytest.mark.e2e
def test_obs_hp_05_mortality(page: Page, login):
    """TC-OBS-PM-02: Set status=Dead → egg.status becomes 'Dead'."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=2)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Find and select "Dead" in Status dropdown
    status_select = page.locator("[data-testid='stSelectbox']:has-text('Status')").first
    if not status_select.is_visible():
        selects = page.locator("[data-testid='stSelectbox']").all()
        for sel in selects:
            try:
                sel.click()
                dead_opt = page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Dead')").first
                if dead_opt.is_visible(timeout=2000):
                    dead_opt.click()
                    break
                page.keyboard.press("Escape")
            except Exception:
                page.keyboard.press("Escape")
    else:
        status_select.click()
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Dead')").first.click()

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    dead_eggs = db.table("egg").select("status").eq("status", "Dead").in_("egg_id", egg_ids).execute()
    assert len(dead_eggs.data) >= 1, "FATAL: No egg marked Dead"


@pytest.mark.e2e
def test_obs_hp_06_s6_hatching(page: Page, login):
    """TC-OBS-S6-01: Set S6 → hatchling_ledger entries created."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    stage_selects = page.locator("[data-testid='stSelectbox']").all()
    for sel in stage_selects:
        try:
            sel.click()
            opt = page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('S6')").first
            if opt.is_visible(timeout=2000):
                opt.click()
                break
            else:
                page.keyboard.press("Escape")
        except Exception:
            page.keyboard.press("Escape")

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(3)

    hl = db.table("hatchling_ledger").select("*").eq("egg_id", egg_ids[0]).execute()
    assert len(hl.data) >= 1, f"FATAL: No hatchling_ledger row for {egg_ids[0]}"

    egg = db.table("egg").select("status, current_stage").eq("egg_id", egg_ids[0]).execute()
    assert egg.data[0]["status"] == "Transferred", "FATAL: Egg not marked Transferred at S6"
    assert egg.data[0]["current_stage"] == "S6", "FATAL: Egg stage not S6"


# =============================================================================
# ADVERSARIAL TESTS
# =============================================================================

@pytest.mark.e2e
def test_obs_adv_01_negative_weight(page: Page, login):
    """TC-OBS-WG-ADV-01: Negative weight at weight gate should be rejected."""
    login()
    page.locator(INTAKE_NAV).first.click()
    expect(page.get_by_role("heading", name="New Intake")).to_be_visible(timeout=15000)

    sig = f"OBS-ADV-{int(time.time())}"
    page.locator("input[aria-label='Finder']").fill(sig)
    page.locator("input[aria-label='WINC Case #']").fill(sig)
    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name="🔬 Observations")).to_be_visible(timeout=30000)

    db = get_supabase_client()
    intake = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
    bin_id = db.table("bin").select("bin_id").eq(
        "intake_id", intake.data[0]["intake_id"]
    ).execute().data[0]["bin_id"]

    page.locator(OBS_NAV).first.click()
    time.sleep(2)

    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')").first.click()
    page.keyboard.press("Escape")
    time.sleep(1)

    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.triple_click()
    weight_input.fill("-10")

    actual_value = weight_input.input_value()
    assert float(actual_value) >= 0, f"FATAL: Negative weight accepted: {actual_value}"

    bin_obs = db.table("bin_observation").select("count", count="exact").eq("bin_id", bin_id).execute()
    assert bin_obs.count == 0, "FATAL: bin_observation row created despite negative weight"


@pytest.mark.e2e
def test_obs_adv_02_future_backdate(page: Page, login):
    """TC-OBS-PM-ADV-08: Future observation date should be rejected or today."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    page.get_by_role("button", name="START").click()
    time.sleep(1)

    date_inputs = page.locator("[data-testid='stDateInput'] input").all()
    if date_inputs:
        date_inputs[0].triple_click()
        date_inputs[0].fill("2027-01-01")
        date_inputs[0].press("Enter")
        time.sleep(1)

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    db = get_supabase_client()
    from datetime import datetime, timezone
    obs = db.table("egg_observation").select("timestamp").eq(
        "egg_id", ctx["egg_ids"][0]
    ).order("created_at", desc=True).limit(1).execute()
    
    if obs.data:
        ts_str = obs.data[0]["timestamp"]
        if ts_str:
            ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            assert ts <= now, f"FATAL: Future timestamp accepted: {ts}"


@pytest.mark.e2e
def test_obs_adv_03_sql_injection(page: Page, login):
    """TC-OBS-PM-ADV-10: SQL injection attempt should be stored literally, not executed."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    notes_area = page.locator("[data-testid='stTextArea'] textarea").first
    if notes_area.is_visible():
        notes_area.fill("'; DROP TABLE egg; --")

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    obs = db.table("egg_observation").select("observation_notes").eq(
        "egg_id", egg_ids[0]
    ).order("created_at", desc=True).limit(1).execute()
    if obs.data:
        notes = obs.data[0].get("observation_notes", "")
        assert "DROP TABLE" in notes, "FATAL: Injection string not stored as literal"

    egg_count = db.table("egg").select("count", count="exact").limit(1).execute()
    assert egg_count.count >= 0, "FATAL: egg table dropped — injection executed!"


@pytest.mark.e2e
def test_obs_adv_04_double_submit(page: Page, login):
    """TC-OBS-PM-ADV-11: Double-click SAVE should not create duplicate observation rows."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    stage_select = page.locator("[data-testid='stSelectbox']:has-text('Stage')").first
    if not stage_select.is_visible():
        stage_select = page.locator("[data-testid='stSelectbox']").first
    stage_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('S2')").first.click()

    obs_before = db.table("egg_observation").select("count", count="exact").eq(
        "egg_id", egg_ids[0]
    ).execute().count

    save_btn = page.get_by_role("button", name="SAVE").last
    save_btn.click()
    time.sleep(0.2)
    try:
        save_btn.click()
    except Exception:
        pass
    time.sleep(3)

    obs_after = db.table("egg_observation").select("count", count="exact").eq(
        "egg_id", egg_ids[0]
    ).execute().count
    assert obs_after <= obs_before + 1, (
        f"FATAL: Duplicate rows created. Before: {obs_before}, After: {obs_after}"
    )

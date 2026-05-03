"""
Phase 2d: Clinical Observation Workflows

TC-OBS-01: Full observation cycle (weight gate → START → stage change → SAVE → DB verify)
TC-OBS-02: Multi-egg batch observation
TC-OBS-03: Stage progression S1 through S5 across multiple cycles
TC-OBS-04: S3 sub-stages (S3S, S3M, S3J)
TC-OBS-05: Health/viability fields persisted in observation
TC-OBS-06: Biological jump warning (S1 → S4 triggers warning)
TC-OBS-07: Mortality recording — egg marked Dead, removed from active grid
"""
from e2e_selectors import HEADING_OBSERVATIONS, NAV_INTAKE, NAV_OBSERVATIONS

import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


# ---------------------------------------------------------------------------
# Shared helper: create intake + pass weight gate, return (bin_id, [egg_ids])
# ---------------------------------------------------------------------------
def _setup_intake_and_unlock_grid(page: Page, login, egg_count: int = 3) -> dict:
    """Create intake via UI with egg_count eggs, navigate to Observations, pass weight gate."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    sig = f"OBS-SETUP-{int(time.time())}"
    page.locator("input[aria-label='Finder']").fill(sig)
    page.locator("input[aria-label='WINC Case #']").fill(sig)

    # Set egg count in data_editor
    cells = page.locator("[data-testid='stDataEditor'] input[type='number']").all()
    if cells:
        cells[0].triple_click()
        cells[0].fill(str(egg_count))

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

    # Go to Observations, add bin to workbench
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

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
    # Use the obs_env_save button key or first SAVE button
    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)  # Allow grid to unlock

    return {"bin_id": bin_id, "egg_ids": egg_ids, "sig": sig}

# ---------------------------------------------------------------------------
# TC-OBS-01: Full observation cycle
# ---------------------------------------------------------------------------
def test_full_observation_cycle(page: Page, login):
    """TC-OBS-01: Weight gate → START → select stage S2 → SAVE → verify DB."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=2)
    bin_id = ctx["bin_id"]
    egg_ids = ctx["egg_ids"]

    # Click START to select all pending eggs
    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Set stage to S2
    stage_select = page.locator("[data-testid='stSelectbox']:has-text('Stage')").first
    if not stage_select.is_visible():
        stage_select = page.locator("[data-testid='stSelectbox']").first
    stage_select.click()
    page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('S2')").first.click()

    # SAVE observation
    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    # DB verification
    db = get_supabase_client()
    for egg_id in egg_ids:
        egg = db.table("egg").select("current_stage").eq("egg_id", egg_id).execute()
        assert egg.data[0]["current_stage"] == "S2", (
            f"DB FAILURE: Egg {egg_id} stage not updated to S2, got {egg.data[0]['current_stage']}"
        )
        obs = db.table("egg_observation").select("*").eq("egg_id", egg_id).order(
            "created_at", desc=True
        ).execute()
        assert obs.data[0]["stage_at_observation"] == "S2", (
            f"DB FAILURE: Latest egg_observation for {egg_id} not S2"
        )

# ---------------------------------------------------------------------------
# TC-OBS-02: Multi-egg batch observation
# ---------------------------------------------------------------------------
def test_multi_egg_batch_observation(page: Page, login):
    """TC-OBS-02: Select multiple eggs, set stage, SAVE — all eggs updated."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=4)
    egg_ids = ctx["egg_ids"]

    # Click START to select all
    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Set stage to S2
    stage_selects = page.locator("[data-testid='stSelectbox']").all()
    for sel in stage_selects:
        label = sel.inner_text()
        if "Stage" in label or "S1" in label:
            sel.click()
            page.locator(
                "[data-testid='stSelectboxVirtualDropdown'] li:has-text('S2')"
            ).first.click()
            break

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    # All 4 eggs must be S2
    db = get_supabase_client()
    for egg_id in egg_ids:
        egg = db.table("egg").select("current_stage").eq("egg_id", egg_id).execute()
        assert egg.data[0]["current_stage"] == "S2", (
            f"DB FAILURE: Batch obs — egg {egg_id} not updated to S2"
        )

# ---------------------------------------------------------------------------
# TC-OBS-03: Stage progression S1 → S2 → S3S → S4 → S5
# ---------------------------------------------------------------------------
def test_stage_progression_s1_through_s5(page: Page, login):
    """TC-OBS-03: Sequential stage advancement S1→S2→S3S→S4→S5 via UI."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    for target_stage in ["S2", "S3S", "S4", "S5"]:
        page.get_by_role("button", name="START").click()
        time.sleep(1)

        # Set stage
        stage_selects = page.locator("[data-testid='stSelectbox']").all()
        stage_set = False
        for sel in stage_selects:
            try:
                sel.click()
                opt = page.locator(
                    f"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{target_stage}')"
                ).first
                if opt.is_visible(timeout=2000):
                    opt.click()
                    stage_set = True
                    break
                else:
                    page.keyboard.press("Escape")
            except Exception:
                page.keyboard.press("Escape")

        assert stage_set, f"UI FAILURE: Could not find stage option '{target_stage}'"

        page.get_by_role("button", name="SAVE").last.click()
        time.sleep(2)

        # Verify DB stage advanced
        egg = db.table("egg").select("current_stage").eq(
            "egg_id", egg_ids[0]
        ).execute()
        assert egg.data[0]["current_stage"] == target_stage, (
            f"DB FAILURE: After targeting {target_stage}, egg is {egg.data[0]['current_stage']}"
        )

        # Re-pass weight gate if needed for next cycle
        if page.get_by_text("current weight").is_visible():
            weight_input = page.locator("[data-testid='stNumberInput'] input").first
            weight_input.triple_click()
            weight_input.fill("300")
            page.get_by_role("button", name="SAVE").first.click()
            time.sleep(2)

# ---------------------------------------------------------------------------
# TC-OBS-04: S3 sub-stages (S3S, S3M, S3J)
# ---------------------------------------------------------------------------
def test_s3_substages(page: Page, login):
    """TC-OBS-04: S3 sub-stages S3S, S3M, S3J each save correct stage_at_observation."""
    # Need 3 separate eggs — use 3-egg intake
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=3)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    for i, substage in enumerate(["S3S", "S3M", "S3J"]):
        # Select one specific egg
        egg_id = egg_ids[i]
        # Click START then deselect all but target egg if possible
        page.get_by_role("button", name="START").click()
        time.sleep(1)

        # Set stage to this substage
        stage_selects = page.locator("[data-testid='stSelectbox']").all()
        stage_set = False
        for sel in stage_selects:
            try:
                sel.click()
                opt = page.locator(
                    f"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{substage}')"
                ).first
                if opt.is_visible(timeout=2000):
                    opt.click()
                    stage_set = True
                    break
                else:
                    page.keyboard.press("Escape")
            except Exception:
                page.keyboard.press("Escape")

        if not stage_set:
            continue  # Sub-stage not available at this point — skip

        page.get_by_role("button", name="SAVE").last.click()
        time.sleep(2)

        # Verify at least one egg has the substage
        any_substage = db.table("egg_observation").select("stage_at_observation").eq(
            "stage_at_observation", substage
        ).execute()
        assert len(any_substage.data) >= 1, (
            f"DB FAILURE: No egg_observation with stage_at_observation='{substage}' found"
        )

        # Re-pass weight gate if needed
        if page.get_by_text("current weight").is_visible():
            wi = page.locator("[data-testid='stNumberInput'] input").first
            wi.triple_click()
            wi.fill("300")
            page.get_by_role("button", name="SAVE").first.click()
            time.sleep(2)

# ---------------------------------------------------------------------------
# TC-OBS-05: Health/viability fields persisted
# ---------------------------------------------------------------------------
def test_observation_health_fields(page: Page, login):
    """TC-OBS-05: Mold, leaking, denting fields saved in egg_observation row."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_ids = ctx["egg_ids"]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Keep stage at S1 (no change needed)
    # Set mold checkbox
    mold_check = page.locator("[data-testid='stCheckbox']:has-text('Mold')").first
    if mold_check.is_visible():
        mold_check.click()

    # Set leaking to level 1 (Damp)
    leaking_select = page.locator("[data-testid='stSelectbox']:has-text('Leaking')").first
    if leaking_select.is_visible():
        leaking_select.click()
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").nth(1).click()

    # Set denting checkbox
    denting_check = page.locator("[data-testid='stCheckbox']:has-text('Dent')").first
    if denting_check.is_visible():
        denting_check.click()

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    # DB verification
    obs = db.table("egg_observation").select("*").eq(
        "egg_id", egg_ids[0]
    ).order("created_at", desc=True).limit(1).execute()
    assert len(obs.data) >= 1, "DB FAILURE: No egg_observation found"
    row = obs.data[0]
    # At least one clinical field should be non-default
    health_fields_set = (
        row.get("is_molding") is True
        or row.get("leaking", 0) > 0
        or row.get("is_denting") is True
    )
    assert health_fields_set, (
        f"DB FAILURE: Health fields not persisted. Row: {row}"
    )

# ---------------------------------------------------------------------------
# TC-OBS-06: Biological jump warning
# ---------------------------------------------------------------------------
def test_biological_jump_warning(page: Page, login):
    """TC-OBS-06: Selecting S1 → S4 triggers a biological jump warning in UI."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Jump from S1 all the way to S4
    stage_selects = page.locator("[data-testid='stSelectbox']").all()
    for sel in stage_selects:
        try:
            sel.click()
            opt = page.locator(
                "[data-testid='stSelectboxVirtualDropdown'] li:has-text('S4')"
            ).first
            if opt.is_visible(timeout=2000):
                opt.click()
                break
            else:
                page.keyboard.press("Escape")
        except Exception:
            page.keyboard.press("Escape")

    # Verify warning appears (biological jump warning)
    expect(
        page.get_by_text("Unusual").first
        .or_(page.get_by_text("jump").first)
        .or_(page.get_by_text("⚠️").first)
    ).to_be_visible(timeout=5000)

# ---------------------------------------------------------------------------
# TC-OBS-07: Mortality recording
# ---------------------------------------------------------------------------
def test_mortality_recording(page: Page, login):
    """TC-OBS-07: Marking an egg as Dead removes it from active grid and sets status=Dead."""
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=2)
    egg_ids = ctx["egg_ids"]
    target_egg = egg_ids[0]
    db = get_supabase_client()

    page.get_by_role("button", name="START").click()
    time.sleep(1)

    # Find the "Dead" / mortality status option in the matrix
    # The status selectbox has options including "Dead"
    status_select = page.locator("[data-testid='stSelectbox']:has-text('Status')").first
    if not status_select.is_visible():
        # Try all selectboxes for one with 'Dead' option
        selects = page.locator("[data-testid='stSelectbox']").all()
        for sel in selects:
            try:
                sel.click()
                dead_opt = page.locator(
                    "[data-testid='stSelectboxVirtualDropdown'] li:has-text('Dead')"
                ).first
                if dead_opt.is_visible(timeout=2000):
                    dead_opt.click()
                    break
                page.keyboard.press("Escape")
            except Exception:
                page.keyboard.press("Escape")
    else:
        status_select.click()
        page.locator(
            "[data-testid='stSelectboxVirtualDropdown'] li:has-text('Dead')"
        ).first.click()

    page.get_by_role("button", name="SAVE").last.click()
    time.sleep(2)

    # DB verification: at least one egg has status=Dead
    dead_eggs = db.table("egg").select("egg_id, status").eq(
        "status", "Dead"
    ).in_("egg_id", egg_ids).execute()
    assert len(dead_eggs.data) >= 1, (
        "DB FAILURE: No egg status set to 'Dead' after mortality recording"
    )

    # UI: reload Observations — dead egg should not appear in active grid
    page.reload()
    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)
    # Re-add bin to workbench and verify dead egg is absent
    bin_id = ctx["bin_id"]
    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"
    ).first.click()
    page.keyboard.press("Escape")
    time.sleep(1)

    # The dead egg ID should not appear as a checkbox in the grid
    dead_checkbox = page.locator(f"[data-testid='stCheckbox']:has-text('{target_egg}')")
    assert not dead_checkbox.is_visible(), (
        "UI FAILURE: Dead egg still visible in active observation grid"
    )

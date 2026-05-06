"""
Phase 5: Mid-Season Scalability Loop

TC-PH5-01: 50x observation loop with single egg — verify DB accumulation and no crashes.
"""
import time
from playwright.sync_api import Page, expect
from e2e_selectors import HEADING_OBSERVATIONS
from utils.db import get_supabase_client


# ---------------------------------------------------------------------------
# Shared helper: create intake + pass weight gate, return (bin_id, [egg_ids])
# (same as test_observation_workflows.py for consistency)
# ---------------------------------------------------------------------------
def _setup_intake_and_unlock_grid(page: Page, login, egg_count: int = 1):
    """Create intake via UI with egg_count eggs, navigate to Observations, pass weight gate."""
    from e2e_selectors import NAV_INTAKE, NAV_OBSERVATIONS

    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    sig = f"PH5-SETUP-{int(time.time())}"
    page.get_by_role("textbox", name="Finder").fill(sig)
    page.get_by_role("textbox", name="WINC Case #").fill(sig)

    species_sel = page.locator("[data-testid='stSelectbox']:has-text('Species')")
    if species_sel.count() > 0:
        species_sel.first.click()
        page.wait_for_timeout(500)
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
        page.wait_for_timeout(300)
    page.wait_for_timeout(1500)

    condition_sel = page.locator("[data-testid='stSelectbox']:has-text('Condition')")
    if condition_sel.count() > 0:
        condition_sel.first.click()
        page.wait_for_timeout(500)
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('Alive')").first.click()
        page.wait_for_timeout(300)

    days_inputs = page.locator("input[aria-label='Days in Care']").all()
    if days_inputs:
        days_inputs[0].fill("3")

    egg_method_opts = page.locator("[data-testid='stSelectbox']:has-text('Egg Collection Method')")
    if egg_method_opts.count() > 0:
        egg_method_opts.first.click()
        page.wait_for_timeout(500)
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()
        page.wait_for_timeout(300)

    circumstances_input = page.get_by_role("textbox", name="Intake Circumstances")
    if circumstances_input.count() > 0:
        circumstances_input.first.fill("Roadside — scalability test")
    else:
        circumstances_inputs = page.locator("textarea").all()
        if circumstances_inputs:
            circumstances_inputs[0].fill("Roadside — scalability test")

    weight_inputs = page.locator("input[aria-label*='Weight']").all()
    if weight_inputs:
        weight_inputs[0].fill("350")

    page.wait_for_timeout(1000)

    new_eggs_input = page.locator("input[aria-label='New Eggs']")
    new_eggs_input.click()
    new_eggs_input.fill(str(egg_count))

    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)

    db = get_supabase_client()
    intake = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
    bin_row = db.table("bin").select("bin_id, bin_code").eq(
        "intake_id", intake.data[0]["intake_id"]
    ).execute()
    bin_data = bin_row.data[0]
    bin_id = bin_data["bin_id"]
    bin_code = bin_data.get("bin_code", str(bin_id))
    eggs = db.table("egg").select("egg_id").eq("bin_id", bin_id).execute()
    egg_ids = [e["egg_id"] for e in eggs.data]

    page.locator(NAV_OBSERVATIONS).first.click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=15000)

    workbench = page.locator("[data-testid='stMultiSelect']").first
    workbench.click()
    page.locator(
        f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_code}')"
    ).first.click()
    page.keyboard.press("Escape")
    time.sleep(1)

    weight_input = page.locator("[data-testid='stNumberInput'] input").first
    weight_input.triple_click()
    weight_input.fill("300")
    page.get_by_role("button", name="SAVE").first.click()
    time.sleep(2)

    return {"bin_id": bin_id, "egg_ids": egg_ids, "sig": sig}


# ---------------------------------------------------------------------------
# TC-PH5-01: 50x observation loop
# ---------------------------------------------------------------------------
def test_50x_observation_loop(page: Page, login):
    """
    TC-PH5-01: Loop observation workflow 50 times for a single egg,
    then perform final DB pincer audit on observation count and stage.
    """
    ctx = _setup_intake_and_unlock_grid(page, login, egg_count=1)
    egg_id = ctx["egg_ids"][0]

    # Loop 50 times: START -> set stage -> SAVE
    for i in range(50):
        # Click START to select the pending egg
        page.get_by_role("button", name="START").click()
        time.sleep(0.5)

        # Set stage to S2 (or alternate stages? use S2 for simplicity)
        stage_select = page.locator("[data-testid='stSelectbox']:has-text('Stage')").first
        if not stage_select.is_visible():
            stage_select = page.locator("[data-testid='stSelectbox']").first
        stage_select.click()
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li:has-text('S2')").first.click()

        # SAVE observation
        page.get_by_role("button", name="SAVE").last.click()
        time.sleep(1)  # allow DB write and UI rerender

    # Final DB pincer audit
    db = get_supabase_client()

    # Verify egg_observation row count for this egg
    obs_res = db.table("egg_observation").select("egg_observation_id", count="exact").eq("egg_id", egg_id).eq("is_deleted", False).execute()
    obs_count = obs_res.count if hasattr(obs_res, 'count') else len(obs_res.data)
    assert obs_count == 50, (
        f"SCALABILITY FAILURE: Expected 50 observations for egg {egg_id}, found {obs_count}"
    )

    # Verify the egg's current_stage is S2 (the last stage we set)
    egg_res = db.table("egg").select("current_stage").eq("egg_id", egg_id).execute()
    assert egg_res.data[0]["current_stage"] == "S2", (
        f"DB FAILURE: Egg {egg_id} final stage not S2, got {egg_res.data[0]['current_stage']}"
    )

    # Additional: verify no crash (assert True to confirm clean exit of loop)
    assert True, "50x observation loop completed without crash"

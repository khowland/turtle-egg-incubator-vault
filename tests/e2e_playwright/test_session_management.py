"""
Session Management

TC-SES-01: SHIFT END terminates session — session_log updated, redirect to login
TC-SES-02: Session continuity within 4-hour window — re-login adopts same session_id
"""
from e2e_selectors import HEADING_DASHBOARD

import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client

# ---------------------------------------------------------------------------
# TC-SES-01: SHIFT END terminates session
# ---------------------------------------------------------------------------
def test_shift_end_terminates_session(page: Page, login, e2e_base_url):
    """TC-SES-01: Clicking SHIFT END marks session inactive and returns to login."""
    login()

    # Capture current session_id from DB before ending shift
    db = get_supabase_client()
    sessions_before = db.table("session_log").select(
        "session_id, is_active"
    ).eq("is_active", True).order("created_at", desc=True).limit(1).execute()

    if not sessions_before.data:
        # No session_log table or no active session — skip gracefully
        import pytest
        pytest.skip("No active session in session_log — skipping SHIFT END test")

    session_id = sessions_before.data[0]["session_id"]

    # Find and click SHIFT END button in sidebar
    shift_end_btn = page.get_by_role("button", name="SHIFT END").first
    if not shift_end_btn.is_visible():
        shift_end_btn = page.locator("button:has-text('END')").first
    expect(shift_end_btn).to_be_visible(timeout=10000)

    # May require confirmation toggle
    confirm_toggle = page.locator("[data-testid='stToggle']").first
    if confirm_toggle.is_visible():
        confirm_toggle.click()
        time.sleep(0.5)

    shift_end_btn.click()
    time.sleep(2)

    # Should redirect to login (START button visible)
    expect(page.get_by_role("button", name="START", exact=True)).to_be_visible(timeout=15000)

    # DB: session should be marked inactive
    session_after = db.table("session_log").select(
        "is_active"
    ).eq("session_id", session_id).execute()
    if session_after.data:
        assert session_after.data[0]["is_active"] is False, (
            "DB FAILURE: session_log.is_active still True after SHIFT END"
        )

# ---------------------------------------------------------------------------
# TC-SES-02: Session continuity within 4-hour window
# ---------------------------------------------------------------------------
def test_session_continuity_within_window(page: Page, login, e2e_base_url):
    """TC-SES-02: Re-login within 4 hours adopts the same session_id."""
    login()

    # Capture current session_id
    db = get_supabase_client()
    first_session = db.table("session_log").select(
        "session_id"
    ).order("created_at", desc=True).limit(1).execute()

    if not first_session.data:
        import pytest
        pytest.skip("No session_log data — skipping continuity test")

    session_id_1 = first_session.data[0]["session_id"]

    # Navigate away (simulate new page load / re-login)
    page.goto(e2e_base_url, wait_until="domcontentloaded")
    expect(page.get_by_role("button", name="START", exact=True)).to_be_visible(timeout=15000)
    page.get_by_role("button", name="START", exact=True).click()
    expect(page.get_by_role("heading", name=HEADING_DASHBOARD)).to_be_visible(timeout=20000)

    # The latest session should be the same ID (adoption within 4-hr window)
    second_session = db.table("session_log").select(
        "session_id"
    ).order("created_at", desc=True).limit(1).execute()

    if second_session.data:
        session_id_2 = second_session.data[0]["session_id"]
        assert session_id_1 == session_id_2, (
            f"DB FAILURE: Re-login created new session_id (expected adoption). "
            f"Before: {session_id_1}, After: {session_id_2}"
        )

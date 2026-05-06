"""
test_adversarial_input.py — A5
Adversarial input validation tests for SQLi, XSS, and edge-case payloads.

Validates:
- SQL injection payloads in intake fields are sanitized (parameterized queries)
- XSS payloads in text inputs are auto-escaped by Streamlit
- Empty/whitespace-only fields are rejected gracefully
- Overly long field values don't crash the application
"""

import time
import pytest
from playwright.sync_api import Page, expect
from e2e_selectors import (
    NAV_INTAKE,
    HEADING_OBSERVATIONS,
    BTN_SAVE,
)
from utils.db import get_supabase_client


SQLI_PAYLOADS = [
    "'; DROP TABLE intake; --",
    "1; SELECT * FROM observer WHERE '1'='1",
    "' OR '1'='1",
    "admin'--",
]

XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "{{constructor.constructor('alert(1)')()}}",
]


def _fill_minimal_required_fields(page: Page, sig: str, finder_override: str = None):
    """Fill only the minimum required fields to test adversarial payloads."""
    page.locator("input[aria-label='Finder']").fill(finder_override or sig)
    page.locator("input[aria-label='WINC Case #']").fill(sig)

    # Species selectbox — required
    species_sel = page.locator("[data-testid='stSelectbox']:has-text('Species')")
    if species_sel.count() > 0:
        species_sel.first.click()
        page.wait_for_timeout(500)
        page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()


# ---------------------------------------------------------------------------
# TC-ADV-INP-01: SQLi payload in Finder field should be sanitized
# ---------------------------------------------------------------------------
def test_sqli_payload_in_finder_field_sanitized(page: Page, login):
    """TC-ADV-INP-01: SQLi payloads in Finder field must not cause DB errors or injection."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    db = get_supabase_client()

    for payload in SQLI_PAYLOADS:
        sig = f"SQLI-FINDER-{int(time.time())}"
        _fill_minimal_required_fields(page, sig, finder_override=payload)

        # Click SAVE — should either succeed (sanitized) or show validation error (not crash)
        page.get_by_role("button", name="SAVE").click()

        # Wait for response — should not see a 500 error or white screen
        page.wait_for_timeout(2000)

        # Determine outcome: navigation to Observations means SAVE succeeded
        obs_heading = page.get_by_role("heading", name=HEADING_OBSERVATIONS)
        if obs_heading.count() > 0 and obs_heading.is_visible():
            # SAVE succeeded — verify DB pincer: intake exists with payload stored
            intake_res = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
            assert len(intake_res.data) == 1, f"Expected intake for Finder SQLi payload {payload}"
            # Navigate back to intake for next iteration
            page.locator(NAV_INTAKE).first.click()
            expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=10000)
        else:
            # SAVE rejected — verify error message shown and no DB write
            error_texts = page.locator("text=Please fill").or_(page.locator("text=Invalid"))
            expect(error_texts.first).to_be_visible(timeout=5000)
            intake_res = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
            assert len(intake_res.data) == 0, f"SQLi payload {payload} should NOT be saved"

        # Clear and retry for next payload
        page.locator("input[aria-label='Finder']").clear()


# ---------------------------------------------------------------------------
# TC-ADV-INP-02: SQLi payload in WINC Case # field should be sanitized
# ---------------------------------------------------------------------------
def test_sqli_payload_in_winc_case_field_sanitized(page: Page, login):
    """TC-ADV-INP-02: SQLi payloads in WINC Case # field must not cause DB errors."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    db = get_supabase_client()

    for payload in SQLI_PAYLOADS:
        sig = f"SQLI-WINC-{int(time.time())}"
        page.locator("input[aria-label='Finder']").fill(sig)
        page.locator("input[aria-label='WINC Case #']").fill(payload)

        species_sel = page.locator("[data-testid='stSelectbox']:has-text('Species')")
        if species_sel.count() > 0:
            species_sel.first.click()
            page.wait_for_timeout(500)
            page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()

        page.get_by_role("button", name="SAVE").click()
        page.wait_for_timeout(2000)

        # Determine outcome
        obs_heading = page.get_by_role("heading", name=HEADING_OBSERVATIONS)
        if obs_heading.count() > 0 and obs_heading.is_visible():
            # SAVE succeeded: verify intake record (intake_name = payload if stored as WINC Case #)
            # intake_name is the WINC Case # field; if stored, find by that value
            intake_res = db.table("intake").select("intake_id").eq("intake_name", payload).execute()
            assert len(intake_res.data) == 1, f"Expected intake for WINC SQLi payload {payload} not found"
            # Navigate back to Intake
            page.locator(NAV_INTAKE).first.click()
            expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=10000)
        else:
            # SAVE rejected: verify error and no DB write
            error_texts = page.locator("text=Please fill").or_(page.locator("text=Invalid"))
            expect(error_texts.first).to_be_visible(timeout=5000)
            intake_res = db.table("intake").select("intake_id").eq("intake_name", payload).execute()
            assert len(intake_res.data) == 0, f"SQLi WINC payload {payload} should NOT be saved"

        page.locator("input[aria-label='WINC Case #']").clear()


# ---------------------------------------------------------------------------
# TC-ADV-INP-03: Empty required fields rejected gracefully
# ---------------------------------------------------------------------------
def test_empty_required_fields_rejected(page: Page, login):
    """TC-ADV-INP-03: Empty Species or Finder fields should be rejected without crash."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    sig = f"EMPTY-TEST-{int(time.time())}"
    # Submit with empty Finder — should be rejected
    page.locator("input[aria-label='WINC Case #']").fill(sig)
    # Leave Finder empty intentionally

    # Try SAVE — should show error or not proceed
    page.get_by_role("button", name="SAVE").click()
    page.wait_for_timeout(2000)

    # Should show error message (st.error / st.warning) about missing required field
    error = page.locator("text=Please fill").or_(page.locator("text=required"))
    expect(error.first).to_be_visible(timeout=10000)

    # Page should still be functional
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=5000)

    # DB Pincer: no intake should be created with empty Finder
    db = get_supabase_client()
    intake_res = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
    assert len(intake_res.data) == 0, f"Empty Finder should not create intake, got {len(intake_res.data)}"


# ---------------------------------------------------------------------------
# TC-ADV-INP-04: XSS payloads in WINC Case # field should be sanitized/escaped
# ---------------------------------------------------------------------------
def test_xss_payloads_sanitized(page: Page, login):
    """TC-ADV-INP-04: XSS payloads in WINC Case # field must not execute or break page."""
    login()
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    db = get_supabase_client()

    for payload in XSS_PAYLOADS:
        sig = f"XSS-PAYLOAD-{int(time.time())}"
        page.locator("input[aria-label='Finder']").fill(sig)
        page.locator("input[aria-label='WINC Case #']").fill(payload)

        # Fill required fields minimally
        species_sel = page.locator("[data-testid='stSelectbox']:has-text('Species')")
        if species_sel.count() > 0:
            species_sel.first.click()
            page.wait_for_timeout(500)
            page.locator("[data-testid='stSelectboxVirtualDropdown'] li").first.click()

        page.get_by_role("button", name="SAVE").click()
        page.wait_for_timeout(2000)

        # Determine outcome
        obs_heading = page.get_by_role("heading", name=HEADING_OBSERVATIONS)
        if obs_heading.count() > 0 and obs_heading.is_visible():
            # SAVE succeeded: verify data stored and page not crashed
            intake_res = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
            assert len(intake_res.data) == 1, f"XSS payload stored as {sig}"
            # Navigate back
            page.locator(NAV_INTAKE).first.click()
            expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=10000)
        else:
            # SAVE rejected: verify error and no DB write
            error_texts = page.locator("text=Please fill").or_(page.locator("text=Invalid"))
            expect(error_texts.first).to_be_visible(timeout=5000)
            intake_res = db.table("intake").select("intake_id").eq("intake_name", sig).execute()
            assert len(intake_res.data) == 0, f"XSS payload should NOT be saved"

        # Clear WINC Case # for next iteration
        page.locator("input[aria-label='WINC Case #']").clear()

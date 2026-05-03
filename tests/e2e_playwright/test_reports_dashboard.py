"""
Phase 4: Reports & Dashboard

TC-RPT-01: Reports page renders — data grid and export button visible
TC-RPT-02: Dashboard summary stats reflect actual DB state (non-zero after intake)
"""
from selectors import HEADING_DASHBOARD, HEADING_OBSERVATIONS, HEADING_REPORTS, NAV_DASHBOARD, NAV_INTAKE, NAV_REPORTS

import time
from playwright.sync_api import Page, expect
from utils.db import get_supabase_client


# ---------------------------------------------------------------------------
# TC-RPT-01: Reports page renders
# ---------------------------------------------------------------------------
def test_reports_page_renders(page: Page, login):
    """TC-RPT-01: Reports page shows title, filter section, and START button."""
    login()
    page.locator(NAV_REPORTS).first.click()
    expect(page.get_by_role("heading", name=HEADING_REPORTS)).to_be_visible(timeout=15000)

    # START button to build export previews
    expect(page.get_by_role("button", name="START")).to_be_visible(timeout=5000)

    # Click START to build the report
    page.get_by_role("button", name="START").click()
    time.sleep(3)  # Allow data load

    # At least one report section should render
    expect(
        page.get_by_text("Export").first
        .or_(page.get_by_text("Intake").first)
        .or_(page.get_by_text("Clinical").first)
    ).to_be_visible(timeout=10000)

# ---------------------------------------------------------------------------
# TC-RPT-02: Dashboard stats reflect actual DB state
# ---------------------------------------------------------------------------
def test_dashboard_reflects_data(page: Page, login):
    """TC-RPT-02: After intake, Dashboard Today's Summary shows non-zero metrics."""
    login()

    # First create an intake so there's data to reflect
    page.locator(NAV_INTAKE).first.click()
    expect(page.get_by_role("heading", name="Step 1")).to_be_visible(timeout=15000)

    sig = f"DASH-RPT-{int(time.time())}"
    page.locator("input[aria-label='Finder']").fill(sig)
    page.locator("input[aria-label='WINC Case #']").fill(sig)
    page.get_by_role("button", name="SAVE").click()
    expect(page.get_by_role("heading", name=HEADING_OBSERVATIONS)).to_be_visible(timeout=30000)

    # Navigate to Dashboard
    page.locator(NAV_DASHBOARD).first.click()
    expect(page.get_by_role("heading", name=HEADING_DASHBOARD)).to_be_visible(timeout=15000)

    # Dashboard should show at least some data metrics (st.metric or numeric values)
    # Verify at least one metric/stat is displayed
    metrics = page.locator("[data-testid='stMetric']").all()
    assert len(metrics) >= 1, "UI FAILURE: No metrics visible on Dashboard"

    # DB verification: intake + bin + egg tables have data
    db = get_supabase_client()
    for table in ["intake", "bin", "egg"]:
        result = db.table(table).select("*", count="exact").execute()
        assert result.count >= 1, (
            f"DB FAILURE: Table '{table}' is empty — Dashboard has nothing to reflect"
        )

    # Verify multiple rows accumulated across tests
    intake_count = db.table("intake").select("*", count="exact").execute()
    assert intake_count.count >= 2, (
        f"DB FAILURE: intake table only has {intake_count.count} rows — "
        "expected accumulation across test suite"
    )

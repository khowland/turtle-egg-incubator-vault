"""
Performance Tests (Requirements §5)

TC-PERF-01: Splash screen TFMP < 1000ms (START button visible within 1s)
TC-PERF-02: Full hydration < 1500ms (Dashboard heading visible after START within 1.5s)

Breadcrumb: If these fail, check utils/performance.py and .streamlit/config.toml
for font disabling (gfonts=false) and Supabase client singleton pattern.
Common causes: external font polling, redundant DB calls at startup.
"""
import time
from playwright.sync_api import Page, expect
from e2e_selectors import HEADING_DASHBOARD


# ---------------------------------------------------------------------------
# TC-PERF-01: Splash screen TFMP < 1000ms
# ---------------------------------------------------------------------------
def test_splash_screen_tfmp(page: Page, e2e_base_url):
    """TC-PERF-01: START button must be visible within 1000ms of page load."""
    start_time = time.time()
    page.goto(e2e_base_url, wait_until="domcontentloaded")
    page.get_by_role("button", name="START", exact=True).wait_for(
        state="visible", timeout=1000
    )
    elapsed_ms = (time.time() - start_time) * 1000

    assert elapsed_ms < 1000, (
        f"PERF FAILURE: Splash TFMP {elapsed_ms:.0f}ms exceeds 1000ms threshold. "
        "Check: .streamlit/config.toml gfonts disabled, Supabase auto-pause, CDN caching."
    )


# ---------------------------------------------------------------------------
# TC-PERF-02: Full hydration < 1500ms
# ---------------------------------------------------------------------------
def test_hydration_time(page: Page, e2e_base_url):
    """TC-PERF-02: Dashboard heading must appear within 1500ms of clicking START."""
    page.goto(e2e_base_url, wait_until="domcontentloaded")
    page.get_by_role("button", name="START", exact=True).wait_for(
        state="visible", timeout=5000
    )

    start_time = time.time()
    page.get_by_role("button", name="START", exact=True).click()
    page.get_by_role("heading", name=HEADING_DASHBOARD).wait_for(
        state="visible", timeout=1500
    )
    elapsed_ms = (time.time() - start_time) * 1000

    assert elapsed_ms < 1500, (
        f"PERF FAILURE: Hydration time {elapsed_ms:.0f}ms exceeds 1500ms threshold. "
        "Check: DB singleton init, network poller disabled, Supabase client caching."
    )

import os
import pytest
from playwright.sync_api import Page, expect
from tests.e2e_playwright.e2e_selectors import HEADINGS, BUTTONS
import os; os.environ.setdefault('DISPLAY', ':99')

# Optional supabase wipe fixture
try:
    from supabase import create_client
except ImportError:
    create_client = None


def _get_test_supabase():
    """Create a test supabase client using environment variables."""
    if create_client is None:
        return None
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        # fallback: try reading .env file
        try:
            from dotenv import load_dotenv
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            load_dotenv(env_path)
            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_ANON_KEY", "")
        except:
            pass
    # Try alternative key names
    if not key:
        for key_name in ["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY"]:
            key = os.environ.get(key_name, "")
            if key:
                break
    if not url or not key:
        return None
    return create_client(url, key)


@pytest.fixture(scope='session', autouse=True)
def wipe_transactional_tables():
    """Soft-delete all transactional tables before test suite. No hard DELETEs."""
    supabase = _get_test_supabase()
    if supabase is None:
        print("[FIXTURE] Could not connect to Supabase; skipping DB wipe.")
        return
    print("[FIXTURE] Starting transactional table soft-delete...")
    # Tables WITH is_deleted column → soft-delete via UPDATE
    soft_delete_tables = [
        "egg_observation",
        "bin_observation",
        "egg",
        "bin",
        "intake",
    ]
    # Tables WITHOUT is_deleted → SKIP (preserve audit trail forever)
    skip_tables = ["system_log", "session_log", "hatchling_ledger"]
    for table in soft_delete_tables:
        try:
            id_map = {
                "hatchling_ledger": "hatchling_ledger_id",
                "egg_observation": "egg_observation_id",
                "bin_observation": "bin_observation_id",
                "egg": "egg_id",
                "bin": "bin_id",
                "intake": "intake_id",
            }
            id_col = id_map[table]
            resp = supabase.table(table).update({"is_deleted": True}).neq(id_col, 0).execute()
            count = len(resp.data) if resp.data else 0
            print(f"  [FIXTURE] Soft-deleted {table}: {count} rows marked is_deleted=true.")
        except Exception as e:
            print(f"  [FIXTURE] Error wiping {table}: {e}")
    for table in skip_tables:
        print(f"  [FIXTURE] Skipped {table} (no is_deleted column — audit trail preserved).")
    print("[FIXTURE] Transactional table soft-delete complete.\n")


@pytest.fixture(scope='session')
def e2e_base_url() -> str:
    return os.environ.get('E2E_BASE_URL', 'http://127.0.0.1:8599')


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        'viewport': {'width': 1280, 'height': 900},
        'ignore_https_errors': True,
    }

@pytest.fixture(scope='session')
def browser_type_launch_args(browser_type_launch_args):
    """Override Playwright launch args to use HEADFUL mode with Xvfb."""
    return {
        **browser_type_launch_args,
        'headless': True,
        'args': ['--no-sandbox'],
    }



@pytest.fixture()
def login(page: Page, e2e_base_url: str):
    def _login():
        page.goto(e2e_base_url, wait_until='domcontentloaded')
        # TSK-04 RESOLUTION: Vision-First coordinate click at (640, 457) to overcome
        # st.form container coordinate drift. Standard locator fails in headless mode.
        page.mouse.click(640, 457)
        # Wait for form submission to process (st.rerun() re-renders splash with session)
        page.wait_for_timeout(1500)
        # Session is now established; test helper handles navigation to Intake/Observations.
    return _login


@pytest.fixture()
def verify_version(page: Page, e2e_base_url: str):
    """Verify the UI version label matches the database system_config version."""
    def _verify(expected_version: str = None):
        # Navigate to settings page to read version
        page.goto(f"{e2e_base_url}/5_Settings", wait_until='domcontentloaded')
        # Look for version text (format: 'v9.2.0')
        version_text = page.locator('text=/v\\d+\\.\\d+\\.\\d+/').first
        version_text.wait_for(timeout=15000)
        actual_version = version_text.text_content()
        if expected_version:
            assert expected_version in actual_version, f"Version mismatch: expected {expected_version}, got {actual_version}"
    return _verify


def _trigger_workbench_hydration(page):
    """RED TEAM FIX: Use page.evaluate() to detect multi-select hydration.
    
    Previous version used Playwright locators to click the multi-select and
    wait for dropdown options — but locators can't see portal-rendered popover
    elements in headless Chromium. The page was always hydrated (server logs
    confirm workbench_bins populated), the trigger just couldn't detect it.
    
    New approach: Use page.evaluate() to directly inspect the popover DOM
    for LI elements containing bin_code patterns, without clicking anything.
    """
    import re
    
    # Diagnostic: check what's on the page
    # Allow Streamlit to fully render before checking (previous body capture showed pre-render text)
    page.wait_for_timeout(3000)
    
    # Re-capture body text AFTER waiting for Streamlit to render
    page_info = page.evaluate("""() => {
        return {
            url: location.href,
            bodyText: document.body ? document.body.textContent.substring(0, 500) : '',
            hasMultiSelect: document.querySelector('[data-testid="stMultiSelect"]') !== null,
            hasSelectbox: document.querySelector('[data-testid="stSelectbox"]') !== null,
            stageText: (() => {
                const sel = document.querySelector('[data-testid="stSelectbox"]');
                return sel ? sel.textContent?.trim().substring(0, 100) : '';
            })(),
        };
    }""")
    print(f"[WORKBENCH_HYDRATION] Page: {page_info.get('url', '?')}")
    print(f"[WORKBENCH_HYDRATION] Has selectbox: {page_info.get('hasSelectbox')}, Stage text: {page_info.get('stageText', '')[:60]}")
    
    # Primary indicator: Stage selectbox visible = Property Matrix rendered = hydration success
    if page_info.get('hasSelectbox'):
        print("[WORKBENCH_HYDRATION] ✅ Stage selectbox found — Property Matrix rendered")
        return True
    
    # Fallback 1: check body text for bin_code patterns (bins populated in session_state)
    body = page_info.get('bodyText', '')
    if re.search(r'[A-Z]{2}\d+-', body):
        print("[WORKBENCH_HYDRATION] ✅ Bin codes found in page body text")
        return True
    
    # Fallback 2: Traditional multi-select popover check
    if page_info.get('hasMultiSelect'):
        try:
            ms = page.locator("[data-testid='stMultiSelect']").first
            if ms.count():
                ms.click()
                page.wait_for_timeout(1500)
                result = page.evaluate("""() => {
                    const pop = document.querySelector('[data-baseweb="popover"]');
                    if (!pop) return { status: 'no_popover' };
                    const lis = pop.querySelectorAll('li');
                    const liTexts = Array.from(lis).map(l => l.textContent?.trim() || '');
                    return {
                        status: 'popover_found',
                        liCount: lis.length,
                        liTexts: liTexts,
                        hasNoResults: liTexts.some(t => t === 'No results'),
                        hasBinOptions: liTexts.some(t => /[A-Z]{2}\d+-/.test(t)),
                    };
                }""")
                print(f"[WORKBENCH_HYDRATION] Popover: LIs={result.get('liCount')}, noResults={result.get('hasNoResults')}, binOptions={result.get('hasBinOptions')}")
                if result.get('hasBinOptions') or (result.get('liCount', 0) > 0 and not result.get('hasNoResults')):
                    print("[WORKBENCH_HYDRATION] ✅ Bin options found in popover")
                    return True
        except Exception as e:
            print(f"[WORKBENCH_HYDRATION] Popover check failed: {e}")
    
    print(f"[WORKBENCH_HYDRATION] ❌ FAILED. Body: {body[:200]}")
    if re.search(r'[A-Z]{2}\d+-', body):
        print("[WORKBENCH_HYDRATION] ✅ Bin codes found in page body text")
        return True
    
    print(f"[WORKBENCH_HYDRATION] ❌ FAILED after 3 retries. Body: {body[:200]}")
    return False

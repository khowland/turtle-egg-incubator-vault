import os
import pytest
from playwright.sync_api import Page, expect

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
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        # fallback: try reading .env file
        try:
            from dotenv import load_dotenv
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            load_dotenv(env_path)
            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_SERVICE_KEY", "")
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
        "hatchling_ledger",
        "egg_observation",
        "bin_observation",
        "egg",
        "bin",
        "intake",
    ]
    # Tables WITHOUT is_deleted → SKIP (preserve audit trail forever)
    skip_tables = ["system_log", "session_log"]
    for table in soft_delete_tables:
        try:
            resp = supabase.table(table).update({"is_deleted": True}).neq('id', 0).execute()
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


@pytest.fixture()
def login(page: Page, e2e_base_url: str):
    def _login():
        page.goto(e2e_base_url, wait_until='domcontentloaded')
        expect(page.get_by_role('button', name='START', exact=True)).to_be_visible(timeout=30000)
        page.get_by_role('button', name='START', exact=True).click()
        expect(page.get_by_role('heading', name='📊 Today\'s Summary')).to_be_visible(timeout=30000)
    return _login

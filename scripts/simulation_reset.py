import os
import requests
from dotenv import load_dotenv

env_path = r"c:\dev\projects\turtle-db\.env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

def execute_sql(label, sql):
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(api_url, headers=headers, json={"query": sql})
    if resp.status_code in (200, 201):
        print(f"[OK] {label} successful.")
        return resp.json()
    else:
        print(f"[FAIL] {label} failed: {resp.text}")
        return None

def phase_0_reset():
    print("Initializing Phase 0: System State Reset")
    
    # 1. Surgical Truncate (Transactional Ledger)
    # Order: Children first to respect FKs
    sql_wipe = """
    BEGIN;
    TRUNCATE TABLE public.hatchling_ledger RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.egg_observation RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.bin_observation RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.egg RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.bin RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.intake RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.system_log RESTART IDENTITY CASCADE;
    TRUNCATE TABLE public.session_log RESTART IDENTITY CASCADE;
    COMMIT;
    """
    execute_sql("Transactional Wipe", sql_wipe)

    # 2. Identity Seeding (Observers)
    # We truncate observer last and immediately re-seed to maintain identity sovereignity
    sql_identity = """
    BEGIN;
    TRUNCATE TABLE public.observer RESTART IDENTITY CASCADE;
    INSERT INTO public.observer (display_name, is_active)
    VALUES 
    ('Kevin Howland', true),
    ('Clinical Director', true),
    ('Shift Supervisor', true),
    ('Field Researcher', true),
    ('QA Actuator Node', true);
    COMMIT;
    """
    execute_sql("Identity Seeding", sql_identity)

    print("Phase 0 Complete: Clean Slate Established.")

if __name__ == "__main__":
    phase_0_reset()

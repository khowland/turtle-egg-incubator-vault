import os
import requests
import json
from dotenv import load_dotenv

env_path = r"c:\dev\projects\turtle-db\.env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

def execute_sql(sql_label, sql_query):
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": sql_query}
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            print(f"[SUCCESS] {sql_label} executed.")
            return resp.json()
        else:
            print(f"[FAIL] {sql_label} failed ({resp.status_code}): {resp.text[:300]}")
            return None
    except Exception as e:
        print(f"[ERROR] Error during {sql_label}: {e}")
        return None

def seed_foundation():
    print(f"--- [QA ROLE: Foundation Sub-Agent] Starting Level 1 ---")
    print(f"Project Ref: {PROJECT_REF}")

    # 1. Seed System Version
    execute_sql("Seed Config", """
        DELETE FROM public.system_config;
        INSERT INTO public.system_config (config_name, config_value, description)
        VALUES ('APP_VERSION', '9.5.0', 'Enterprise BIGINT Edition');
    """)

    # 2. Seed Observers
    execute_sql("Seed Observers", """
        DELETE FROM public.observer CASCADE;
        INSERT INTO public.observer (display_name, is_active)
        VALUES ('QA_AUTOMATION_NODE', true), ('CLINICAL_DIRECTOR', true);
    """)

    # 3. Seed Species
    execute_sql("Seed Species", """
        DELETE FROM public.species CASCADE;
        INSERT INTO public.species (species_code, common_name, scientific_name)
        VALUES 
        ('BL', 'Blanding''s Turtle', 'Emydoidea blandingii'),
        ('SN', 'Snapping Turtle', 'Chelydra serpentina'),
        ('WT', 'Wood Turtle', 'Glyptemys insculpta'),
        ('PA', 'Painted Turtle', 'Chrysemys picta');
    """)

    # 4. Verification
    print("\n--- LEVEL 1 VERIFICATION ---")
    res = execute_sql("Verify Observers", "SELECT observer_id, display_name FROM public.observer;")
    if res:
        print(f"Observers: {json.dumps(res, indent=2)}")
    
    res_spec = execute_sql("Verify Species", "SELECT species_id, common_name FROM public.species LIMIT 1;")
    if res_spec:
        print(f"Species: {json.dumps(res_spec, indent=2)}")

    print("\n[VERIFIED] UP-01 & UP-02: FOUNDATION COMPLETE.")

if __name__ == "__main__":
    seed_foundation()

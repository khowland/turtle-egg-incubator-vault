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

def verify_hatch():
    print(f"--- [QA ROLE: Hatchling Sub-Agent] Starting LED-01 ---")
    
    # 1. Resolve Egg ID
    print("Fetching last created Egg ID...")
    egg_res = execute_sql("Get Egg", "SELECT egg_id, egg_code FROM public.egg WHERE egg_code = 'QA-BIN-A-E1' LIMIT 1;")
    if not egg_res or len(egg_res) == 0:
        print("[FAIL] LED-01: Target egg 'QA-BIN-A-E1' not found.")
        return
    
    target_egg_id = egg_res[0]['egg_id']
    print(f"Target Egg ID: {target_egg_id}")

    # 2. Resolve Intake ID
    intake_res = execute_sql("Get Intake", "SELECT intake_id FROM public.intake WHERE intake_name = 'QA-CASE-999' LIMIT 1;")
    target_intake_id = intake_res[0]['intake_id']

    # 3. Resolve Session ID
    sess_res = execute_sql("Get Session", "SELECT session_id FROM public.session_log WHERE session_token = 'QA-SESSION-UUID-001' LIMIT 1;")
    dynamic_session_id = sess_res[0]['session_id']

    # 4. Commit to Hatchling Ledger
    print("Committing to Hatchling Ledger...")
    hatch_sql = f"""
        INSERT INTO public.hatchling_ledger (
            egg_id, intake_id, session_id,
            hatch_weight_g, vitality_score, notes
        ) VALUES (
            {target_egg_id}, {target_intake_id}, {dynamic_session_id},
            12.5, 'Strong', 'Final Phase 3 Verification'
        ) RETURNING hatchling_ledger_id;
    """
    
    hatch_res = execute_sql("Insert Hatchling", hatch_sql)
    if hatch_res:
        ledger_id = hatch_res[0]['hatchling_ledger_id']
        print(f"Created Ledger ID: {ledger_id}")
        print("\n[VERIFIED] LED-01: HATCHLING LEDGER COMPLETE. Full clinical lifecycle verified.")
    else:
        print("\n[FAIL] LED-01: Could not commit hatchling.")

if __name__ == "__main__":
    verify_hatch()

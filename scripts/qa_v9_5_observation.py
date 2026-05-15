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

def verify_observation():
    print(f"--- [QA ROLE: Observation Sub-Agent] Starting Level 3 (RETRY 1) ---")
    
    # 1. Resolve Dynamic Session ID (Enterprise Mapping Check)
    print("Resolving BIGINT Session ID for 'QA-SESSION-UUID-001'...")
    sess_res = execute_sql("Get Session", "SELECT session_id FROM public.session_log WHERE session_token = 'QA-SESSION-UUID-001' LIMIT 1;")
    if not sess_res or len(sess_res) == 0:
        print("[FAIL] OBS-01: Could not resolve session_id.")
        return
    
    dynamic_session_id = sess_res[0]['session_id']
    print(f"Dynamic Session ID: {dynamic_session_id}")

    # 2. Resolve Bin ID
    print("Fetching last created Bin ID...")
    bin_res = execute_sql("Get Bin", "SELECT bin_id FROM public.bin WHERE bin_code = 'QA-BIN-A' LIMIT 1;")
    if not bin_res or len(bin_res) == 0:
        print("[FAIL] OBS-01: Target bin 'QA-BIN-A' not found.")
        return
    
    target_bin_id = bin_res[0]['bin_id']
    print(f"Target Bin ID: {target_bin_id}")

    # 3. Insert new Observation (Level 3 Test)
    print("Committing Bin Observation (Mass Check)...")
    obs_sql = f"""
        INSERT INTO public.bin_observation (
            session_id, bin_id, observer_id, observer_name,
            bin_weight_g, incubator_temp_f, env_notes
        ) VALUES (
            {dynamic_session_id}, {target_bin_id}, 1, 'QA_SUB_AGENT',
            455.5, 83.2, 'Phase 3 Verification: Dynamic BIGINT Resolution'
        ) RETURNING bin_observation_id;
    """
    
    obs_res = execute_sql("Insert Observation", obs_sql)
    if obs_res:
        obs_id = obs_res[0]['bin_observation_id']
        print(f"Created Observation ID: {obs_id}")
        print("\n[VERIFIED] OBS-01: BIN OBSERVATION COMPLETE. Dynamic BIGINT resolution operational.")
    else:
        print("\n[FAIL] OBS-01: Could not commit observation.")

if __name__ == "__main__":
    verify_observation()

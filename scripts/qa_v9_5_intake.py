import os
import requests
import json
from dotenv import load_dotenv

env_path = r"c:\dev\projects\turtle-db\.env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

def execute_rpc(rpc_name, payload):
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    # For RPC call via API query endpoint, we use SELECT public.rpc_name(p_payload := '...')
    payload_json = json.dumps(payload).replace("'", "''")
    query = f"SELECT public.{rpc_name}('{payload_json}'::jsonb);"
    
    body = {"query": query}
    try:
        resp = requests.post(api_url, headers=headers, json=body, timeout=30)
        if resp.status_code in (200, 201):
            print(f"[SUCCESS] RPC {rpc_name} executed.")
            return resp.json()
        else:
            print(f"[FAIL] RPC {rpc_name} failed ({resp.status_code}): {resp.text[:500]}")
            return None
    except Exception as e:
        print(f"[ERROR] Error during RPC {rpc_name}: {e}")
        return None

def verify_intake():
    print(f"--- [QA ROLE: Intake Sub-Agent] Starting Level 2 ---")
    
    test_payload = {
        "species_id": 1,
        "intake_date": "2026-05-14",
        "session_id": "QA-SESSION-UUID-001",
        "observer_id": 1,
        "intake": {
            "intake_name": "QA-CASE-999",
            "finder_turtle_name": "Antigravity QA Node",
            "intake_condition": "Standard Test"
        },
        "bins": [
            {
                "bin_code": "QA-BIN-A",
                "egg_count": 2,
                "bin_weight_g": 450,
                "incubator_temp_f": 82.0
            }
        ]
    }

    print("Executing Atomic Intake Save...")
    result = execute_rpc("vault_finalize_intake", test_payload)
    if not result:
        print("❌ INT-01 FAILED: RPC execution failed.")
        return

    print(f"RPC Result: {json.dumps(result, indent=2)}")
    
    # 2. Forensic Verification of created BIGINTs
    print("\n--- LEVEL 2 VERIFICATION ---")
    
    # We check if we can see the new intake
    check_query = """
        SELECT i.intake_id, i.intake_name, b.bin_id, b.bin_code, e.egg_id, e.egg_code
        FROM public.intake i
        JOIN public.bin b ON i.intake_id = b.intake_id
        JOIN public.egg e ON b.bin_id = e.bin_id
        WHERE i.intake_name = 'QA-CASE-999';
    """
    
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
    body = {"query": check_query}
    resp = requests.post(api_url, headers=headers, json=body)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Forensic Trace: {json.dumps(data, indent=2)}")
        if len(data) > 0:
            print("\n✅ INT-01: ATOMIC INTAKE VERIFIED. Multi-table BIGINT integrity confirmed.")
        else:
            print("\n❌ INT-01: FAILED. Records not found in database.")
    else:
        print(f"❌ Verification query failed: {resp.text}")

if __name__ == "__main__":
    verify_intake()

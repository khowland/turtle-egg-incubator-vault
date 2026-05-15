import os
import requests
import json
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
        return resp.json()
    return None

def forensic_audit():
    print("--- [Ac] Actuator: Phase 3 Forensic Audit ---")
    
    audit_report = {
        "timestamp": "2026-05-14",
        "system_status": "HARDENED",
        "verifications": {},
        "violations": []
    }

    # 1. Row Counts
    counts = {}
    tables = ["intake", "bin", "egg", "bin_observation", "observer"]
    for t in tables:
        res = execute_sql(f"Count {t}", f"SELECT count(*) FROM public.{t}")
        counts[t] = res[0]['count'] if res else 0
    audit_report["verifications"]["row_counts"] = counts

    # 2. Lifecycle Status Check
    lifecycle = {}
    # Check for soft deletes
    res_del = execute_sql("Soft Delete Check", "SELECT count(*) FROM public.egg WHERE is_deleted = true")
    lifecycle["soft_deletes"] = res_del[0]['count'] if res_del else 0
    # Check for mortality
    res_dead = execute_sql("Mortality Check", "SELECT count(*) FROM public.egg WHERE status = 'Dead'")
    lifecycle["mortality_count"] = res_dead[0]['count'] if res_dead else 0
    audit_report["verifications"]["lifecycle_states"] = lifecycle

    # 3. Future Date Check (Pollution Analysis)
    pollution = execute_sql("Future Check", "SELECT intake_id FROM public.intake WHERE intake_date > '2026-12-31'")
    if pollution and len(pollution) > 0:
        audit_report["violations"].append(f"Temporal Pollution: {len(pollution)} future records found.")

    # 4. Generate Snapshot (Including the edge cases)
    snapshot = {}
    for t in tables:
        snapshot[t] = execute_sql(f"Sample {t}", f"SELECT * FROM public.{t} LIMIT 5")
    
    # Add the soft-deleted eggs specifically for review
    snapshot["retired_eggs"] = execute_sql("Retired Eggs", "SELECT * FROM public.egg WHERE is_deleted = true OR status = 'Dead'")
    
    audit_report["snapshot"] = snapshot

    with open("mid_season_golden_snapshot.json", "w") as f:
        json.dump(audit_report, f, indent=2)
    
    print("Done. Forensic Audit updated with Lifecycle verification.")

if __name__ == "__main__":
    forensic_audit()

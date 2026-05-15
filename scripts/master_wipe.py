import os
import requests
from dotenv import load_dotenv

env_path = r"c:\dev\projects\turtle-db\.env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

def master_wipe():
    print(f"--- [QA ROLE: Master Janitor] Obliterating Clinical Ledger ---")
    
    # Correct order for foreign key constraints
    tables = [
        "hatchling_ledger",
        "egg_observation",
        "bin_observation",
        "egg",
        "bin",
        "intake",
        "system_log",
        "session_log",
        "observer",
        "species"
    ]
    
    sql = "BEGIN;\n"
    for table in tables:
        sql += f"TRUNCATE public.{table} RESTART IDENTITY CASCADE;\n"
    sql += "COMMIT;"

    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
    
    resp = requests.post(api_url, headers=headers, json={"query": sql})
    if resp.status_code in (200, 201):
        print("[SUCCESS] Database is now a clean slate.")
    else:
        print(f"[FAIL] Wipe failed: {resp.text}")

if __name__ == "__main__":
    master_wipe()

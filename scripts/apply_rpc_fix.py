import os
import requests
from dotenv import load_dotenv

env_path = r"c:\dev\projects\turtle-db\.env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

RPC_FILE = r"c:\dev\projects\turtle-db\supabase_db\migrations\v9_5_1_UPDATE_RPCS_FOR_BIGINT.sql"

def apply_fix():
    with open(RPC_FILE, 'r') as f:
        sql = f.read()

    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": sql}
    
    print(f"Applying RPC fix to {PROJECT_REF}...")
    resp = requests.post(api_url, headers=headers, json=payload)
    if resp.status_code in (200, 201):
        print("✅ RPC Fix applied successfully.")
    else:
        print(f"❌ Failed to apply fix: {resp.text}")

if __name__ == "__main__":
    apply_fix()

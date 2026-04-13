"""
=============================================================================
Script:     scripts/heartbeat_ping.py
Project:    Incubator Vault v7.3.0
Purpose:    Prevent Supabase auto-pausing by performing a daily clinical ping.
Usage:      Deploy this to a Google Cloud Function or run as a daily cron.
=============================================================================
"""
import os
import datetime
from supabase import create_client
from dotenv import load_dotenv

def trigger_heartbeat():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ Heartbeat Failed: Missing credentials.")
        return

    try:
        sb = create_client(url, key)
        # Perform a lightweight read on the species table
        res = sb.table('species').select("count", count='exact').limit(1).execute()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ [{timestamp}] Heartbeat Successful. Species Count: {res.count}")
        
        # Optional: Record the heartbeat in the systemlog
        sb.table('systemlog').insert({
            "event_type": "HEARTBEAT",
            "event_message": "Automated production stay-alive ping successful."
        }).execute()
        
    except Exception as e:
        print(f"❌ [{datetime.datetime.now()}] Heartbeat ERROR: {e}")

if __name__ == "__main__":
    trigger_heartbeat()

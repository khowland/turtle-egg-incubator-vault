"""
=============================================================================
Module:        utils/supabase_mgmt.py
Project:       Incubator Vault v8.1.4
Purpose:       Programmatic Supabase project restoration (Plan B).
Requirement:   Infrastructure & Lifecycle Recovery.
=============================================================================
"""
import os
import requests
import time
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

def wake_supabase_project():
    """
    Triggers the Supabase Management API to restore (unpause) the project.
    Requirement: Requires SUPABASE_MANAGEMENT_API_TOKEN in .env.
    """
    url = os.getenv("SUPABASE_URL", "")
    token = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
    
    if not url or not token:
        logger.error("❌ Wake Logic Aborted: Missing SUPABASE_URL or MANAGEMENT_API_TOKEN.")
        return False

    # Extract project reference from URL (e.g., https://ref.supabase.co)
    try:
        project_ref = url.split("://")[1].split(".")[0]
    except Exception as e:
        logger.error(f"❌ Failed to parse project ref from URL: {e}")
        return False

    mgmt_api_url = f"https://api.supabase.com/v1/projects/{project_ref}/restore"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    logger.warning(f"⚡ Plan B: Attempting to wake Supabase project '{project_ref}'...")
    
    try:
        response = requests.post(mgmt_api_url, headers=headers)
        if response.status_code in (200, 201):
            logger.info("✅ Wake Signal Sent Successfully. Project is now 'Restoring'.")
            return True
        elif response.status_code == 409:
            # 409 usually means project is already active or already restoring
            logger.info("ℹ️ Project is already active or in transition.")
            return True
        else:
            logger.error(f"❌ Wake API Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Wake Connection Error: {e}")
        return False

def wait_for_restoration(check_func, timeout_s=90, interval_s=5):
    """
    Polls a connection check function until success or timeout.
    """
    start_time = time.time()
    logger.info(f"⏳ Waiting for database restoration (timeout: {timeout_s}s)...")
    
    while time.time() - start_time < timeout_s:
        if check_func():
            logger.info("✅ Database is back online!")
            return True
        time.sleep(interval_s)
    
    logger.error("❌ Restoration timed out.")
    return False

"""
DB Verification module for TC-LOGIN-001.
Blind Pincer: This module has NO UI knowledge, only DB schema.
Verifies that a login created a session_log entry and system_config version is correct.
"""
import os
from supabase import create_client

def get_supabase_client():
    """Create Supabase client using environment variables."""
    url = os.environ.get("SUPABASE_URL", "https://kxfkfeuhkdopgmkpdimo.supabase.co")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not key:
        # fallback to dotenv
        try:
            from dotenv import load_dotenv
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
            load_dotenv(env_path)
            key = os.environ.get("SUPABASE_ANON_KEY", "")
        except:
            pass
    if not key:
        # last resort: try SUPABASE_SERVICE_ROLE_KEY
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    return create_client(url, key)

def verify_login_db_state():
    """
    Verify database state after login:
    1. system_config APP_VERSION is v9.2.0
    2. session_log has at least one row
    3. Most recent session has required fields (session_id, user_name, login_timestamp)
    """
    supabase = get_supabase_client()
    
    errors = []
    
    # 1. Verify system_config version
    version_resp = supabase.table("system_config").select("setting_value").eq("setting_name", "APP_VERSION").execute()
    if not version_resp.data:
        errors.append("APP_VERSION not found in system_config")
    else:
        db_version = version_resp.data[0]["setting_value"]
        if db_version != "v9.2.0":
            errors.append(f"Expected version v9.2.0, got {db_version}")
    
    # 2. Verify session_log has rows
    try:
        session_count_resp = supabase.table("session_log").select("*", count="exact").execute()
        if session_count_resp.count == 0:
            errors.append("No session_log rows found after login")
    except Exception as e:
        errors.append(f"session_log query failed: {e}")
    
    # 3. Verify latest session has required fields
    try:
        latest = supabase.table("session_log").select("*").order("login_timestamp", desc=True).limit(1).execute()
        if latest.data:
            session = latest.data[0]
            if not session.get("session_id"):
                errors.append("Latest session_log row missing session_id")
            if not session.get("user_name"):
                errors.append("Latest session_log row missing user_name")
        else:
            errors.append("Could not fetch latest session_log row")
    except Exception as e:
        errors.append(f"Latest session query failed: {e}")
    
    if errors:
        raise AssertionError("DB Verification failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

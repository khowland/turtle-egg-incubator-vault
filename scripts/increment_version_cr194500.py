#!/usr/bin/env python3
"""
Increment MAJOR version in system_config table for CR-20260430-194500.
Reads current APP_VERSION, increments major component, resets minor/patch to 0.
Example: v8.1.27 -> v9.0.0
"""
import sys
import os
import re

# Ensure workdir is on path for utils access
sys.path.insert(0, '/a0/usr/workdir')

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment.")
        sys.exit(1)
    
    supabase = create_client(url, key)
    
    # Query current version
    response = supabase.table("system_config").select("*").eq("config_key", "APP_VERSION").execute()
    
    if not response.data:
        print("ERROR: No APP_VERSION row found in system_config table.")
        sys.exit(1)
    
    row = response.data[0]
    old_version = row["config_value"]
    print(f"Current version (from DB): {old_version}")
    
    # Parse version: handle optional 'v' prefix, e.g. "v8.1.27" or "8.1.27"
    match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)$', old_version.strip())
    if not match:
        print(f"ERROR: Could not parse version string: '{old_version}'")
        sys.exit(1)
    
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    new_major = major + 1
    new_version = f"v{new_major}.0.0"
    print(f"New version (computed):  {new_version}")
    
    # Update the row
    update_resp = supabase.table("system_config").update({"config_value": new_version}).eq("config_key", "APP_VERSION").execute()
    
    if update_resp.data:
        print(f"Update response: {update_resp.data[0]}")
    else:
        print("ERROR: Update returned empty data.")
        sys.exit(1)
    
    # Re-read to verify
    verify_resp = supabase.table("system_config").select("*").eq("config_key", "APP_VERSION").execute()
    if verify_resp.data:
        verified_version = verify_resp.data[0]["config_value"]
        print(f"Verified version (re-read): {verified_version}")
        if verified_version == new_version:
            print("SUCCESS: Version update confirmed.")
            print(f"OLD_VERSION={old_version}")
            print(f"NEW_VERSION={new_version}")
        else:
            print(f"MISMATCH: Expected {new_version}, got {verified_version}")
            sys.exit(1)
    else:
        print("ERROR: Verification query returned no data.")
        sys.exit(1)

if __name__ == "__main__":
    main()

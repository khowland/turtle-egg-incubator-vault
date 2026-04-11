import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Credentials missing.")
    exit(1)

supabase = create_client(url, key)

try:
    # Get all tables in the public schema
    response = supabase.rpc("get_tables", {}).execute()
    # Note: If get_tables RPC doesn't exist, we can try a simple query
    print("✅ Connection Successful.")
    
    # Try listing tables via SQL if RPC fails or just query a known table
    res = supabase.table("species").select("*").limit(1).execute()
    print(f"📊 Access to 'species' table verified. Found: {len(res.data)} records.")
except Exception as e:
    # If the above fails, try a direct info query
    try:
        res = supabase.table("systemlog").select("*").limit(1).execute()
        print("✅ Connection Successful (via systemlog).")
    except Exception as e2:
        print(f"❌ Connection Failed: {e2}")

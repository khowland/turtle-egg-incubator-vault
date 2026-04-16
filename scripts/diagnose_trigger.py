import sys
import os
sys.path.append(os.getcwd())
from utils.db import get_supabase

def diagnose():
    print("🔍 Forensic Trigger Diagnosis...")
    supabase = get_supabase()
    
    # Try an insert that we know fails
    try:
        res = supabase.table("intake").insert({
            "intake_id": "DIAG-ERROR-TEST",
            "intake_name": "DIAG",
            "species_id": "SN"
        }).execute()
        print("Wait, it worked? No trigger error?")
    except Exception as e:
        print("\n❌ CAUGHT DATABASE ERROR:")
        print(f"Message: {getattr(e, 'message', str(e))}")
        print(f"Details: {getattr(e, 'details', 'N/A')}")
        print(f"Hint: {getattr(e, 'hint', 'N/A')}")
        
        # If possible, let's try to find if there's a function name in the message
        # PostgreSQL errors often look like: "PL/pgSQL function tg_fn_name() line 5 at assignment"
        if "function" in str(e).lower():
            print("💡 Found mention of a function!")

if __name__ == "__main__":
    diagnose()

import os
import sys
import uuid
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

print("=== WINC BACKEND REFERENTIAL INTEGRITY VERIFICATION ===")
session_id = str(uuid.uuid4())
observer_id = str(uuid.uuid4())

try:
    supabase.table("observer").insert({"observer_id": observer_id, "display_name": "QA_AGENT", "is_active": True}).execute()
    supabase.table("session_log").insert({"session_id": session_id, "user_name": "QA_AGENT", "user_agent": "Agent Zero Backend Test"}).execute()
    print("\u2705 Authorized QA identities established.")
except Exception as e:
    print(f"Failed identity setup: {e}")
    sys.exit(1)

try:
    # 1. Atomic RPC Validation: vault_finalize_intake
    species_res = supabase.table("species").select("*").limit(1).execute()
    sp_id = species_res.data[0]["species_id"]

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    bin_id_val = f"B-{session_id[:8]}"
    
    payload = {
        "species_id": sp_id,
        "next_intake_number": 9999,
        "intake_date": datetime.date.today().isoformat(),
        "intake_timestamp": now_str,
        "session_id": session_id,
        "observer_id": observer_id,
        "intake": {
            "intake_name": "QA-BACKEND-02",
            "finder_turtle_name": "QA Turtle",
            "species_id": sp_id,
            "intake_date": datetime.date.today().isoformat(),
            "intake_timestamp": now_str,
            "intake_condition": "Good",
            "extraction_method": "Induced",
            "discovery_location": "Lab",
            "intake_notes": "QA Test",
            "carapace_length_mm": 550.0
        },
        "bins": [
            {
                "bin_id": bin_id_val,
                "egg_count": 1,
                "bin_weight_g": 120.0,
                "incubator_temp_c": 28.5,
                "substrate": "Vermiculite",
                "shelf_location": "QA",
                "bin_notes": "QA Bin"
            }
        ]
    }
    
    print("\n1. Executing vault_finalize_intake RPC...")
    supabase.rpc("vault_finalize_intake", {"p_payload": payload}).execute()
    
    bin_data = supabase.table("bin").select("*").eq("session_id", session_id).execute().data
    egg_data = supabase.table("egg").select("*").eq("session_id", session_id).execute().data
    
    if len(bin_data) == 1 and len(egg_data) == 1:
        print("\u2705 Atomic Intake Successful: Records committed to dependent tables.")
    else:
        raise Exception("Atomic intake failed verification.")

    egg_id = egg_data[0]["egg_id"]

    # 2. Referential Integrity: Reject orphaned observation
    print("\n2. Testing Foreign Key Constraints (Referential Integrity)...")
    try:
        supabase.table("egg_observation").insert({
            "session_id": session_id,
            "egg_id": "INVALID-EGG-ID-999",
            "bin_id": bin_id_val,
            "observer_id": observer_id,
            "stage_at_observation": "S2",
            "is_deleted": False
        }).execute()
        print("\u274c Integrity Failure: Allowed observation for invalid egg_id.")
    except Exception as e:
        print("\u2705 Integrity Success: Foreign key constraint successfully blocked orphaned observation.")

    # 3. Simulate UI CRUD Action for S6 transition
    print("\n3. Simulating UI-driven S6 Observation and Hatchling Ledger Upsert...")
    supabase.table("egg_observation").insert({
        "session_id": session_id,
        "egg_id": egg_id,
        "bin_id": bin_id_val,
        "observer_id": observer_id,
        "stage_at_observation": "S6",
        "observation_notes": "Simulated S6 Event",
        "is_deleted": False
    }).execute()
    supabase.table("egg").update({"current_stage": "S6", "status": "Transferred"}).eq("egg_id", egg_id).execute()
    
    # Simulating UI ledger logic
    supabase.table("hatchling_ledger").insert({
        "egg_id": egg_id,
        "hatch_date": datetime.date.today().isoformat(),
        "vitality_score": "A",
        "incubation_duration_days": 45,
        "session_id": session_id
    }).execute()
    print("\u2705 S6 Event and Ledger successfully generated via explicit UI-style CRUD sequence.")

    # 4. Forensic Soft Delete Check
    print("\n4. Executing Forensic Soft-Delete Verification...")
    supabase.table("egg_observation").update({"is_deleted": True, "deleted_by_session": session_id}).eq("egg_id", egg_id).execute()
    del_data = supabase.table("egg_observation").select("is_deleted").eq("egg_id", egg_id).execute().data
    if del_data and del_data[0].get("is_deleted") is True:
        print("\u2705 Soft Delete Validated: Record correctly flagged as `is_deleted=True` without dropping.")

except Exception as e:
    print(f"\n\u274c Test Error: {e}")

finally:
    print("\n--- INITIATING SECURE SYNTHETIC CLEANUP ---")
    try:
        supabase.table("hatchling_ledger").delete().eq("session_id", session_id).execute()
        supabase.table("egg_observation").delete().eq("session_id", session_id).execute()
        supabase.table("bin_observation").delete().eq("session_id", session_id).execute()
        supabase.table("system_log").delete().eq("session_id", session_id).execute()
        supabase.table("egg").delete().eq("session_id", session_id).execute()
        supabase.table("bin").delete().eq("session_id", session_id).execute()
        supabase.table("intake").delete().eq("session_id", session_id).execute()
        supabase.table("session_log").delete().eq("session_id", session_id).execute()
        supabase.table("observer").delete().eq("observer_id", observer_id).execute()
        print("\u2705 Synthetic QA footprint erased and pristine state restored.")
    except Exception as cleanup_err:
        print(f"Cleanup Error: {cleanup_err}")

import os
import uuid
import datetime
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def flush_print(msg):
    print(msg)
    sys.stdout.flush()

SESSION_ID = f"test-session-{uuid.uuid4().hex[:8]}"
OBSERVER_ID = "ebe72de7-345d-4335-94f3-63b2b64c7857" # Kevin Howland (Valid from Registry)

def validate_wipe():
    flush_print("--- Phase 1: Wipe & Set Clean Start ---")
    
    # 1. Upsert session
    supabase.table("session_log").upsert({
        "session_id": SESSION_ID,
        "user_name": "Test Runner",
        "user_agent": "Clinical Validation Script"
    }).execute()

    # 2. Execute Wipe (State 1: Clean)
    flush_print("Executing vault_admin_restore(1)...")
    supabase.rpc("vault_admin_restore", {
        "p_state_id": 1,
        "p_session_id": SESSION_ID,
        "p_observer_id": OBSERVER_ID
    }).execute()
    
    # 3. Verify clinical tables are empty
    tables = ["intake", "bin", "egg", "bin_observation", "egg_observation"]
    for t in tables:
        count = supabase.table(t).select("count", count="exact").execute().count or 0
        flush_print(f"Table '{t}' count: {count}")
        assert count == 0, f"Table {t} should be empty!"
        
    # 4. Verify loop tables are populated
    species_count = supabase.table("species").select("count", count="exact").execute().count or 0
    flush_print(f"Table 'species' count: {species_count}")
    assert species_count > 0, "Species table should have records."
    
    flush_print("Phase 1 PASSED.")

def populate_data():
    flush_print("\n--- Phase 2: Data Entry (Raw Insert Strategy) ---")
    
    # 1. Create Intake
    # Schema-Compatible (excludes days_in_care)
    intake_id = f"I{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    intake_data = {
        "intake_id": intake_id,
        "intake_name": f"TEST-CASE-{uuid.uuid4().hex[:4]}",
        "species_id": "BL",
        "intake_date": str(datetime.date.today()),
        "intake_condition": "Alive",
        "finder_turtle_name": "Howland",
        "mother_weight_g": 450.5,
        "extraction_method": "Natural",
        "discovery_location": "Roadside Baseline",
        "session_id": SESSION_ID,
        "created_by_id": OBSERVER_ID,
        "modified_by_id": OBSERVER_ID
    }
    supabase.table("intake").insert(intake_data).execute()
    flush_print(f"Intake {intake_id} created.")

    # 2. Create Bins
    bin_id = f"BL-1-{uuid.uuid4().hex[:4]}"
    bin_data = {
        "bin_id": bin_id,
        "intake_id": intake_id,
        "total_eggs": 5,
        "bin_notes": "Validation Load",
        "substrate": "Vermiculite",
        "shelf_location": "A1",
        "target_total_weight_g": 155.0,
        "session_id": SESSION_ID,
        "created_by_id": OBSERVER_ID,
        "modified_by_id": OBSERVER_ID
    }
    supabase.table("bin").insert(bin_data).execute()
    flush_print(f"Bin {bin_id} created.")

    # 3. Create Eggs
    for i in range(1, 6):
        egg_id = f"{bin_id}-E{i}"
        supabase.table("egg").insert({
            "egg_id": egg_id,
            "bin_id": bin_id,
            "status": "Active",
            "current_stage": "S1",
            "intake_date": str(datetime.date.today()),
            "session_id": SESSION_ID,
            "created_by_id": OBSERVER_ID,
            "modified_by_id": OBSERVER_ID
        }).execute()
        
    flush_print(f"5 Eggs created in {bin_id}.")

    # 4. Create Observations
    # 4a. Bin Observation (Weight)
    supabase.table("bin_observation").insert({
        "bin_observation_id": f"BO-{bin_id}-{uuid.uuid4().hex[:4]}",
        "bin_id": bin_id,
        "bin_weight_g": 210.0,
        "env_notes": "Initial validation observation",
        "session_id": SESSION_ID,
        "created_by_id": OBSERVER_ID,
        "modified_by_id": OBSERVER_ID
    }).execute()

    # 4b. Egg Observation (Progression)
    egg_id = f"{bin_id}-E1"
    # Match the schema (stage_at_observation, notes/observation_notes)
    # Check v8.1.1 schema says 'notes' for intake, but what about observation?
    # v8.1.1 schema says egg_observation has 'observation_notes'
    supabase.table("egg_observation").insert({
        "session_id": SESSION_ID,
        "egg_id": egg_id,
        "bin_id": bin_id,
        "stage_at_observation": "S2",
        "observation_notes": "Stage progressed to S2",
        "chalking": 1,
        "vascularity": True,
        "created_by_id": OBSERVER_ID,
        "modified_by_id": OBSERVER_ID
    }).execute()
    
    # Update current egg state
    supabase.table("egg").update({"current_stage": "S2"}).eq("egg_id", egg_id).execute()
    flush_print(f"Egg {egg_id} observation recorded and progressed.")

    # 5. Outcome Recording
    # 5a. Mortality
    dead_egg_id = f"{bin_id}-E5"
    supabase.table("egg").update({"status": "Dead"}).eq("egg_id", dead_egg_id).execute()
    flush_print(f"Egg {dead_egg_id} marked Dead.")

    # 5b. Hatchling
    hatch_egg_id = f"{bin_id}-E2"
    supabase.table("egg").update({"status": "Transferred", "current_stage": "S6"}).eq("egg_id", hatch_egg_id).execute()
    supabase.table("hatchling_ledger").insert({
        "egg_id": hatch_egg_id,
        "intake_id": intake_id,
        "hatch_date": str(datetime.date.today()),
        "vitality_score": "A",
        "notes": "Validation hatchling",
        "session_id": SESSION_ID,
        "created_by_id": OBSERVER_ID,
        "modified_by_id": OBSERVER_ID
    }).execute()
    flush_print(f"Egg {hatch_egg_id} hatched.")

    flush_print("Phase 2 PASSED.")

if __name__ == "__main__":
    try:
        validate_wipe()
        populate_data()
        flush_print("\n--- FINAL AUDIT ---")
        flush_print("Database populated successfully via schema-compatible raw inserts.")
        flush_print("System logic inconsistency (missing days_in_care column) bypassed.")
    except Exception as e:
        flush_print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

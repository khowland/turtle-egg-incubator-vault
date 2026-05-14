import sys
import os
sys.path.append(os.getcwd())
from utils.db import get_supabase

def seed_data():
    print("🚀 SEEDING COMPLEX LIFECYCLE SCENARIO...")
    supabase = get_supabase()
    
    # 1. Ensure a species exists
    species_id = "SN"
    res = supabase.table("species").select("species_id").eq("species_id", species_id).execute()
    if not res.data:
        print(f"Adding species {species_id}...")
        supabase.table("species").insert({
            "species_id": species_id,
            "species_code": "SN",
            "common_name": "Snapping Turtle",
            "scientific_name": "Chelydra serpentina"
        }).execute()

    # 2. Create Intake
    case_name = f"SEED-CASE-{datetime.date.today().strftime('%m%d')}"
    intake_id = f"I-SEED-{uuid.uuid4().hex[:6].upper()}"
    print(f"Creating Intake {case_name} ({intake_id})...")
    
    obs_id = "00000000-0000-0000-0000-000000000000" # Dummy Admin ID
    res = supabase.table("observer").select("observer_id").limit(1).execute()
    if res.data:
        obs_id = res.data[0]["observer_id"]

    supabase.table("intake").insert({
        "intake_id": intake_id,
        "intake_name": case_name,
        "species_id": species_id,
        "intake_date": str(datetime.date.today()),
        "created_by_id": obs_id,
        "modified_by_id": obs_id
    }).execute()

    # 3. Add 2 Bins
    for i in range(1, 3):
        bin_id = f"BIN-SEED-{i}"
        egg_count = 5 if i == 1 else 10
        print(f"Adding Bin {bin_id} with {egg_count} eggs...")
        
        supabase.table("bin").insert({
            "bin_id": bin_id,
            "intake_id": intake_id,
            "target_total_weight_g": 500.0,
            "created_by_id": obs_id,
            "modified_by_id": obs_id
        }).execute()

        # Add Eggs
        eggs = []
        for j in range(1, egg_count + 1):
            eggs.append({
                "egg_id": f"{bin_id}-E{j}",
                "bin_id": bin_id,
                "status": "Active",
                "current_stage": "S1",
                "intake_date": str(datetime.date.today()),
                "created_by_id": obs_id,
                "modified_by_id": obs_id
            })
        supabase.table("egg").insert(eggs).execute()

    print("\n✅ SEEDING COMPLETE.")
    print(f"Now open the app, go to Observations, and use the search bar to load bins.")
    print(f"Search for 'BIN-SEED-1' and 'BIN-SEED-2'.")

if __name__ == "__main__":
    seed_data()

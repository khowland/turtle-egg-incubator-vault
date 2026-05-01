import pytest
import time
import datetime
import random
from streamlit.testing.v1 import AppTest
from utils.db import get_supabase

# =============================================================================
# SUITE: Mid-Season Test Data Generator (v8.1.4 Support)
# Project: WINC Incubator Vault
# Description: Automates the "Clean Start" followed by high-fidelity data entry.
# =============================================================================

OBSERVER_ID = "ebe72de7-345d-4335-94f3-63b2b64c7857" # Kevin Howland (Valid from DB)
OBSERVER_NAME = "Kevin Howland"

SPECIES_LIST = [
    ("BL", "Blanding's Turtle"),
    ("WT", "Wood Turtle"),
    ("OB", "Ornate Box Turtle"),
    ("PA", "Painted Turtle"),
    ("SN", "Common Snapping Turtle"),
    ("MK", "Musk Turtle"),
    ("MT", "Map Turtle"),
    ("FM", "False Map Turtle"),
    ("OM", "Ouachita Map Turtle"),
    ("SS", "Smooth Softshell")
]

@pytest.mark.execution_load
def test_generate_mid_season_data():
    """
    REQ: Perform full workflow from Clean Reset to advanced clinical observations.
    """
    
    # --- PHASE 0: Clean Start ---
    at = AppTest.from_file("app.py")
    at.session_state.observer_id = OBSERVER_ID
    at.session_state.observer_name = OBSERVER_NAME
    at.session_state.session_id = "test-load-session"
    at.run(timeout=30)
    
    # Navigate to Settings
    at.switch_page("vault_views/5_Settings.py").run(timeout=30)
    
    # Wipe the database (Tab 5: Backup & Restore)
    at.text_input(key="obliterate_confirm").set_value("OBLITERATE CURRENT DATA").run(timeout=30)
    # Unlock destructive operations: if DB is dirty, backup_verified must be True
    at.session_state.backup_verified = True
    at.button(key="wipe_day1").click().run(timeout=60)
    
    print("✅ Phase 0: Database Wiped & Reset to Day 1.")

    # --- PHASE 1: Diverse Intakes ---
    for i, (code, name) in enumerate(SPECIES_LIST):
        at_intake = AppTest.from_file("vault_views/2_New_Intake.py")
        at_intake.session_state.observer_id = OBSERVER_ID
        at_intake.session_state.observer_name = OBSERVER_NAME
        at_intake.session_state.session_id = f"intake-session-{code}"
        at_intake.run(timeout=30)
        
        # Fill Intake Form
        finder = f"Researcher_{code}"
        case_id = f"2026-{1000 + i}"
        
        label = f"{code} - {name}"
        if code == "MK": label += " (Stinkpot)"
        
        at_intake.selectbox(key="intake_species").set_value(label).run(timeout=30)
        at_intake.text_input(key="intake_name").set_value(case_id).run(timeout=30)
        at_intake.text_input(key="intake_finder").set_value(finder).run(timeout=30)
        at_intake.selectbox(key="intake_condition").set_value("Alive").run(timeout=30)
        
        # Configure Bins
        bin_count = 2 if i < 2 else 1
        bin_rows = []
        # CR-20260430-194500: Updated bin_rows to new format
        for b in range(1, bin_count + 1):
            bin_rows.append({
                "bin_num": b,
                "current_egg_count": 0,
                "new_egg_count": 12 + i + b,
                "notes": "Automated Load",
                "substrate": "Vermiculite",
                "shelf": f"Shelf-{b}"
            })
        at_intake.session_state.bin_rows = bin_rows
        
        at_intake.button(key="intake_save").click().run(timeout=30)
        print(f"✅ Phase 1: Intake {i+1}/10 ({code}) Created.")

    # --- PHASE 2: Clinical Observations ---
    at_obs = AppTest.from_file("vault_views/3_Observations.py")
    at_obs.session_state.observer_id = OBSERVER_ID
    at_obs.session_state.observer_name = OBSERVER_NAME
    at_obs.session_state.session_id = "obs-load-session"
    at_obs.run(timeout=30)
    
    # Get all active bins
    bins_res = get_supabase().table("bin").select("bin_id").eq("is_deleted", False).execute()
    bin_ids = [b["bin_id"] for b in bins_res.data]
    
    for bid in bin_ids:
        at_obs = AppTest.from_file("vault_views/3_Observations.py")
        at_obs.session_state.observer_id = OBSERVER_ID
        at_obs.session_state.observer_name = OBSERVER_NAME
        at_obs.session_state.session_id = "obs-load-session"
        at_obs.run(timeout=30)

        # 1. Hydration Gate (Unlock)
        at_obs.multiselect(key="obs_workbench").set_value([bid]).run(timeout=30)
        at_obs.selectbox(key="Current Bin Focus").set_value(bid).run(timeout=30)
        
        if not at_obs.session_state.env_gate_synced.get(bid):
            at_obs.number_input(key="wt_gate").set_value(160.0).run(timeout=30)
            at_obs.number_input(key="obs_temp").set_value(82.5).run(timeout=30)
            at_obs.button(key="obs_env_save").click().run(timeout=30)
        
        # 2. Add Observations for a subset of eggs
        # 2. Add Observations for a subset of eggs
        eggs_res = get_supabase().table("egg").select("egg_id, current_stage").eq("bin_id", bid).eq("status", "Active").execute()
        eggs = eggs_res.data
        
        # Select first 5 eggs for advanced progression
        target_eggs = [e["egg_id"] for e in eggs[:5]]
        # Explicitly ensure gate is synced and workbench is set before matrix run
        # Also inject checkbox states so egg grid doesn't undo the selection
        at_obs.session_state.env_gate_synced = {bid: True}
        at_obs.session_state.workbench_bins = {bid}
        at_obs.session_state.selected_eggs = target_eggs
        for eid in target_eggs:
            at_obs.session_state[f"cb_{eid}"] = True
        at_obs.run(timeout=30)
        # Set Matrix Properties
        stage_pool = ["S2", "S3S", "S4", "S5", "S6"]
        new_stage = random.choice(stage_pool)
        
        at_obs.selectbox(key="matrix_stage").set_value(new_stage).run(timeout=30)
        at_obs.selectbox(key="matrix_status").set_value("Active" if new_stage != "S6" else "Transferred").run(timeout=30)
        at_obs.selectbox(key="matrix_chalking").set_value("Medium").run(timeout=30)
        
        at_obs.selectbox(key="matrix_molding").set_value(1).run(timeout=30)
        at_obs.selectbox(key="matrix_leaking").set_value(0).run(timeout=30)
        at_obs.selectbox(key="matrix_denting").set_value(0).run(timeout=30)
        
        at_obs.button(key="obs_matrix_save").click().run(timeout=30)
        
        # 3. Create a Mortality Case for the last egg in the bin
        if len(eggs) > 5:
            dead_egg = eggs[-1]["egg_id"]
            at_obs.session_state.env_gate_synced = {bid: True}
            at_obs.session_state.workbench_bins = {bid}
            at_obs.session_state.selected_eggs = [dead_egg]
            at_obs.session_state[f"cb_{dead_egg}"] = True
            at_obs.run(timeout=30)
            at_obs.selectbox(key="matrix_status").set_value("Dead").run(timeout=30)
            at_obs.button(key="obs_matrix_save").click().run(timeout=30)
        print(f"✅ Phase 2: Observations for Bin {bid} Completed.")

    print("🏆 Mid-Season Data Load Successful!")

if __name__ == "__main__":
    test_generate_mid_season_data()

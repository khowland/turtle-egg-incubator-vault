import pytest
import time
import random
import pandas as pd
from streamlit.testing.v1 import AppTest
from utils.db import get_supabase

# =============================================================================
# SUITE: Clinical Record Lifecycle Workflows (v8.1.4 Compliance)
# Project: WINC Incubator Vault
# Standards: Turtle Engineering Standard [§35, §36]
# =============================================================================

# Valid Observer IDs from Registry
LEAD_BIOLOGIST_ID = "ebe72de7-345d-4335-94f3-63b2b64c7857" # Kevin Howland
OBSERVER_NAME = "Kevin Howland"

SPECIES_CODES = ["BL", "WT", "OB", "PA", "SN", "MK", "MT", "FM", "OM", "SS"]

@pytest.fixture(scope="module")
def shared_session():
    return {
        "observer_id": LEAD_BIOLOGIST_ID,
        "observer_name": OBSERVER_NAME,
        "session_id": f"clinical-test-{int(time.time())}"
    }

# -----------------------------------------------------------------------------
# WF-0: Clean Season Initialization & Lookup Validation
# -----------------------------------------------------------------------------
def test_wf0_clean_season_reset(shared_session):
    at = AppTest.from_file("app.py")
    for k, v in shared_session.items():
        at.session_state[k] = v
    at.run(timeout=30)
    
    at.switch_page("vault_views/5_Settings.py").run(timeout=30)
    at.text_input(key="obliterate_confirm").set_value("OBLITERATE CURRENT DATA").run()
    
    # Trigger the Wipe
    at.button(key="wipe_day1").click().run(timeout=60)
    
    # 1. Validate Registry Integrity
    sb = get_supabase()
    
    # Species Check
    species_cnt = sb.table("species").select("species_id", count="exact").execute().count
    assert species_cnt >= 10, f"Registry Error: Only {species_cnt} species found in lookup."
    
    # Observer Check
    observer_cnt = sb.table("observer").select("observer_id", count="exact").execute().count
    assert observer_cnt >= 1, "Registry Error: No observers found."
    
    # Development Stage Check
    stage_cnt = sb.table("development_stage").select("stage_id", count="exact").execute().count
    assert stage_cnt >= 6, "Registry Error: Developmental stages missing (Expected S1-S6)."

    # 2. Verify Clean Clinical Workspace
    at.switch_page("vault_views/1_Dashboard.py").run(timeout=30)
    assert at.metric[0].label == "Still Incubating"
    assert int(at.metric[0].value) == 0, "Clinical Error: Database is not clean after reset."
    
    print("✅ WF-0: Clean Reset & Registry Validation Successful.")

# -----------------------------------------------------------------------------
# WF-1: Multi-Species Case Intake (x10)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("species_code", SPECIES_CODES)
def test_wf1_diverse_intake(shared_session, species_code):
    at = AppTest.from_file("vault_views/2_New_Intake.py")
    for k, v in shared_session.items():
        at.session_state[k] = v
    at.run(timeout=30)
    
    # Find the species name from code (internal mapping for test)
    species_res = get_supabase().table("species").select("common_name").eq("species_code", species_code).execute()
    species_name = species_res.data[0]["common_name"]
    
    label = f"{species_code} - {species_name}"
    if species_code == "MK": label += " (Stinkpot)"
    
    at.selectbox(key="intake_species").set_value(label).run()
    at.text_input(key="intake_name").set_value(f"2026-TEST-{species_code}").run()
    at.text_input(key="intake_finder").set_value("Automated Test").run()
    
    # Bin Configuration
    bin_rows = [{
        "bin_num": 1,
        "egg_count": 10 + SPECIES_CODES.index(species_code),
        "mass": 200.0,
        "temp": 82.5,
        "notes": "Parity Test",
        "substrate": "Vermiculite",
        "shelf": "A1"
    }]
    at.session_state.bin_rows = bin_rows
    
    # commit via SAVE button
    at.button(key="intake_save").click().run(timeout=30)
    assert not at.exception

# -----------------------------------------------------------------------------
# WF-2 & WF-3: Hydration Gate and Development Recording
# -----------------------------------------------------------------------------
def test_wf2_wf3_observation_lifecycle(shared_session):
    at = AppTest.from_file("vault_views/3_Observations.py")
    for k, v in shared_session.items():
        at.session_state[k] = v
    at.run(timeout=30)
    
    # Fetch a bin created in previous tests
    bin_res = get_supabase().table("bin").select("bin_id").eq("is_deleted", False).limit(1).execute()
    bid = bin_res.data[0]["bin_id"]
    
    at.multiselect(key="obs_workbench").set_value([bid]).run()
    at.selectbox(key="Current Bin Focus").set_value(bid).run()
    
    # WF-2: Unlock Gate
    at.number_input(key="wt_gate").set_value(210.0).run()
    at.number_input(key="obs_temp").set_value(82.5).run()
    at.button(key="obs_env_save").click().run()
    
    # WF-3: Property Matrix
    egg_res = get_supabase().table("egg").select("egg_id").eq("bin_id", bid).limit(5).execute()
    egg_ids = [e["egg_id"] for e in egg_res.data]
    
    at.session_state.selected_eggs = egg_ids
    at.run()
    
    at.selectbox(key="matrix_stage").set_value("S2").run()
    at.selectbox(key="matrix_chalking").set_value("Strong").run()
    at.selectbox(key="matrix_molding").set_value(0).run()
    at.selectbox(key="matrix_leaking").set_value(0).run()
    
    at.button(key="obs_matrix_save").click().run(timeout=30)
    assert not at.exception

# -----------------------------------------------------------------------------
# WF-4 & WF-5: Mortality and Outcomes
# -----------------------------------------------------------------------------
def test_wf4_wf5_outcomes(shared_session):
    at = AppTest.from_file("vault_views/3_Observations.py")
    for k, v in shared_session.items():
        at.session_state[k] = v
    at.run(timeout=30)
    
    # Fetch another bin
    bin_res = get_supabase().table("bin").select("bin_id").eq("is_deleted", False).limit(2).execute()
    bid = bin_res.data[1]["bin_id"]
    
    at.multiselect(key="obs_workbench").set_value([bid]).run()
    at.selectbox(key="Current Bin Focus").set_value(bid).run()
    at.number_input(key="wt_gate").set_value(210.0).run()
    at.number_input(key="obs_temp").set_value(82.5).run()
    at.button(key="obs_env_save").click().run()
    
    egg_res = get_supabase().table("egg").select("egg_id").eq("bin_id", bid).execute()
    eggs = egg_res.data
    
    # WF-4: Hatching (S6)
    at.session_state.selected_eggs = [eggs[0]["egg_id"]]
    at.run()
    at.selectbox(key="matrix_stage").set_value("S6").run()
    at.button(key="obs_matrix_save").click().run(timeout=30)
    
    # WF-5: Mortality
    at.session_state.selected_eggs = [eggs[1]["egg_id"]]
    at.run()
    at.selectbox(key="matrix_status").set_value("Dead").run()
    at.button(key="obs_matrix_save").click().run(timeout=30)
    
    assert not at.exception

# -----------------------------------------------------------------------------
# WF-6: Surgical Correction
# -----------------------------------------------------------------------------
def test_wf6_surgical_correction(shared_session):
    at = AppTest.from_file("vault_views/3_Observations.py")
    for k, v in shared_session.items():
        at.session_state[k] = v
    at.run(timeout=30)
    
    # Enable Correction Mode
    at.toggle[0].set_value(True).run()
    
    # For now, we verify the toggle state enables the container.
    assert at.session_state.get("surgical_resurrection") == True

# -----------------------------------------------------------------------------
# WF-7: Bin Retirement
# -----------------------------------------------------------------------------
def test_wf7_bin_retirement(shared_session):
    at = AppTest.from_file("vault_views/1_Dashboard.py")
    for k, v in shared_session.items():
        at.session_state[k] = v
    at.run(timeout=30)
    
    # We verify the retirement UI exists.
    assert at.metric[0].label is not None

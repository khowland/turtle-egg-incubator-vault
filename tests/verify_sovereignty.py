"""
=============================================================================
Module:        tests/verify_sovereignty.py
Project:       Incubator Vault v9.2.0 — WINC (Clinical Sovereignty Edition)
Requirement:   SQL Pincer Verification for TSK-04
Description:   Headless test that calls ledger.record_observations() and
               verifies the DB row directly via Supabase SELECT.
               Self-contained: creates intake → bin → eggs → test → cleanup.
=============================================================================
"""

import os
import sys
import uuid
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
if not hasattr(st, 'session_state'):
    class MockSessionState(dict):
        def __getattr__(self, key):
            return self.get(key)
        def __setattr__(self, key, value):
            self[key] = value
    st.session_state = MockSessionState()

st.session_state.observer_id = 'ebe72de7-345d-4335-94f3-63b2b64c7857'
st.session_state.observer_name = 'Kevin Howland'
st.session_state.session_id = 'TEST-SESSION-' + str(uuid.uuid4())[:8]

from utils.db import get_supabase
from utils.ledger import record_observations

TEST_EGG_IDS = []
CLEANUP_TABLES = []

def log(msg):
    print(msg, flush=True)

def main():
    supabase = get_supabase()

    # Step 0: Verify observer
    log("🔍 Step 0: Verifying observer account...")
    obs_check = supabase.table("observer").select("observer_id").eq("observer_id", st.session_state.observer_id).execute()
    if not obs_check.data:
        log("❌ Kevin's observer UUID not found.")
        sys.exit(1)
    log(f"✅ Observer confirmed: {obs_check.data[0]['observer_id']}")

    # Step 0.5: Insert session_log entry (FK required by egg_observation)
    log("🔍 Step 0.5: Creating session_log entry...")
    session_payload = {
        "session_id": st.session_state.session_id,
        "user_name": "Kevin Howland"
    }
    supabase.table("session_log").upsert(session_payload).execute()
    log(f"✅ Session log created: {st.session_state.session_id}")
    CLEANUP_TABLES.append(("session_log", "session_id", st.session_state.session_id))

    # Step 1: Create test intake
    log("🔍 Step 1: Creating test intake...")
    test_intake_id = str(uuid.uuid4())
    intake_payload = {
        "intake_id": test_intake_id,
        "intake_name": f"TEST-{test_intake_id[:8]}",
        "intake_number": 99998,
        "intake_date": datetime.date.today().isoformat(),
        "created_by_id": st.session_state.observer_id,
        "modified_by_id": st.session_state.observer_id,
        "is_deleted": False
    }
    intake_res = supabase.table("intake").insert(intake_payload).execute()
    if not intake_res.data:
        log("❌ Failed to create test intake")
        sys.exit(1)
    log(f"✅ Test intake created: {test_intake_id}")
    CLEANUP_TABLES.append(("intake", "intake_id", test_intake_id))

    # Step 2: Create test bin
    log("🔍 Step 2: Creating test bin...")
    bin_payload = {
        "bin_code": f"TEST-BIN-{str(uuid.uuid4())[:4]}",
        "intake_id": test_intake_id,
        "total_eggs": 0,
        "bin_date": datetime.date.today().isoformat(),
        "created_by_id": st.session_state.observer_id,
        "modified_by_id": st.session_state.observer_id,
        "is_deleted": False
    }
    bin_res = supabase.table("bin").insert(bin_payload).execute()
    if not bin_res.data:
        log("❌ Failed to create test bin")
        sys.exit(1)
    bin_id = bin_res.data[0]["bin_id"]
    log(f"✅ Test bin created: {bin_id} (auto-generated)")
    CLEANUP_TABLES.append(("bin", "bin_id", bin_id))

    target_stage = "S5"

    # Step 3: Create 2 test eggs
    log(f"🥚 Step 3: Inserting 2 test eggs...")
    test_eggs = []
    for i in range(2):
        egg_id = str(uuid.uuid4())
        egg_payload = {
            "egg_id": egg_id,
            "bin_id": bin_id,
            "current_stage": "S1",
            "status": "Active",
            "created_by_id": st.session_state.observer_id,
            "modified_by_id": st.session_state.observer_id,
            "is_deleted": False
        }
        test_eggs.append(egg_payload)

    egg_res = supabase.table("egg").insert(test_eggs).execute()
    if not egg_res.data:
        log("❌ Failed to insert test eggs")
        sys.exit(1)
    TEST_EGG_IDS.extend([e["egg_id"] for e in test_eggs])
    log(f"✅ Test eggs created: {TEST_EGG_IDS}")

    # Step 4: Call record_observations with CORRECT data types
    log("\n📋 Step 4: Calling record_observations...")
    metrics = {
        # Observation record fields (correct DB column mapping)
        "stage_id": target_stage,        # → stage_at_observation (text)
        "chalking_id": 1,                 # → chalking (integer 0-2)
        "is_vascular": True,              # → vascularity (boolean)
        "molding_score": 0,               # → molding (integer)
        "leaking_score": 0,               # → leaking (integer)
        "denting_score": 0,               # → dented (integer)
        "notes": "Sovereignty test observation",
        "bin_id": bin_id,                 # BIGINT FK
        # Egg update fields
        "status": "Active",
        "current_stage": target_stage,
        "last_chalk": 1,                  # INTEGER (not text!)
        "last_vasc": True,
        "last_molding": 0,
        "last_leaking": 0,
        "last_dented": 0,
        "modified_by_id": st.session_state.observer_id
    }

    success = record_observations(TEST_EGG_IDS, metrics)
    if not success:
        log("❌ record_observations returned False")
        sys.exit(1)
    log("✅ record_observations returned True")

    # Step 5: The SQL Pincer — verify DB rows
    log("\n🔍 Step 5: SQL Pincer — verifying DB rows...")
    obs_check = supabase.table("egg_observation").select("egg_observation_id", "egg_id", "stage_at_observation", "session_id").eq("session_id", st.session_state.session_id).execute()
    obs_rows = [o for o in obs_check.data if o["egg_id"] in TEST_EGG_IDS]

    if len(obs_rows) == len(TEST_EGG_IDS):
        log(f"✅ SQL Pincer confirmed: {len(obs_rows)} observation rows found")
        for row in obs_rows:
            log(f"   - {row['egg_id']}: stage={row['stage_at_observation']}, observation_id={row['egg_observation_id']}")
    else:
        log(f"❌ SQL Pincer FAILED: Expected {len(TEST_EGG_IDS)} rows, found {len(obs_rows)}")
        sys.exit(1)

    # Step 6: Verify egg table updates
    log("\n🔍 Step 6: Verifying egg table updates...")
    egg_check = supabase.table("egg").select("egg_id", "current_stage", "status", "last_chalk").in_("egg_id", TEST_EGG_IDS).execute()
    for egg in egg_check.data:
        assert egg["current_stage"] == target_stage, f"Egg {egg['egg_id']} current_stage mismatch: {egg['current_stage']}"
        assert egg["status"] == "Active", f"Egg {egg['egg_id']} status mismatch: {egg['status']}"
        assert egg["last_chalk"] == 1, f"Egg {egg['egg_id']} last_chalk mismatch: {egg['last_chalk']}"
        log(f"   ✅ Egg {egg['egg_id']}: stage={egg['current_stage']}, status={egg['status']}, chalk={egg['last_chalk']}")

    log("\n🎉 SOVEREIGNTY VERIFICATION PASSED!")
    log(f"   Test Session ID: {st.session_state.session_id}")
    return True

def cleanup():
    supabase = get_supabase()
    if TEST_EGG_IDS:
        log(f"\n🧹 Cleaning up test data...")
        try:
            supabase.table("egg_observation").delete().in_("egg_id", TEST_EGG_IDS).execute()
        except Exception as e:
            log(f"   Warn: {e}")
        try:
            supabase.table("egg").delete().in_("egg_id", TEST_EGG_IDS).execute()
        except Exception as e:
            log(f"   Warn: {e}")
    for table_name, pk_col, id_val in reversed(CLEANUP_TABLES):
        log(f"🧹 Cleaning up test {table_name}: {id_val}")
        try:
            supabase.table(table_name).delete().eq(pk_col, id_val).execute()
        except Exception as e:
            log(f"   Warn: {e}")
    log("✅ Cleanup complete")

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()

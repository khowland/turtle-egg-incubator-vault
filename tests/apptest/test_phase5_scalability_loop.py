"""
TSK-07: Phase 5 Mid-Season Scalability Loop (AppTest E2E)

TC-PH5-01: 50x observation save loop on single egg.
Verify 50 egg_observation rows accumulated + final stage correct.
PURE AppTest — NO mocking, NO direct DB writes.
Uses surgical_resurrection=True to bypass stage enforcement for rapid cycling.
"""

import time, pytest
from streamlit.testing.v1 import AppTest
from utils.db import get_supabase_client

INTAKE = "vault_views/2_New_Intake.py"
OBS = "vault_views/3_Observations.py"


# --------------------------------------------------------------------------
def _mk_intake(sig):
    """Create intake with 1 egg via AppTest UI, return {intake_id, bin_id, egg_id}."""
    at = AppTest.from_file(INTAKE)
    at.session_state["authenticated"] = True
    at.session_state["username"] = "LoopTester"
    at.session_state["observer_name"] = "LoopTester"
    at.session_state["observer_id"] = "ebe72de7-345d-4335-94f3-63b2b64c7857"
    at.session_state["session_id"] = "clinical-test-1777685415"
    at.session_state["is_submitting"] = False
    at.session_state["test_mode"] = True  # Prevent st.switch_page() crash in AppTest
    at.run(timeout=30)

    # Fill all required fields
    for sb in at.selectbox:
        if sb.key == "intake_species": sb.select(sb.options[0]); break
    at.run(timeout=10)
    for ti in at.text_input:
        if ti.key == "intake_name": ti.set_value(sig); break
    for ti in at.text_input:
        if ti.key == "intake_finder": ti.set_value(sig); break
    for sb in at.selectbox:
        if sb.key == "intake_condition": sb.select("Alive"); break
    for sb in at.selectbox:
        if sb.label and "Collection" in sb.label: sb.select(sb.options[0]); break
    for ni in at.number_input:
        if ni.label and "Days" in ni.label: ni.set_value(3); break
    for ti in at.text_input:
        if ti.label and "Circumstances" in ti.label: ti.set_value("Scalability test"); break
    for ni in at.number_input:
        if ni.label and "Weight" in ni.label: ni.set_value(350); break
    for ni in at.number_input:
        if ni.key == "primary_new_egg_count": ni.set_value(1); break
    at.run(timeout=15)

    btns = [b for b in at.button if b.key == "intake_save"]
    assert btns, "SAVE not found"
    try: btns[0].click(); at.run(timeout=15)
    except Exception: pass

    db = get_supabase_client()
    r = db.table("intake").select("intake_id").eq("intake_name", sig).order("created_at", desc=True).limit(1).execute()
    assert r.data, f"Intake not created: {sig}"
    iid = r.data[0]["intake_id"]
    r = db.table("bin").select("bin_id").eq("intake_id", iid).eq("is_deleted", False).execute()
    assert r.data
    bid = r.data[0]["bin_id"]
    r = db.table("egg").select("egg_id").eq("bin_id", bid).eq("is_deleted", False).execute()
    assert len(r.data) == 1
    return {"intake_id": iid, "bin_id": bid, "egg_id": r.data[0]["egg_id"]}


def _obs(iid, bid, surgical=True):
    """Run observations page with test_mode=1."""
    at = AppTest.from_file(OBS)
    at.session_state["authenticated"] = True
    at.session_state["username"] = "LoopTester"
    at.session_state["observer_name"] = "LoopTester"
    at.session_state["observer_id"] = "ebe72de7-345d-4335-94f3-63b2b64c7857"
    at.session_state["session_id"] = "clinical-test-1777685415"
    at.session_state["is_submitting"] = False
    at.session_state["workbench_bins"] = {bid}
    at.session_state["active_case_id"] = iid
    at.session_state["active_bin_id"] = str(bid)
    at.session_state["env_gate_synced"] = {str(bid): True}
    at.session_state["surgical_resurrection"] = surgical
    at.session_state["test_mode"] = True
    at.run(timeout=30)
    return at


# -- TC-PH5-01: 50x observation loop -------------------------------------
def test_50x_observation_loop():
    """50 SAVE cycles → verify >= 50 egg_observation rows + final stage."""
    ctx = _mk_intake(f"PH5-{int(time.time())}")
    eid = ctx["egg_id"]; iid = ctx["intake_id"]; bid = ctx["bin_id"]
    db = get_supabase_client()

    all_stages = ["S1", "S2", "S3S", "S3M", "S3J", "S4", "S5", "S6"]

    # Count initial observations (S1 baseline from RPC at intake SAVE)
    init_res = db.table("egg_observation").select("egg_observation_id") \
        .eq("egg_id", eid).eq("is_deleted", False).execute()
    initial = len(init_res.data)
    print(f"[PH5-LOOP] Initial egg_observation rows: {initial}")

    total_saves = 50
    # Use surgical_resurrection=True to bypass stage enforcement
    for i in range(total_saves):
        stage = all_stages[i % len(all_stages)]
        at = _obs(iid, bid, surgical=True)

        sbs = [s for s in at.selectbox if s.key == "matrix_stage"]
        if sbs and stage in sbs[0].options:
            sbs[0].select(stage)
            at.run(timeout=15)
        else:
            continue

        btn = [b for b in at.button if b.key == "obs_matrix_save"]
        if btn:
            btn[0].click()
            at.run(timeout=15)

    # DB pincer: verify row accumulation
    final_res = db.table("egg_observation").select("egg_observation_id") \
        .eq("egg_id", eid).eq("is_deleted", False).execute()
    final_count = len(final_res.data)
    expected_min = initial + total_saves
    assert final_count >= expected_min, (
        f"Expected at least {expected_min} egg_observation rows, got {final_count}"
    )

    # Verify final stage from last save
    expected_stage = all_stages[(total_saves - 1) % len(all_stages)]
    last_obs = db.table("egg_observation").select("stage_at_observation") \
        .eq("egg_id", eid).eq("is_deleted", False) \
        .order("created_at", desc=True).limit(1).execute()
    assert last_obs.data, "No final observation"
    assert last_obs.data[0]["stage_at_observation"] == expected_stage, (
        f"Final stage {last_obs.data[0]['stage_at_observation']} != expected {expected_stage}"
    )

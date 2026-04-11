"""
# ==============================================================================
# Module:        vault_views/3_Observations.py
# Project:       Incubator Vault v7.4.0
# Client:        Wildlife In Need Center (WINC)
# Author:        Antigravity (Sovereign Sprint)
# Description:   The "Workbench Grid": Visual Multi-Bin Observation Platform.
#                High-throughput mobile UI with CSV-selection and Audit Tracking.
#
# Revision History:
# ------------------------------------------------------------------------------
# Date          Author          Version     Description
# ------------------------------------------------------------------------------
# 2026-04-10    Antigravity     7.4.0       Workbench Grid & Status Icons
# ==============================================================================
"""

import streamlit as st
import datetime
from utils.bootstrap import bootstrap_page, safe_db_execute

# 1. Page Initialization
supabase = bootstrap_page("Observations", "🔍")
st.title("🛡️ Observations")

# 2. State Initialization
if 'workbench_bins' not in st.session_state:
    st.session_state.workbench_bins = set()
if 'observed_this_session' not in st.session_state:
    st.session_state.observed_this_session = set()

# Handle Auto-Transition from Intake
if 'active_case_id' in st.session_state:
    # Pre-load all bins for the active case into the workbench
    case_bins = supabase.table('bin').select('bin_id').eq('mother_id', st.session_state.active_case_id).execute()
    for b in case_bins.data:
        st.session_state.workbench_bins.add(b['bin_id'])

# ------------------------------------------------------------------------------
# SIDEBAR: Supplemental Tools & Help
# ------------------------------------------------------------------------------
with st.sidebar:
    st.header("➕ Supplemental Tools")
    with st.expander("Add Bin to Existing Case"):
        all_mothers = supabase.table('mother').select('mother_id, mother_name').eq('is_deleted', False).order('created_at', desc=True).limit(20).execute()
        m_map = {m['mother_name']: m['mother_id'] for m in all_mothers.data}
        target_m = st.selectbox("Select Mother/Case", list(m_map.keys()), key="sup_m")
        new_bin_code = st.text_input("New Bin ID", placeholder="OB1-NAME-2")
        if st.button("Create Supplemental Bin"):
            def create_sup_bin():
                supabase.table('bin').insert({
                    "bin_id": new_bin_code,
                    "mother_id": m_map[target_m],
                    "session_id": st.session_state.session_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id
                }).execute()
                st.session_state.workbench_bins.add(new_bin_code)
                st.success(f"Bin {new_bin_code} added to Workbench.")
            safe_db_execute("Add Bin", create_sup_bin)

    with st.expander("Add Eggs to Existing Bin"):
        target_b = st.selectbox("Select Target Bin", list(st.session_state.workbench_bins), key="sup_b")
        egg_count = st.number_input("Eggs to Add", 1, 50, 1)
        egg_date = st.date_input("Egg Intake Date", key="sup_d")
        if st.button("Append Eggs"):
            def append_eggs():
                current = supabase.table('egg').select('egg_id', count='exact').eq('bin_id', target_b).execute()
                start_num = current.count + 1
                new_eggs = [{
                    "egg_id": f"{target_b}-E{i}",
                    "bin_id": target_b,
                    "intake_date": str(egg_date),
                    "session_id": st.session_state.session_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id
                } for i in range(start_num, start_num + egg_count)]
                supabase.table('egg').insert(new_eggs).execute()
                st.success(f"Added {egg_count} eggs to {target_b}.")
            safe_db_execute("Append Eggs", append_eggs)

# ------------------------------------------------------------------------------
# 1. THE WORKBENCH CONFIG & CORRECTION TOGGLE
# ------------------------------------------------------------------------------
# 🚨 CLINICAL CORRECTION MODE: Allows surgical removal of observations.
if 'correction_mode' not in st.session_state: st.session_state.correction_mode = False

col_h1, col_h2 = st.columns([2,1])
with col_h2:
    st.session_state.correction_mode = st.toggle("🛡️ Correction Mode", help="Switch to single-egg surgical edit/delete mode.")

st.caption("Active Workbench")

# Multi-select to "Load" bins into the session
available_bins = supabase.table('bin').select('bin_id').eq('is_deleted', False).execute()
bin_options = [b['bin_id'] for b in available_bins.data]
loaded_bins = st.multiselect("Load Bins to Session", bin_options, default=list(st.session_state.workbench_bins))
st.session_state.workbench_bins = set(loaded_bins)

if not st.session_state.workbench_bins:
    st.info("No bins loaded. Use the search bar above or perform an Intake to begin.")
    st.stop()

# Switcher with Status Icons
wb_status_list = []
for b_id in sorted(st.session_state.workbench_bins):
    # Calculate status in session
    eggs = supabase.table('egg').select('egg_id').eq('bin_id', b_id).eq('status', 'Active').execute().data
    obs = supabase.table('eggobservation').select('egg_id').eq('session_id', st.session_state.session_id).execute().data
    obs_ids = {o['egg_id'] for o in obs}
    
    done = sum(1 for e in eggs if e['egg_id'] in obs_ids)
    total = len(eggs)
    
    icon = "⚪"
    if done == total and total > 0: icon = "🟢"
    elif done > 0: icon = "🌓"
    wb_status_list.append(f"{icon} {b_id} ({done}/{total})")

active_wb_item = st.selectbox("Current Bin Focus", wb_status_list)
active_bin_id = active_wb_item.split(" ")[1]

# ------------------------------------------------------------------------------
# 2. HYDRATION GATE (Bypass in Correction Mode)
# ------------------------------------------------------------------------------
gate_key = f"env_gated_{active_bin_id}"
if gate_key not in st.session_state: st.session_state[gate_key] = False

# Skip hydration gate if exclusively in correction mode
if not st.session_state.correction_mode and not st.session_state[gate_key]:
    target_weight_res = supabase.table('bin').select('target_total_weight_g').eq('bin_id', active_bin_id).execute()
    target_weight = target_weight_res.data[0]['target_total_weight_g'] if target_weight_res.data else None

    with st.container(border=True):
        st.subheader("💧 Hydration Lock")
        st.write(f"Stabilize **{active_bin_id}** (Target: {target_weight or 'TBD'}g)")
        c1, c2 = st.columns(2)
        curr_w = c1.number_input("Current Weight (g)", 0.0, 5000.0, key="wt_gate")
        water_suggestion = max(0.0, target_weight - curr_w) if target_weight else 0.0
        c2.metric("Suggested Water (ml)", f"{water_suggestion:.1f}")
        water_add = c1.number_input("Actual Added (ml)", 0.0, 500.0, value=water_suggestion)
        if st.button("Unlock Grid", type="primary"):
            def unlock():
                if target_weight is None:
                    supabase.table('bin').update({"target_total_weight_g": curr_w}).eq('bin_id', active_bin_id).execute()
                supabase.table('incubatorobservation').insert({
                    "session_id": st.session_state.session_id,
                    "bin_id": active_bin_id,
                    "observer_id": st.session_state.observer_id,
                    "bin_weight_g": curr_w,
                    "water_added_ml": water_add
                }).execute()
                st.session_state[gate_key] = True
            safe_db_execute("Hydration", unlock)
            st.rerun()
    st.stop()

# ------------------------------------------------------------------------------
# 3. VISUAL EGG GRID & SELECTION
# ------------------------------------------------------------------------------
res_eggs = supabase.table('egg').select('*').eq('bin_id', active_bin_id).eq('status', 'Active').eq('is_deleted', False).order('egg_id').execute()
eggs_data = res_eggs.data

# Fetch session accomplishments (For Status Icons & Matrix Analysis)
obs_session = supabase.table('eggobservation').select('*').eq('bin_id', active_bin_id).eq('session_id', st.session_state.session_id).execute().data
observed_ids = {o['egg_id'] for o in obs_session}

def sort_key(e_id):
    try: return int(e_id.split('-E')[-1])
    except: return 0

# Grid Setup
egg_labels = []
for e in sorted(eggs_data, key=lambda x: sort_key(x['egg_id'])):
    id_num = e['egg_id'].split('-E')[-1]
    status = "✅" if e['egg_id'] in observed_ids else "⚪"
    egg_labels.append(f"{status} E{id_num}")

label_to_id = {f"{'✅' if e['egg_id'] in observed_ids else '⚪'} E{e['egg_id'].split('-E')[-1]}": e['egg_id'] for e in eggs_data}

if st.session_state.correction_mode:
    st.write("### 🥚 Biological Timeline (Surgical Mode)")
    st.warning("Tap ONE egg below to perform clinical data surgery.")
    selected_target = st.selectbox("Select Egg for Timeline", egg_labels)
    if selected_target:
        target_id = label_to_id[selected_target]
        st.write(f"#### Timeline: {target_id}")
        # Fetch ALL history for this egg
        history = supabase.table('eggobservation').select('*').eq('egg_id', target_id).order('timestamp', desc=True).execute().data
        if not history:
            st.info("No clinical history detected for this subject.")
        else:
            for h in history:
                with st.container(border=True):
                    ts = datetime.datetime.fromisoformat(h['timestamp']).strftime('%Y-%m-%d %H:%M')
                    st.write(f"**{ts}** | Stage: {h['stage_at_observation']} | Observer: {h['observer_id'] or 'Unknown'}")
                    cols = st.columns([4,1])
                    cols[0].caption(f"Props: Chalk {h['chalking']} | Vasc {h['vascularity']} | Mold {h['molding']} | Leak {h['leaking']}")
                    if cols[1].button("🗑️", key=f"del_{h['detail_id']}"):
                        def surgical_delete():
                            supabase.table('eggobservation').delete().eq('detail_id', h['detail_id']).execute()
                            # ROLLBACK LOGIC: Find next most recent to update egg current state
                            rem = supabase.table('eggobservation').select('stage_at_observation').eq('egg_id', target_id).order('timestamp', desc=True).limit(1).execute()
                            new_s = rem.data[0]['stage_at_observation'] if rem.data else "S0"
                            supabase.table('egg').update({"current_stage": new_s, "modified_by_id": st.session_state.observer_id}).eq('egg_id', target_id).execute()
                            st.success("Record purged. Egg state reverted.")
                        safe_db_execute("Surgical Delete", surgical_delete)
                        st.rerun()
else:
    st.write("### 🥚 Biological Grid")
    selected_labels = st.multiselect("Batch Triage (Tap to group):", egg_labels)
    selected_real_ids = [label_to_id[l] for l in selected_labels]

    # --------------------------------------------------------------------------
    # 4. ACTION TRAY (Inherited Property Matrix)
    # --------------------------------------------------------------------------
    if selected_real_ids:
        # INTERSECTION ANALYSIS (Solid/Mixed/Clear Logic)
        selected_eggs_state = [e for e in eggs_data if e['egg_id'] in selected_real_ids]
        
        stages_found = {e['current_stage'] for e in selected_eggs_state}
        matrix_stage = next(iter(stages_found)) if len(stages_found) == 1 else "MIXED"
        
        # CSV String for visual confirmation
        csv_ids = ",".join([r.split('-E')[-1] for r in selected_real_ids])
        
        with st.container(border=True):
            st.markdown(f"#### 📐 Property Matrix: `[{csv_ids}]`")
            ac1, ac2 = st.columns(2)
            
            stage_opts = ["S0","S1","S2","S3","S4","S5","S6"]
            st_idx = stage_opts.index(matrix_stage) if matrix_stage in stage_opts else 0
            new_stage = ac1.selectbox(f"{'✅' if matrix_stage != 'MIXED' else '➖'} Stage", stage_opts, index=st_idx)
            
            chalks_found = {o['chalking'] for o in obs_session if o['egg_id'] in selected_real_ids}
            matrix_chalk = next(iter(chalks_found)) if len(chalks_found) == 1 else 0
            new_chalk = ac2.selectbox(f"{'✅' if len(chalks_found) == 1 else '⚪'} Chalking", [0, 1, 2], index=matrix_chalk)
            
            st.write("**Cumulative Health Flags**")
            bc1, bc2, bc3 = st.columns(3)
            # Simplified for now, in a full enterprise app these would be 3-way checkboxes
            v = bc1.checkbox("Vascularity (+)")
            m = bc2.checkbox("Molding")
            l = bc3.checkbox("Leaking")
            
            if st.button("🚀 Push Batch Update", type="primary", use_container_width=True):
                def commit_batch():
                    m_id = supabase.table('bin').select('mother_id').eq('bin_id', active_bin_id).execute().data[0]['mother_id']
                    obs_payload = []
                    for rid in selected_real_ids:
                        obs_payload.append({
                            "session_id": st.session_state.session_id, "egg_id": rid, "bin_id": active_bin_id,
                            "observer_id": st.session_state.observer_id, "chalking": new_chalk, "vascularity": v,
                            "molding": m, "leaking": l, "stage_at_observation": new_stage
                        })
                        status = "Active" if new_stage != "S6" else "Transferred"
                        supabase.table('egg').update({"current_stage": new_stage, "status": status, "modified_by_id": st.session_state.observer_id}).eq('egg_id', rid).execute()
                    
                    supabase.table('eggobservation').insert(obs_payload).execute()
                    st.success(f"Finalized {len(selected_real_ids)} clinical signatures.")
                safe_db_execute("Prop Matrix Commit", commit_batch)
                st.rerun()

# ------------------------------------------------------------------------------
# 5. DIAGNOSTIC LOG (HIDDEN IN CORRECTION MODE)
# ------------------------------------------------------------------------------
if not st.session_state.correction_mode:
    with st.expander("📊 Live Session Audit"):
        logs = supabase.table('eggobservation').select('*').eq('session_id', st.session_state.session_id).order('timestamp', desc=True).execute().data
        for l in logs:
            st.write(f"[{l['timestamp'][11:16]}] **{l['egg_id']}** -> Stage {l['stage_at_observation']} ✅")


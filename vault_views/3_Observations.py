"""
=============================================================================
Module:        vault_views/3_Observations.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.bootstrap, utils.visuals
Inputs:        st.session_state (observer_id, session_id, workbench_bins)
Outputs:       bin_observation, egg_observation, egg, hatchling_ledger
Description:   Workbench Grid with Hardened Hydration Gate and Surgical Resurrection
               (soft-void observations, ISS-1); S6 hatchling ledger (ISS-3); RBAC (ISS-7).
=============================================================================
"""

import streamlit as st
import datetime
import uuid
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table, get_last_bin_weight
from utils.rbac import can_elevated_clinical_operations
from utils.visuals import render_egg_icon

# 1. Page Initialization
supabase = bootstrap_page("Egg Checks", "🔬")
st.title("🔬 Check on Eggs")

# 2. State Initialization
if 'workbench_bins' not in st.session_state:
    st.session_state.workbench_bins = set()
if 'observed_this_session' not in st.session_state:
    st.session_state.observed_this_session = set()

# Handle Auto-Transition from Intake
if 'active_case_id' in st.session_state:
    case_bins = supabase.table('bin').select('bin_id').eq('mother_id', st.session_state.active_case_id).execute()
    for b in case_bins.data:
        st.session_state.workbench_bins.add(b['bin_id'])

# ------------------------------------------------------------------------------
# SIDEBAR: Supplemental Tools & Help
# ------------------------------------------------------------------------------
with st.sidebar:
    st.header("🛠️ Extra Tools")
    with st.expander("Add a Bin to a Case"):
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
        b_last_w_data = get_last_bin_weight(target_b) if target_b else {"bin_weight_g": 0.0}
        b_last_w = b_last_w_data['bin_weight_g']
        
        st.write(f"**Current Context Mass:** `{b_last_w}g`" if b_last_w > 0 else "**Current Context:** New Bin")
        
        egg_count = st.number_input("Eggs to Add", 1, 50, 1)
        egg_date = st.date_input("Egg Intake Date", key="sup_d")
        new_target = st.number_input("New Post-Append Mass (g)", 0.0, 5000.0, help="Record the new total weight after stabilization.")
        
        if st.button("Append & Recalibrate"):
            def append_eggs():
                if new_target <= 0:
                    st.error("You must enter a valid new weight to recalibrate.")
                    return
                prev_bin = supabase.table('bin').select('bin_notes').eq('bin_id', target_b).execute().data[0]
                new_bin_note = f"{prev_bin.get('bin_notes', '')} | Append: {egg_count} new eggs added on {datetime.date.today().isoformat()}"
                supabase.table('bin').update({
                    "target_total_weight_g": new_target,
                    "bin_notes": new_bin_note,
                    "modified_by_id": st.session_state.observer_id
                }).eq('bin_id', target_b).execute()
                
                current = supabase.table('egg').select('egg_id', count='exact').eq('bin_id', target_b).execute()
                start_num = current.count + 1
                new_eggs = [{
                    "egg_id": f"{target_b}-E{i}", "bin_id": target_b, "intake_date": str(egg_date),
                    "egg_notes": "Supplemental Append",
                    "session_id": st.session_state.session_id, "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id
                } for i in range(start_num, start_num + egg_count)]
                egg_res = supabase.table('egg').insert(new_eggs).execute()
                
                obs_list = [{
                    "session_id": st.session_state.session_id,
                    "egg_id": e['egg_id'],
                    "bin_id": target_b,
                    "observer_id": st.session_state.observer_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id,
                    "stage_at_observation": "S0",
                    "observation_notes": "Supplemental Intake Baseline",
                    "is_deleted": False,
                } for e in egg_res.data]
                get_resilient_table(supabase, 'egg_observation').insert(obs_list).execute()
                
                get_resilient_table(supabase, 'bin_observation').insert({
                    "bin_observation_id": str(uuid.uuid4()),
                    "session_id": st.session_state.session_id, 
                    "bin_id": target_b, 
                    "observer_id": st.session_state.observer_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id,
                    "bin_weight_g": new_target,
                    "env_notes": f"Recalibration during append of {egg_count} eggs"
                }).execute()
                
                st.success(f"Recalibrated {target_b} at {new_target}g.")
                st.cache_resource.clear()
            audit_msg = f"Supplemental Append: Added {egg_count} eggs to Bin {target_b}. New context mass: {new_target}g."
            safe_db_execute("Append", append_eggs, success_message=audit_msg)
            st.rerun()

# ------------------------------------------------------------------------------
# 1. THE WORKBENCH CONFIG & SURGICAL RESURRECTION TOGGLE
# ------------------------------------------------------------------------------
if 'surgical_resurrection' not in st.session_state:
    st.session_state.surgical_resurrection = False

_col_h1, col_h2 = st.columns([2, 1])
with col_h2:
    if can_elevated_clinical_operations():
        st.session_state.surgical_resurrection = st.toggle(
            "🛠️ Correction Mode",
            help="Enable this to fix mistakes or undo accidental saves.",
        )
    else:
        st.session_state.surgical_resurrection = False
        st.caption("Admin only.")

st.caption("Bins being checked:")

# Select bins to work on
available_bins = supabase.table('bin').select('bin_id').eq('is_deleted', False).execute()
bin_options = sorted([b['bin_id'] for b in available_bins.data])
loaded_bins = st.multiselect("Select Bins to Check", bin_options, default=list(st.session_state.workbench_bins))
st.session_state.workbench_bins = set(loaded_bins)

if not st.session_state.workbench_bins:
    st.info("No bins loaded. Use the search bar above or perform an Intake to begin.")
    st.stop()

# Switcher with Status Icons
wb_status_list = []
for b_id in sorted(st.session_state.workbench_bins):
    eggs = supabase.table('egg').select('egg_id').eq('bin_id', b_id).eq('status', 'Active').eq('is_deleted', False).execute().data
    obs = (
        get_resilient_table(supabase, 'egg_observation')
        .select('egg_id')
        .eq('session_id', st.session_state.session_id)
        .eq('is_deleted', False)
        .execute()
        .data
    )
    observed_ids = {o['egg_id'] for o in obs}
    
    done = sum(1 for e in eggs if e['egg_id'] in observed_ids)
    total = len(eggs)
    
    icon = "⚪"
    if done == total and total > 0: icon = "🟢"
    elif done > 0: icon = "🌓"
    wb_status_list.append(f"{icon} {b_id} ({done}/{total})")

active_wb_item = st.selectbox("Current Bin Focus", wb_status_list)
active_bin_id = active_wb_item.split(" ")[1]

# ------------------------------------------------------------------------------
# 2. HYDRATION GATE (Bypass in Surgical Resurrection Mode)
# ------------------------------------------------------------------------------
# v8.0.0 Requirement: Grid restricted unless last bin_observation matches session_id
if 'env_gate_synced' not in st.session_state:
    st.session_state.env_gate_synced = {}

if not st.session_state.surgical_resurrection:
    # Check if this specific bin has been unlocked in the current session
    if not st.session_state.env_gate_synced.get(active_bin_id):
        # Double-check DB in case of page refresh/session resumption
        obs_result = supabase.table('bin_observation').select('session_id').eq('bin_id', active_bin_id).order('timestamp', desc=True).limit(1).execute()
        if obs_result.data and obs_result.data[0]['session_id'] == st.session_state.session_id:
            st.session_state.env_gate_synced[active_bin_id] = True
        else:
            st.session_state.env_gate_synced[active_bin_id] = False

    if not st.session_state.env_gate_synced.get(active_bin_id):
        last_weight_data = get_last_bin_weight(active_bin_id)
        last_weight = last_weight_data['bin_weight_g']

        with st.container(border=True):
            st.subheader("💧 Bin Weight Check")
            st.write(f"We need the current weight for **{active_bin_id}** before you check the eggs.")
            
            col_w1, col_w2 = st.columns(2)
            col_w1.metric("Last Recorded Weight", f"{last_weight}g" if last_weight > 0 else "New Bin")
            curr_w = col_w2.number_input("Current Total Mass (g)", 0.0, 5000.0, key="wt_gate", help="Biologist: Use your formula based on the delta from last weight.")
            
            water_add = st.number_input("Actual Water Added (ml)", 0.0, 500.0, help="Record the volume added based on your clinical assessment.")
            
            if st.button("START WORKING", type="primary"):
                def unlock():
                    get_resilient_table(supabase, 'bin_observation').insert({
                        "bin_observation_id": str(uuid.uuid4()),
                        "session_id": st.session_state.session_id,
                        "bin_id": active_bin_id,
                        "observer_id": st.session_state.observer_id,
                        "created_by_id": st.session_state.observer_id,
                        "modified_by_id": st.session_state.observer_id,
                        "bin_weight_g": curr_w,
                        "water_added_ml": water_add,
                        "env_notes": "Gated weight check"
                    }).execute()
                    supabase.table('bin').update({"target_total_weight_g": curr_w}).eq('bin_id', active_bin_id).execute()
                    st.session_state.env_gate_synced[active_bin_id] = True
                    st.cache_resource.clear()
                audit_msg = f"Environment Check: Bin {active_bin_id} mass recorded at {curr_w}g. Water added: {water_add}ml."
                safe_db_execute("Hydration", unlock, success_message=audit_msg)
                st.rerun()
        st.stop()

# ------------------------------------------------------------------------------
# 3. VISUAL EGG GRID & SELECTION
# ------------------------------------------------------------------------------
res_eggs = supabase.table('egg').select('*').eq('bin_id', active_bin_id).eq('status', 'Active').eq('is_deleted', False).order('egg_id').execute()
eggs_data = res_eggs.data

obs_session = (
    get_resilient_table(supabase, 'egg_observation')
    .select('*')
    .eq('bin_id', active_bin_id)
    .eq('session_id', st.session_state.session_id)
    .eq('is_deleted', False)
    .execute()
    .data
)
observed_ids = {o['egg_id'] for o in obs_session}

def sort_key(e_id):
    try: return int(e_id.split('-E')[-1])
    except: return 0

if st.session_state.surgical_resurrection:
    st.write("### 🥚 Biological Timeline (Surgical Mode)")
    st.warning(
        "Search for ANY egg below (including Transferred/Dead) to void individual "
        "observation rows (soft delete). Egg stage rolls back to the latest remaining observation."
    )

    repair_eggs = supabase.table('egg').select('egg_id').eq('bin_id', active_bin_id).execute().data
    repair_labels = [f"🔍 {e['egg_id']}" for e in repair_eggs]

    selected_target = st.selectbox("Select Egg for Surgery", repair_labels)
    void_reason_input = st.text_input(
        "Void reason (audit)",
        placeholder="e.g. duplicate entry, wrong stage selected",
        key="surgical_void_reason",
    )
    if selected_target:
        target_id = selected_target.replace("🔍 ", "")
        st.write(f"#### Timeline: {target_id}")
        history_active = (
            get_resilient_table(supabase, 'egg_observation')
            .select('*')
            .eq('egg_id', target_id)
            .eq('is_deleted', False)
            .order('timestamp', desc=True)
            .execute()
            .data
        )
        history_voided = (
            get_resilient_table(supabase, 'egg_observation')
            .select('*')
            .eq('egg_id', target_id)
            .eq('is_deleted', True)
            .order('timestamp', desc=True)
            .execute()
            .data
        )
        if not history_active and not history_voided:
            st.info("No clinical history detected for this subject.")
        else:
            for h in history_active:
                with st.container(border=True):
                    ts = datetime.datetime.fromisoformat(str(h['timestamp']).replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                    st.write(f"**{ts}** | Stage: {h['stage_at_observation']} | Observer: {h['observer_id'] or 'Unknown'}")
                    cols = st.columns([4, 1])
                    cols[0].caption(
                        f"Props: Chalk {h['chalking']} | Vasc {h['vascularity']} | "
                        f"Mold {h['molding']} | Leak {h['leaking']}"
                    )
                    if cols[1].button("Void", key=f"void_{h['egg_observation_id']}"):
                        def surgical_void():
                            reason = (void_reason_input or "").strip() or "No reason supplied"
                            get_resilient_table(supabase, 'egg_observation').update({
                                "is_deleted": True,
                                "void_reason": reason,
                                "modified_by_id": st.session_state.observer_id,
                            }).eq('egg_observation_id', h['egg_observation_id']).execute()
                            rem = (
                                get_resilient_table(supabase, 'egg_observation')
                                .select('stage_at_observation')
                                .eq('egg_id', target_id)
                                .eq('is_deleted', False)
                                .order('timestamp', desc=True)
                                .limit(1)
                                .execute()
                            )
                            new_s = rem.data[0]['stage_at_observation'] if rem.data else "S0"
                            new_status = "Active" if new_s != "S6" else "Transferred"

                            supabase.table('egg').update({
                                "current_stage": new_s,
                                "status": new_status,
                                "modified_by_id": st.session_state.observer_id,
                            }).eq('egg_id', target_id).execute()

                            if new_s != "S6":
                                # Rollback from S hatchling requires voiding ledger entries
                                supabase.table("hatchling_ledger").update({
                                    "is_deleted": True,
                                    "notes": f"Voided via surgery {datetime.date.today().isoformat()}",
                                    "modified_by_id": st.session_state.observer_id,
                                }).eq("egg_id", target_id).execute()

                            st.success(f"Observation voided. Egg {target_id} reverted to {new_s} ({new_status}).")

                        audit_msg = f"Surgical void: egg_observation_id={h['egg_observation_id']} egg={target_id} reason={void_reason_input or 'n/a'}"
                        safe_db_execute("Surgical Void", surgical_void, success_message=audit_msg)
                        st.rerun()
            if history_voided:
                with st.expander("Voided observations (audit trail)"):
                    for h in history_voided:
                        ts = datetime.datetime.fromisoformat(str(h['timestamp']).replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                        st.caption(
                            f"{ts} | stage {h.get('stage_at_observation')} | "
                            f"reason: {h.get('void_reason') or '—'}"
                        )
else:
    # ------------------------------------------------------------------------------
    # 4. THE BIOLOGICAL GRID
    # ------------------------------------------------------------------------------
    st.markdown("### 🥚 Biological Grid")
    st.write(f"Showing **{len(eggs_data)}** subjects in **{active_bin_id}**")

    if st.button("🏁 Select All Pending"):
        st.session_state.selected_eggs = [e['egg_id'] for e in eggs_data if e['egg_id'] not in observed_ids]
        st.rerun()

    cols_per_row = 4
    rows = [eggs_data[i:i + cols_per_row] for i in range(0, len(eggs_data), cols_per_row)]

    for row in rows:
        grid_cols = st.columns(cols_per_row)
        for idx, egg in enumerate(row):
            eid = egg['egg_id']
            is_selected = eid in st.session_state.get("selected_eggs", [])
            is_done = eid in observed_ids
            
            img_data = render_egg_icon(
                egg['current_stage'], 
                egg.get('last_chalk', 0), 
                egg.get('last_vasc', False), 
                egg['status'],
                is_selected
            )
            
            with grid_cols[idx]:
                label_text = f"**{eid.split('-E' if '-E' in eid else 'Egg')[-1]}**"
                if is_done: label_text = "✅ " + label_text
                
                # Render the High-Contrast Tray
                st.markdown(f"""
                <div class="egg-tray">
                    <img src="{img_data}" width="70">
                    <br>
                </div>
                """, unsafe_allow_html=True)
                
                if st.checkbox(label_text, key=f"cb_{eid}", value=is_selected):
                    if 'selected_eggs' not in st.session_state: st.session_state.selected_eggs = []
                    if eid not in st.session_state.selected_eggs:
                        st.session_state.selected_eggs.append(eid)
                        st.rerun()
                else:
                    if 'selected_eggs' in st.session_state and eid in st.session_state.selected_eggs:
                        st.session_state.selected_eggs.remove(eid)
                        st.rerun()

    selected_real_ids = st.session_state.get("selected_eggs", [])

    if selected_real_ids:
        selected_eggs_state = [e for e in eggs_data if e['egg_id'] in selected_real_ids]
        stages_found = {e['current_stage'] for e in selected_eggs_state}
        matrix_stage = next(iter(stages_found)) if len(stages_found) == 1 else "MIXED"
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
            v = bc1.checkbox("Vascularity (+)")
            m = bc2.checkbox("Molding")
            l = bc3.checkbox("Leaking")
            
            egg_meta_notes = st.text_input("Permanent Egg Notes", placeholder="e.g., 'Slightly cracked'")
            observation_notes = st.text_area("Shift Observation Notes", placeholder="Describe unusual observations...")
            
            if st.button("SAVE", type="primary", use_container_width=True):
                def commit_batch():
                    obs_payload = []
                    for rid in selected_real_ids:
                        obs_payload.append({
                            "session_id": st.session_state.session_id,
                            "egg_id": rid,
                            "bin_id": active_bin_id,
                            "observer_id": st.session_state.observer_id,
                            "created_by_id": st.session_state.observer_id,
                            "modified_by_id": st.session_state.observer_id,
                            "chalking": new_chalk,
                            "vascularity": v,
                            "molding": m,
                            "leaking": l,
                            "stage_at_observation": new_stage,
                            "observation_notes": observation_notes,
                            "is_deleted": False,
                        })

                    status_val = "Active" if new_stage != "S6" else "Transferred"
                    update_fields = {
                        "current_stage": new_stage,
                        "status": status_val,
                        "last_chalk": new_chalk,
                        "last_vasc": v,
                        "modified_by_id": st.session_state.observer_id,
                    }
                    if egg_meta_notes:
                        update_fields["egg_notes"] = egg_meta_notes

                    supabase.table('egg').update(update_fields).in_('egg_id', selected_real_ids).execute()
                    get_resilient_table(supabase, 'egg_observation').insert(obs_payload).execute()

                    if new_stage == "S6":
                        hatch_date = datetime.date.today()
                        vitality = (observation_notes or "").strip() or "pending_field_assessment"
                        for rid in selected_real_ids:
                            egg_one = (
                                supabase.table('egg')
                                .select("egg_id, bin_id, intake_timestamp")
                                .eq("egg_id", rid)
                                .execute()
                            )
                            if not egg_one.data:
                                continue
                            erow = egg_one.data[0]
                            bin_one = (
                                supabase.table("bin")
                                .select("mother_id")
                                .eq("bin_id", erow["bin_id"])
                                .execute()
                            )
                            if not bin_one.data:
                                continue
                            mother_id = bin_one.data[0]["mother_id"]
                            incub_days = None
                            id_raw = erow.get("intake_timestamp")
                            if id_raw:
                                try:
                                    # Handle string or datetime object
                                    dt_val = datetime.datetime.fromisoformat(str(id_raw).replace('Z', '+00:00'))
                                    incub_days = (hatch_date - dt_val.date()).days
                                except (ValueError, TypeError):
                                    incub_days = None
                            hl_existing = (
                                supabase.table("hatchling_ledger")
                                .select("hatchling_ledger_id")
                                .eq("egg_id", rid)
                                .execute()
                            )
                            hl_row = {
                                "egg_id": rid,
                                "mother_id": mother_id,
                                "hatch_date": str(hatch_date),
                                "vitality_score": vitality[:500],
                                "incubation_duration_days": incub_days,
                                "notes": "Auto-recorded on S6 batch transition",
                                "session_id": st.session_state.session_id,
                                "created_by_id": st.session_state.observer_id,
                                "modified_by_id": st.session_state.observer_id,
                            }
                            if hl_existing.data:
                                hid = hl_existing.data[0]["hatchling_ledger_id"]
                                supabase.table("hatchling_ledger").update({
                                    "hatch_date": str(hatch_date),
                                    "vitality_score": vitality[:500],
                                    "incubation_duration_days": incub_days,
                                    "modified_by_id": st.session_state.observer_id,
                                }).eq("hatchling_ledger_id", hid).execute()
                            else:
                                supabase.table("hatchling_ledger").insert(hl_row).execute()

                    st.success(f"Finalized {len(selected_real_ids)} clinical signatures.")
                audit_msg = f"Batch Commit: {len(selected_real_ids)} eggs in Bin {active_bin_id} at Stage {new_stage}."
                safe_db_execute("Prop Matrix Commit", commit_batch, success_message=audit_msg)
                st.rerun()

# ------------------------------------------------------------------------------
# 5. DIAGNOSTIC LOG
# ------------------------------------------------------------------------------
if not st.session_state.surgical_resurrection:
    with st.expander("📊 Live Session Audit"):
        logs = (
            get_resilient_table(supabase, 'egg_observation')
            .select('*')
            .eq('session_id', st.session_state.session_id)
            .eq('is_deleted', False)
            .order('timestamp', desc=True)
            .execute()
            .data
        )
        for l in logs:
            st.write(f"[{l['timestamp'][11:16]}] **{l['egg_id']}** -> Stage {l['stage_at_observation']} ✅")

"""
=============================================================================
Module:        vault_views/3_Observations.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap, utils.visuals
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, session_id, workbench_bins)
Outputs:       bin_observation, egg_observation, egg, hatchling_ledger
Description:   Workbench Grid with Hardened Hydration Gate and Surgical Resurrection
               (soft-void observations, ISS-1); S6 hatchling ledger (ISS-3); RBAC (ISS-7).
=============================================================================
"""

import streamlit as st

if "is_submitting" not in st.session_state:
    st.session_state.is_submitting = False
import datetime
import uuid
from utils.bootstrap import (
    bootstrap_page,
    safe_db_execute,
    get_resilient_table,
    get_last_bin_weight,
)
from utils.rbac import can_elevated_clinical_operations
from utils.performance import track_view_performance
from utils.visuals import render_egg_icon

with track_view_performance("Observations"):
    # 1. Page Initialization
    supabase = bootstrap_page("Observations", "🔬")
    st.title("🔬 Observations")

    # 2. State Initialization
    if "workbench_bins" not in st.session_state:
        st.session_state.workbench_bins = set()
    if "observed_this_session" not in st.session_state:
        st.session_state.observed_this_session = set()
    if "surgical_resurrection" not in st.session_state:
        st.session_state.surgical_resurrection = False
    # CR-20260430-194500: Removed sup_bin_mode state init (migrated to intake screen)

    # Handle Auto-Transition from Intake
    if "active_case_id" in st.session_state:
        case_bins = (
            supabase.table("bin")
            .select("bin_id")
            .eq("intake_id", st.session_state.active_case_id)
            .execute()
        )
        for b in case_bins.data:
            st.session_state.workbench_bins.add(b["bin_id"])

    # CR-20260430-194500: Removed supplemental tools sidebar (migrated to intake screen)

    # [Correction Mode Toggle now at bottom of Header block for visibility]

    _col_h1, col_h2 = st.columns([2, 1])
    with col_h2:
        st.session_state.surgical_resurrection = st.toggle(
            "🛠️ Correction Mode",
            value=st.session_state.surgical_resurrection,
            help="Enable this to fix mistakes or undo accidental saves.",
        )

    # --- 2. THE FOCUS SELECTBOX (§35.5) ---
    available_bins = (
        supabase.table("bin").select("bin_id, bin_code").eq("is_deleted", False).execute()  # CR-20260501-1800: Added bin_code for display
    )
    bin_options = sorted([b["bin_id"] for b in available_bins.data if b["bin_id"]])
    # CR-20260501-1800: Build bin_code lookup map for display purposes
    bin_code_map = {b["bin_id"]: b.get("bin_code", str(b["bin_id"])) for b in available_bins.data if b["bin_id"]}

    # Pre-calculate stats for icons
    # CR-20260426 Lo-4: Wrap per-bin query in try/except.
    # A bin ID containing invalid chars (e.g. '/' in legacy records like Snapper_Val_0/16)
    # breaks the Supabase REST URL path and returns a non-data object, causing AttributeError.
    bin_stats = {}
    for b_id in bin_options:
        try:
            eggs = supabase.table("egg").select("egg_id").eq("bin_id", b_id).eq("is_deleted", False).execute().data
            obs = supabase.table("egg_observation").select("egg_id").in_("egg_id", [e["egg_id"] for e in eggs]).eq("session_id", st.session_state.session_id).execute().data if eggs else []
            obs_ids = {o["egg_id"] for o in obs}
            done = sum(1 for e in eggs if e["egg_id"] in obs_ids)
            bin_stats[b_id] = {"done": done, "total": len(eggs)}
        except Exception:
            bin_stats[b_id] = {"done": 0, "total": 0}

    def get_bin_display_label(b_id):
        stats = bin_stats.get(b_id, {"done": 0, "total": 0})
        total = stats["total"]
        done = stats["done"]
        if total == 0: icon = "⚪"
        elif total == done: icon = "✅"
        else: icon = "🌓"
        # CR-20260501-1800: Display bin_code (text) instead of raw bin_id (now BIGINT)
        display_code = bin_code_map.get(b_id, str(b_id))
        return f"{icon} {display_code} ({done}/{total})"

    # Multiselect with raw IDs
    bin_ids_in_db = set(bin_stats.keys())
    valid_defaults = [b for b in st.session_state.workbench_bins if b and b in bin_ids_in_db]
    
    st.session_state.workbench_bins = st.multiselect(
        "Observation Workbench",
        options=bin_options,
        default=valid_defaults,
        format_func=get_bin_display_label,
        key="obs_workbench",
        help="Added bins from Intake appear here automatically."
    )

    # --- 2. THE FOCUS SELECTBOX (§35.5) ---
    focus_options = sorted(list(st.session_state.workbench_bins))
    
    if not focus_options:
        st.info("No bins loaded. Use the search bar above or perform an Intake to begin.")
        st.stop()
    
    # B-008: Focus on the raw ID while showing the decorated label
    active_focus_index = 0
    if st.session_state.get("active_bin_id") in focus_options:
        active_focus_index = focus_options.index(st.session_state.active_bin_id)

    active_bin_id = st.selectbox(
        "Current Bin Focus", 
        focus_options, 
        index=active_focus_index,
        format_func=get_bin_display_label,
        key="Current Bin Focus",
        help="Switch between selected bins to record observations."
    )

    # Finding 6: Reset Correction Mode if Bin changes
    if "last_active_bin_id" not in st.session_state:
        st.session_state.last_active_bin_id = active_bin_id
    
    if st.session_state.last_active_bin_id != active_bin_id:
        st.session_state.surgical_resurrection = False
        st.session_state.last_active_bin_id = active_bin_id

    # CR-20260430-194500: Removed supplemental tools sidebar (migrated to intake screen)

    # ------------------------------------------------------------------------------
    # 3. HYDRATION GATE (Bypass in Surgical Resurrection Mode)
    # ------------------------------------------------------------------------------
    if "env_gate_synced" not in st.session_state:
        st.session_state.env_gate_synced = {}

    if not st.session_state.surgical_resurrection:
        # Check if this specific bin has been unlocked in the current session
        if not st.session_state.env_gate_synced.get(active_bin_id):
            # Double-check DB in case of page refresh/session resumption
            obs_result = (
                supabase.table("bin_observation")
                .select("session_id")
                .eq("bin_id", active_bin_id)
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )
            if (
                obs_result.data
                and obs_result.data[0]["session_id"] == st.session_state.session_id
            ):
                st.session_state.env_gate_synced[active_bin_id] = True
            else:
                st.session_state.env_gate_synced[active_bin_id] = False

        if not st.session_state.env_gate_synced.get(active_bin_id):
            last_weight_data = get_last_bin_weight(active_bin_id)
            last_weight = last_weight_data["bin_weight_g"]

            with st.container(border=True):
                st.subheader("💧 Bin Weight Check")
                st.warning("⚠️ **BIOLOGICAL ALERT: NEVER ROTATE EGGS.**\nMaintain exact original top-orientation during weighing and candling. Embryos will drown if turned.", icon="🛑")
                st.write(
                    f"We need the current weight for **{bin_code_map.get(active_bin_id, str(active_bin_id))}** before you check the eggs."  # CR-20260501-1800: Display bin_code instead of raw bin_id
                )

                col_w1, col_w2 = st.columns(2)
                col_w1.metric(
                    "Last Recorded Weight",
                    f"{last_weight}g" if last_weight > 0 else "New Bin",
                )
                curr_w = col_w2.number_input(
                    "Current Total Mass (g)",
                    0.0,
                    5000.0,
                    key="wt_gate",
                    help="Biologist: Use your formula based on the delta from last weight.",
                )

                water_add = st.number_input(
                    "Actual Water Added (ml)",
                    0.0,
                    500.0,
                    help="Record the volume added based on your clinical assessment.",
                )

                # CR-20260429: Temperature recording in Fahrenheit
                obs_temp = st.number_input(
                    "Incubator Temp (°F)",
                    60.0,
                    113.0,
                    value=82.0,
                    format="%.1f",
                    key="obs_temp",
                    help="Record the measured temperature inside the incubator.",
                )

                st.info("💡 **Clinical Requirement**: Record weights then press **SAVE** to unlock the observation grid.")
                if st.button("SAVE", type="primary", use_container_width=True, key="obs_env_save", help="Record weights and unlock the Egg Observation grid"):

                    def unlock():
                        get_resilient_table(supabase, "bin_observation").insert(
                            {
                                "bin_observation_id": str(uuid.uuid4()),
                                "session_id": st.session_state.session_id,
                                "bin_id": active_bin_id,
                                "observer_name": st.session_state.observer_name,
                                "created_by_id": st.session_state.observer_id,
                                "modified_by_id": st.session_state.observer_id,
                                "bin_weight_g": curr_w,
                                "water_added_ml": water_add,
                                "incubator_temp_f": obs_temp,  # CR-20260430-194500: Renamed column per schema migration
                                "env_notes": "Gated weight check",
                            }
                        ).execute()
                        supabase.table("bin").update({"target_total_weight_g": curr_w}).eq(
                            "bin_id", active_bin_id
                        ).execute()
                        st.session_state.env_gate_synced[active_bin_id] = True
                        st.cache_resource.clear()

                    audit_msg = f"Environment Check: Bin {bin_code_map.get(active_bin_id, str(active_bin_id))} mass recorded at {curr_w}g. Water added: {water_add}ml."  # CR-20260501-1800: Display bin_code
                    safe_db_execute("Hydration", unlock, success_message=audit_msg)
                    st.rerun()
            st.stop()

    # ------------------------------------------------------------------------------
    # 3. VISUAL EGG GRID & SELECTION
    # ------------------------------------------------------------------------------
    try:
        res_eggs = (
            supabase.table("egg")
            .select("*")
            .eq("bin_id", active_bin_id)
            .eq("status", "Active")
            .eq("is_deleted", False)
            .order("egg_id")
            .execute()
        )
        eggs_data = res_eggs.data
    except Exception:
        st.error("This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs.")
        st.stop()

    obs_session = (
        get_resilient_table(supabase, "egg_observation")
        .select("*")
        .eq("bin_id", active_bin_id)
        .eq("session_id", st.session_state.session_id)
        .eq("is_deleted", False)
        .execute()
        .data
    )
    observed_ids = {o["egg_id"] for o in obs_session}


    def sort_key(e_id):
        try:
            return int(e_id.split("-E")[-1])
        except:
            return 0


    if st.session_state.surgical_resurrection:
        st.write("### 🥚 Biological Timeline (Surgical Mode)")
        st.warning(
            "Search for ANY egg below (including Transferred/Dead) to void individual "
            "observation rows (soft delete). Egg stage rolls back to the latest remaining observation."
        )

        repair_eggs = (
            supabase.table("egg")
            .select("egg_id")
            .eq("bin_id", active_bin_id)
            .execute()
            .data
        )
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
                get_resilient_table(supabase, "egg_observation")
                .select("*")
                .eq("egg_id", target_id)
                .eq("is_deleted", False)
                .order("timestamp", desc=True)
                .execute()
                .data
            )
            history_voided = (
                get_resilient_table(supabase, "egg_observation")
                .select("*")
                .eq("egg_id", target_id)
                .eq("is_deleted", True)
                .order("timestamp", desc=True)
                .execute()
                .data
            )
            if not history_active and not history_voided:
                st.info("No clinical history detected for this subject.")
            else:
                # Display Active Observations
                for h in history_active:
                    with st.container(border=True):
                        ts = (
                            datetime.datetime.fromisoformat(
                                str(h["timestamp"]).replace("Z", "+00:00")
                            ).strftime("%m/%d/%Y %H:%M")
                        )
                        st.write(
                            f"**{ts}** | Stage: {h.get('stage_at_observation', 'N/A')} | Observer: {h.get('observer_id', 'Unknown')}"
                        )
                        cols = st.columns([4, 1])
                        cols[0].caption(
                            f"Props: Chalk {h.get('chalking', 0)} | Vasc {h.get('vascularity', False)} | "
                            f"Mold {h.get('molding', 0)} | Leak {h.get('leaking', 0)}"
                        )
                        # §4.2: LIFO Rollback Gate
                        is_latest = (h["egg_observation_id"] == history_active[0]["egg_observation_id"])
                        if cols[1].button("🗑️", key=f"void_{h['egg_observation_id']}", disabled=not is_latest):

                            def surgical_void():
                                reason = (
                                    void_reason_input or ""
                                ).strip() or "No reason supplied"
                                get_resilient_table(supabase, "egg_observation").update(
                                    {
                                        "is_deleted": True,
                                        "void_reason": reason,
                                        "modified_by_id": st.session_state.observer_id,
                                    }
                                ).eq(
                                    "egg_observation_id", h["egg_observation_id"]
                                ).execute()
                                
                                # Standard §35: Forensic Audit Log
                                # Standard §35: Forensic Audit Log
                                try:
                                    get_resilient_table(supabase, "system_log").insert({
                                        "session_id": st.session_state.session_id,
                                        "event_type": "VOID",
                                        "event_message": f"Record voided: Observation {h['egg_observation_id']} — Reason: {reason}",
                                        "observer_id": st.session_state.observer_id
                                    }).execute()
                                except: pass
                                
                                # Rollback state calculation
                                rem = (
                                    get_resilient_table(supabase, "egg_observation")
                                    .select("stage_at_observation")
                                    .eq("egg_id", target_id)
                                    .eq("is_deleted", False)
                                    .order("timestamp", desc=True)
                                    .limit(1)
                                    .execute()
                                )
                                new_s = (
                                    rem.data[0]["stage_at_observation"]
                                    if rem.data
                                    else "S1"
                                )
                                new_status = "Active" if new_s != "S6" else "Transferred"

                                supabase.table("egg").update(
                                    {
                                        "current_stage": new_s,
                                        "status": new_status,
                                        "modified_by_id": st.session_state.observer_id,
                                    }
                                ).eq("egg_id", target_id).execute()

                                if new_s != "S6":
                                    # Rollback from S6 (Hatched) requires voiding ledger entries Standard ISS-3
                                    try:
                                        supabase.table("hatchling_ledger").update(
                                            {
                                                "is_deleted": True,
                                                "notes": f"Voided via clinical surgery {datetime.date.today().isoformat()}",
                                                "modified_by_id": st.session_state.observer_id,
                                            }
                                        ).eq("egg_id", target_id).execute()
                                        
                                        get_resilient_table(supabase, "system_log").insert({
                                            "session_id": st.session_state.session_id,
                                            "event_type": "ROLLBACK",
                                            "event_message": f"State reverted: Subject {target_id} — Hatched status reversed, ledger entries voided",
                                            "observer_id": st.session_state.observer_id
                                        }).execute()
                                    except Exception as rollback_err:
                                        logger.error(f"S6 Ledger Rollback failed: {rollback_err}")

                                st.success(f"Observation voided. Egg {target_id} reverted to {new_s}.")
                                st.rerun()

                            safe_db_execute("Void Observation", surgical_void)

                # §6.1 Surgical Resurrection: Display Voided Observations
                if history_voided:
                    st.divider()
                    st.write("🗑️ **Voided Observations (Resurrection Eligible)**")
                    for hv in history_voided:
                        with st.container(border=True):
                            ts_v = (
                                datetime.datetime.fromisoformat(
                                    str(hv["timestamp"]).replace("Z", "+00:00")
                                ).strftime("%m/%d/%Y %H:%M")
                            )
                            st.write(
                                f"**{ts_v}** | Stage: {hv.get('stage_at_observation', 'N/A')} | Voided: {hv.get('void_reason', 'N/A')}"
                            )
                            if st.button("RESTORE", key=f"res_{hv['egg_observation_id']}", type="primary"):
                                def resurrect():
                                    get_resilient_table(supabase, "egg_observation").update(
                                        {"is_deleted": False, "modified_by_id": st.session_state.observer_id}
                                    ).eq("egg_observation_id", hv["egg_observation_id"]).execute()
                                    
                                    # Log resurrection
                                    try:
                                        get_resilient_table(supabase, "system_log").insert({
                                            "session_id": st.session_state.session_id,
                                            "event_type": "RESTORE",
                                            "event_message": f"Record restored: Observation {hv['egg_observation_id']}",
                                            "observer_id": st.session_state.observer_id
                                        }).execute()
                                    except: pass
                                    
                                    st.success(f"Observation {hv['egg_observation_id']} resurrected.")
                                    st.rerun()
                                
                                safe_db_execute("Resurrection", resurrect)
    else:
        # ------------------------------------------------------------------------------
        # 4. THE BIOLOGICAL GRID
        # ------------------------------------------------------------------------------
        st.markdown("### 🥚 Biological Grid")
        st.write(f"Showing **{len(eggs_data)}** subjects in **{bin_code_map.get(active_bin_id, str(active_bin_id))}**")  # CR-20260501-1800: Display bin_code

        if st.button("START", help="Select All Pending", key="obs_start_all"):
            st.session_state.selected_eggs = [
                e["egg_id"] for e in eggs_data if e["egg_id"] not in observed_ids
            ]
            st.rerun()

        cols_per_row = 4
        rows = [
            eggs_data[i : i + cols_per_row] for i in range(0, len(eggs_data), cols_per_row)
        ]

        for row in rows:
            grid_cols = st.columns(cols_per_row)
            for idx, egg in enumerate(row):
                eid = egg["egg_id"]
                is_selected = eid in st.session_state.get("selected_eggs", [])
                is_done = eid in observed_ids

                img_data = render_egg_icon(
                    egg["current_stage"],
                    egg.get("last_chalk", 0),
                    egg.get("last_vasc", False),
                    egg["status"],
                    is_selected,
                )

                with grid_cols[idx]:
                    label_text = f"**{eid.split('-E' if '-E' in eid else 'Egg')[-1]}**"
                    if is_done:
                        label_text = "✅ " + label_text

                    # Render the High-Contrast Tray
                    st.markdown(
                        f"""
                    <div class="egg-tray">
                        <img src="{img_data}" width="70">
                        <br>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    if st.checkbox(label_text, key=f"cb_{eid}", value=is_selected):
                        if "selected_eggs" not in st.session_state:
                            st.session_state.selected_eggs = []
                        if eid not in st.session_state.selected_eggs:
                            st.session_state.selected_eggs.append(eid)
                            st.rerun()
                    else:
                        if (
                            "selected_eggs" in st.session_state
                            and eid in st.session_state.selected_eggs
                        ):
                            st.session_state.selected_eggs.remove(eid)
                            st.rerun()

        selected_real_ids = st.session_state.get("selected_eggs", [])

        if selected_real_ids:
            selected_eggs_state = [e for e in eggs_data if e["egg_id"] in selected_real_ids]
            stages_found = {e["current_stage"] for e in selected_eggs_state}
            matrix_stage = next(iter(stages_found)) if len(stages_found) == 1 else "MIXED"
            csv_ids = ",".join([r.split("-E")[-1] for r in selected_real_ids])

            with st.container(border=True):
                st.markdown(f"#### 📐 Property Matrix: `[{csv_ids}]`")
                ac1, ac2 = st.columns(2)

                # §3.1 Biological Progression Validation
                stage_opts = ["S1", "S2", "S3S", "S3M", "S3J", "S4", "S5", "S6"]
                st_idx = stage_opts.index(matrix_stage) if matrix_stage in stage_opts else 0
                new_stage = ac1.selectbox(
                    f"{'✅' if matrix_stage != 'MIXED' else '➖'} Stage",
                    stage_opts,
                    index=st_idx,
                    key="matrix_stage",
                )

                # Validation Gate: Within 1 Step Check
                if (
                    matrix_stage != "MIXED" 
                    and not st.session_state.surgical_resurrection
                    and matrix_stage in stage_opts
                ):
                    curr_idx = stage_opts.index(matrix_stage)
                    next_idx = stage_opts.index(new_stage)
                    if abs(next_idx - curr_idx) > 1:
                        ac1.warning(
                            f"⚠️ Unusual biological jump: {matrix_stage} → {new_stage}. "
                            "Ensure this is medically intended."
                        )

                # §3.5 Expansion: Status Selection (Active, Transferred, Dead)
                # Mixed status logic
                stat_opts = ["Active", "Transferred", "Dead"]
                stats_found = {e["status"] for e in selected_eggs_state}
                matrix_stat = next(iter(stats_found)) if len(stats_found) == 1 else "Active"
                stat_idx = stat_opts.index(matrix_stat) if matrix_stat in stat_opts else 0
                new_status = ac1.selectbox(
                    f"{'✅' if len(stats_found) == 1 else '➖'} Status",
                    stat_opts,
                    index=stat_idx,
                    key="matrix_status",
                    help="Mark as Dead to remove from active grid and log mortality."
                )

                chalks_found = {
                    o["chalking"] for o in obs_session if o["egg_id"] in selected_real_ids
                }
                matrix_chalk = next(iter(chalks_found)) if len(chalks_found) == 1 else 0
                chalking_map = {0: "None", 1: "Small", 2: "Medium", 3: "Major"}
                new_chalk_label = ac2.selectbox(
                    f"{'✅' if len(chalks_found) == 1 else '⚪'} Chalking",
                    options=list(chalking_map.values()),
                    index=matrix_chalk if matrix_chalk <= 3 else 0,
                    key="matrix_chalking",
                )
                new_chalk = next(k for k, v in chalking_map.items() if v == new_chalk_label)

                st.write("**Clinical Health Scales (0-3)**")
                bc1, bc2, bc3, bc4 = st.columns(4)
                auto_vasc = bool(new_stage and new_stage.startswith("S3"))
                v = bc1.checkbox("Vascularity (+)", value=auto_vasc, disabled=auto_vasc)
                m_val = bc2.selectbox(
                    "Molding",
                    [0, 1, 2, 3],
                    key="matrix_molding",
                    help="0:None, 1:Spotting, 2:Patchy, 3:Aggressive",
                )
                l_val = bc3.selectbox(
                    "Leaking", [0, 1, 2, 3], key="matrix_leaking", help="0:None, 1:Damp, 2:Active, 3:Ruptured"
                )
                d_val = bc4.selectbox(
                    "Denting",
                    [0, 1, 2, 3],
                    key="matrix_denting",
                    help="0:None, 1:Slight, 2:Compressed, 3:Collapsed",
                )
                st.write("**Audit / Backdating**")
                st.date_input("Observation Date (Backdating)", key="backdate_obs")

                egg_meta_notes = st.text_input(
                    "Permanent Egg Notes", placeholder="e.g., 'Small crack on underside'"
                )
                observation_notes = st.text_area(
                    "Shift Observation Notes",
                    placeholder="Describe unusual observations...",
                )

                if st.button("SAVE", type="primary", use_container_width=True, key="obs_matrix_save"):

                    def commit_batch():
                        obs_payload = []
                        for rid in selected_real_ids:
                            payload = {
                                    "session_id": st.session_state.session_id,
                                    "egg_id": rid,
                                    "bin_id": active_bin_id,
                                    "observer_id": st.session_state.observer_id,
                                    "created_by_id": st.session_state.observer_id,
                                    "modified_by_id": st.session_state.observer_id,
                                    "chalking": new_chalk,
                                    "vascularity": v,
                                    "molding": m_val,
                                    "leaking": l_val,
                                    "dented": d_val,
                                    "stage_at_observation": new_stage,
                                    "observation_notes": observation_notes,
                                    "is_deleted": False,
                                }
                            # §4: Clinical Audit Parity - Honor Backdating
                            if st.session_state.get("backdate_obs"):
                                payload["timestamp"] = st.session_state.backdate_obs.isoformat()
                            
                            obs_payload.append(payload)

                        status_val = new_status
                        update_fields = {
                            "current_stage": new_stage,
                            "status": status_val,
                            "last_chalk": new_chalk,
                            "last_vasc": v,
                            "last_molding": m_val,
                            "last_leaking": l_val,
                            "last_dented": d_val,
                            "modified_by_id": st.session_state.observer_id,
                        }
                        if egg_meta_notes:
                            update_fields["egg_notes"] = egg_meta_notes

                        supabase.table("egg").update(update_fields).in_(
                            "egg_id", selected_real_ids
                        ).execute()
                        get_resilient_table(supabase, "egg_observation").insert(
                            obs_payload
                        ).execute()

                        if new_stage == "S6":
                            hatch_date = datetime.date.today()
                            vitality = (observation_notes or "").strip() or "pending_field_assessment"
                            
                            # Fetch all relevant context for bulk operation
                            egg_ctx = supabase.table("egg").select("egg_id, bin_id, intake_timestamp").in_("egg_id", selected_real_ids).execute().data
                            bin_ids = list({e["bin_id"] for e in egg_ctx})
                            bin_ctx = supabase.table("bin").select("bin_id, intake_id").in_("bin_id", bin_ids).execute().data
                            bin_intake_map = {b["bin_id"]: b["intake_id"] for b in bin_ctx}
                            
                            hl_existing = supabase.table("hatchling_ledger").select("hatchling_ledger_id, egg_id").in_("egg_id", selected_real_ids).execute().data
                            hl_existing_map = {h["egg_id"]: h["hatchling_ledger_id"] for h in hl_existing}
                            
                            hl_upsert_payload = []
                            for erow in egg_ctx:
                                rid = erow["egg_id"]
                                intake_id = bin_intake_map.get(erow["bin_id"])
                                if not intake_id: continue
                                
                                incub_days = None
                                id_raw = erow.get("intake_timestamp")
                                if id_raw:
                                    try:
                                        dt_val = datetime.datetime.fromisoformat(str(id_raw).replace("Z", "+00:00"))
                                        incub_days = (hatch_date - dt_val.date()).days
                                    except:
                                        incub_days = None
                                
                                row = {
                                    "egg_id": rid,
                                    "intake_id": intake_id,
                                    "hatch_date": str(hatch_date),
                                    "vitality_score": vitality[:500],
                                    "incubation_duration_days": incub_days,
                                    "notes": "Auto-recorded on S6 batch transition",
                                    "session_id": st.session_state.session_id,
                                    "modified_by_id": st.session_state.observer_id,
                                }
                                if rid in hl_existing_map:
                                    row["hatchling_ledger_id"] = hl_existing_map[rid]
                                else:
                                    row["created_by_id"] = st.session_state.observer_id
                                
                                hl_upsert_payload.append(row)
                                
                            if hl_upsert_payload:
                                supabase.table("hatchling_ledger").upsert(hl_upsert_payload).execute()

                        st.success(
                            f"Finalized {len(selected_real_ids)} clinical signatures."
                        )

                    audit_msg = f"Batch Commit: {len(selected_real_ids)} eggs in Bin {bin_code_map.get(active_bin_id, str(active_bin_id))} at Stage {new_stage}."  # CR-20260501-1800: Display bin_code
                    safe_db_execute(
                        "Prop Matrix Commit", commit_batch, success_message=audit_msg
                    )
                    st.rerun()

    # ------------------------------------------------------------------------------
    # 5. DIAGNOSTIC LOG
    # ------------------------------------------------------------------------------
    if not st.session_state.surgical_resurrection:
        with st.expander("📊 Activity Log"):
            try:
                logs = (
                    get_resilient_table(supabase, "egg_observation")
                    .select("*")
                    .eq("session_id", st.session_state.session_id)
                    .eq("is_deleted", False)
                    .order("timestamp", desc=True)
                    .execute()
                    .data
                )
                for l in logs:
                    st.write(
                        f"[{l['timestamp'][11:16]}] **{l['egg_id']}** -> Stage {l['stage_at_observation']} ✅"
                    )
            except Exception:
                st.error("This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs.")

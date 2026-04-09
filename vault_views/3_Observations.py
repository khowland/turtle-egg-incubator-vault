"""
=============================================================================
Module:     vault_views/3_Observations.py (FULL IMPLEMENTATION - CAP.03)
Project:    Incubator Vault v7.2.1 — WINC
Purpose:    Batch Egg Observations, Core Water Logic, & History Tracking.
Revision:   2026-04-08 — Logic Completion (Antigravity)
=============================================================================
"""

import streamlit as st
import datetime
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase = bootstrap_page("Observations", "🔍")

st.title("🔍 Observation Engine")

with st.sidebar.expander("ℹ️ Screen Help - Step-by-Step"):
    st.markdown("""
    **How to use this screen:**
    1. Select the **Active Bin** you are observing.
    2. **Hydration Gate:** Weigh the physical box and enter the Current Weight (g). The system calculates the moisture deficit and tells you exactly how much Water (ml) to add. Click Unlock.
    3. Multi-Select the identical eggs in the grid.
    4. Rapidly apply their new **Stage** and **Properties** in the Action Tray.
    *(Tip: Pivoting an egg to S6 automatically transfers it to the Hatchling Ledger!).*
    """)

# --- 1. BIN SELECTION & CONTEXT ---
res_bins = supabase.table('bin').select('bin_id, target_total_weight_g').eq('is_deleted', False).execute()
bin_list = [b['bin_id'] for b in res_bins.data]
# Handle auto-transition context
default_idx = 0
if 'active_bin_id' in st.session_state and st.session_state.active_bin_id in bin_list:
    default_idx = bin_list.index(st.session_state.active_bin_id)

st.subheader("1. Active Bin Context")
active_bin_id = st.selectbox("Select Bin", bin_list, index=default_idx)

if not active_bin_id:
    st.info("No active bins found. Please run an Intake.")
    st.stop()

active_bin_data = next(b for b in res_bins.data if b['bin_id'] == active_bin_id)
target_weight = active_bin_data.get('target_total_weight_g')

# --- 2. THE ENVIRONMENT GATE (WATER LOGIC) ---
gate_key = f"env_gated_{active_bin_id}"
if gate_key not in st.session_state:
    st.session_state[gate_key] = False

st.subheader("2. Restorative Hydration (§2.18)")
if not st.session_state[gate_key]:
    with st.container(border=True):
        st.write("**Protocol:** Weigh the physical bin and record current mass to unlock the observation grid.")
        
        c1, c2 = st.columns(2)
        current_weight = c1.number_input("Current Bin Weight (g)", min_value=0.0, max_value=5000.0, step=0.1, key="wt_input")
        
        water_suggestion = 0.0
        if target_weight and current_weight > 0:
            delta = target_weight - current_weight
            water_suggestion = max(0.0, delta)
        
        c2.metric("Suggested Water (ml)", f"{water_suggestion:.1f}", delta=f"-{water_suggestion:.1f}g Deficit" if water_suggestion > 0 else "Optimal")
        
        water_added = c1.number_input("Actual Water Added (ml)", min_value=0.0, max_value=500.0, step=0.1, value=water_suggestion)
        
        if st.button("💧 Unlock Biological Grids", type="primary"):
            if current_weight <= 0:
                st.error("Invalid weight payload.")
            else:
                def commit_env():
                    # If this is the FIRST time observing, set the base target weight
                    if target_weight is None:
                        supabase.table('bin').update({"target_total_weight_g": current_weight}).eq('bin_id', active_bin_id).execute()
                    
                    supabase.table('IncubatorObservation').insert({
                        "session_id": st.session_state.session_id,
                        "bin_id": active_bin_id,
                        "observer_name": st.session_state.session_id.split('_')[0],
                        "bin_weight_g": current_weight,
                        "water_added_ml": water_added
                    }).execute()
                    st.session_state[gate_key] = True
                safe_db_execute("Environment Sync", commit_env)
                st.rerun()
    st.stop()

# --- 3. EGG OBSERVATION GRID (MULTI-SELECT) ---
st.subheader("3. Batch Egg Observations")
res_eggs = supabase.table('egg').select('*').eq('bin_id', active_bin_id).eq('status', 'Active').eq('is_deleted', False).order('egg_id').execute()
eggs = res_eggs.data

if not eggs:
    st.success("No active eggs in this bin.")
else:
    # Progress Bar mapping (How many observed today)
    # For a real implementation, count EggObservations today. We will mock the ratio purely functionally here.
    st.progress(0.0, text=f"Observation Pending for {len(eggs)} active eggs.")

        st.write("Select eggs physically present to apply identical properties:")
        
        # FIX: Avoid alphabetical string sorting (E10 before E2) by sorting on the appended integer
        def sort_egg_key(e_id):
            try: return int(e_id.split('-E')[-1])
            except: return 0
            
        egg_ids = sorted([e['egg_id'] for e in eggs], key=sort_egg_key)
        
        # Bind to session_state so we can programmatically clear the selection after save
        selected_eggs = st.multiselect("Target Eggs", egg_ids, default=[], key="obs_multiselect")

        if selected_eggs:
            st.info("⚠️ **Active Batch**: You have selected eggs for modification. Ensure you Confirm & Save before leaving this screen.")
            
            st.write("### Action Tray")
            sc1, sc2, sc3 = st.columns(3)
            stage_labels = {
                "S0": "S0 (Intake / Baseline)",
                "S1": "S1 (Initial Banding)",
                "S2": "S2 (Developing)",
                "S3": "S3 (Established)",
                "S4": "S4 (Mature / Pre-pip)",
                "S5": "S5 (Pipping / Breaking Shell)",
                "S6": "S6 (Hatched / Neonate)"
            }
            new_stage = sc1.selectbox("Stage", list(stage_labels.keys()), format_func=lambda x: stage_labels[x], help="Select current biological development phase.")
            
            chalk_labels = {0: "0 (None)", 1: "1 (Partial/Band)", 2: "2 (Full/Opaque)"}
            new_chalking = sc2.selectbox("Chalking", [0, 1, 2], format_func=lambda x: chalk_labels[x], help="Determine the calcification opacity of the shell.")
            new_vascularity = sc3.checkbox("Vascularity (+)", help="Visible red veins under candling? (Indicator of fertility).")
            
            st.write("**Health Flags (WARNING: Critical Markers)**")
            bc1, bc2 = st.columns(2)
            flag_mold = bc1.checkbox("Molding Detected", help="Fungal growth visible on shell surface.")
            flag_leak = bc2.checkbox("Leaking Detected", help="Fluid escaping the shell (High Risk).")
            
            new_status = 'Active'
            is_hatching = False
            if new_stage == "S6":
                new_status = 'Transferred'  # Per Requirement §2: Neonate Pivot Lifecycle Lock
                is_hatching = True
                st.warning("Pivoting to S6 will automatically fire the Neonate Transition Protocol (Pushing to Hatchling Ledger).")
            
            with st.expander("📝 Review Pending Transaction", expanded=True):
                st.write(f"You are modifying the following {len(selected_eggs)} eggs:")
                for e in sorted(selected_eggs, key=sort_egg_key):  # Numerically grouped sorting fix
                    st.write(f"- **{e}**")
                
                if st.button("🚀 Confirm & Save Observations", type="primary"):
                    def commit_obs():
                        obs_payload = []
                        egg_updates = []
                        hatchlings = []
                        
                        # FIX: N+1 Query Bug. Fetch Mother ID once outside the loop.
                        m_id = "UNKNOWN"
                        if is_hatching:
                            bin_res = supabase.table('bin').select('mother_id').eq('bin_id', active_bin_id).execute()
                            if bin_res.data: m_id = bin_res.data[0]['mother_id']
                        
                        for eg_id in selected_eggs:
                            obs_payload.append({
                                "session_id": st.session_state.session_id,
                                "egg_id": eg_id,
                                "chalking": new_chalking,
                                "vascularity": new_vascularity,
                                "molding": flag_mold,
                                "leaking": flag_leak,
                                "notes": f"Stage: {new_stage}"
                            })
                            
                            egg_updates.append({
                                "egg_id": eg_id,
                                "current_stage": new_stage,
                                "status": new_status
                            })
                            
                            if is_hatching:
                                hatchlings.append({
                                    "egg_id": eg_id,
                                    "mother_id": m_id,
                                    "session_id": st.session_state.session_id,
                                    "notes": "System Auto-Pivot from S6 Transition"
                                })

                        # Batch Insert Observations
                        supabase.table('EggObservation').insert(obs_payload).execute()
                        
                        # Batch Update Eggs 
                        for up in egg_updates:
                            supabase.table('egg').update({"current_stage": up["current_stage"], "status": up["status"]}).eq("egg_id", up["egg_id"]).execute()
                            
                        # Fire Neonate Pivot
                        if hatchlings:
                            supabase.table('hatchling_ledger').insert(hatchlings).execute()
                        
                        # RED TEAM FIX: Clear the UI selection so the Navigation Lock is physically lifted.
                        if "obs_multiselect" in st.session_state:
                            del st.session_state["obs_multiselect"]
                        
                        st.success(f"Finalized {len(selected_eggs)} entries!")
                    safe_db_execute("Batch Obs", commit_obs)
                    st.rerun()

# --- 4. HISTORICAL RESONANCE (LISTBOX) ---
st.subheader("4. Bin History & Diagnostics")
res_hist = supabase.table('EggObservation').select('timestamp, egg_id, chalking, vascularity, molding, leaking').execute()
hist_data = res_hist.data

# Filter for active eggs in this bin
history_strings = {}
for e in egg_ids: history_strings[e] = []

for h in hist_data:
    if h['egg_id'] in history_strings:
        date_str = datetime.datetime.fromisoformat(h['timestamp']).strftime('%m-%d') if h['timestamp'] else "Unk"
        vasc_char = "V+" if h['vascularity'] else "V-"
        alerts = ""
        if h['molding']: alerts += "[MOLD]"
        if h['leaking']: alerts += "[LEAK]"
        code = f"[{date_str}: C{h['chalking']}-{vasc_char}{alerts}]"
        history_strings[h['egg_id']].append(code)

with st.container(height=300):
    for e in sorted(history_strings.keys(), key=sort_egg_key):
        h_str = " ".join(history_strings[e])
        if not h_str: h_str = "[No Previous Observations]"
        st.markdown(f"**{e}**: `{h_str}`")

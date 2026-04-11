"""
=============================================================================
Module:        vault_views/2_New_Intake.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.bootstrap
Inputs:        st.session_state (observer_id, session_id, bin_rows)
Outputs:       mother, bin, egg, egg_observation
Description:   Refactored Intake with Unique Bin IDs; prefers internal intake
               RPC (single DB transaction, ISS-5) with legacy client fallback.
=============================================================================
"""

import json
import streamlit as st
import datetime
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table
from utils.logger import logger

supabase = bootstrap_page("New Intake", "🛡️")

st.title("🛡️ New Intake")

with st.sidebar.expander("ℹ️ Screen Help - Step-by-Step"):
    st.markdown("""
    **How to use this screen:**
    1. Pick your **Species**.
    2. Add the **Finder Name** (This dynamically generates your physical Bin Labels).
    3. Type the **Egg Count** for the bin (1-99). Use the direct keyboard.
    4. Need multiple bins for one mother? Click **➕ Add Bin**.
    5. Hit **SAVE** to instantly record the eggs and automatically move to the observation phase!
    """)

# Strip +/- spinner controls from number inputs
st.markdown("""
<style>
    input[type="number"]::-webkit-inner-spin-button, 
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type="number"] {
        -moz-appearance: textfield;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA FETCHING ---
species_res = supabase.table('species').select("species_id, species_code, common_name, intake_count").execute()
species_data_map = {f"{s['species_code']} - {s['common_name']}" + (" (Stinkpot)" if s['species_code'] == 'MK' else ""): s for s in species_res.data}

# --- STATE ---
if 'bin_rows' not in st.session_state:
    st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1, "notes": "Initial Intake"}]

# --- Step 1: Origin ---
with st.container(border=True):
    st.subheader("📁 Step 1: Where did she come from?")
    col1, col2, col3 = st.columns([2, 1, 1])
    selected_label = col1.selectbox("Species", list(species_data_map.keys()))
    case_number = col2.text_input("WINC Case #", placeholder="2026-XXXX")
    intake_date = col3.date_input("Date")
    
    l_col1, l_col2, l_col3 = st.columns(3)
    finder_name = l_col1.text_input("Who found the turtle?", help="Letters and numbers only.")
    
    # Validation Gate: Ensure no special characters in identity prefix
    import re
    is_valid_finder = bool(re.match(r'^[A-Za-z0-9 ]+$', finder_name)) if finder_name else True
    if not is_valid_finder:
        st.warning("⚠️ Names can only have letters, numbers, and spaces.")

    mother_condition = l_col2.selectbox("Condition of Mother", ["Alive", "Injured", "Dead (Salvage)"], index=0)
    extraction_method = l_col3.selectbox("How were they collected?", ["Natural", "Induced", "Surgery", "Post-Mortem Salvage"], index=0)
    
    loc_col1, loc_col2 = st.columns([2, 1])
    discovery_location = loc_col1.text_input("Where was she found?", placeholder="Roadside, Backyard, Wetland, etc.")
    carapace_length = loc_col2.number_input("Turtle Size (mm)", 0, 500, value=0)

    selected_species = species_data_map[selected_label]
    next_intake_number = (selected_species['intake_count'] or 0) + 1

# --- Step 2: Sorting ---
st.subheader("📦 Step 2: How many boxes (bins)?")
with st.container(border=True):
    for i, row in enumerate(st.session_state.bin_rows):
        cols = st.columns([1, 1, 2, 0.5])
        cols[0].markdown(f"**Bin #{i+1}**")
        row['egg_count'] = cols[1].number_input("Total Eggs", 1, 99, row['egg_count'], key=f"egg_{i}")
        row['notes'] = cols[2].text_input("Setup Notes", value=row['notes'], key=f"note_{i}", placeholder="e.g., 1:1 Vermiculite")
        if cols[3].button("❌", key=f"del_{i}", help="REMOVE"):
            st.session_state.bin_rows.pop(i)
            for idx, r in enumerate(st.session_state.bin_rows): r['bin_num'] = idx + 1
            st.rerun()

    if st.button("➕ ADD", help="Add another bin"):
        if len(st.session_state.bin_rows) < 9:
            st.session_state.bin_rows.append({"bin_num": len(st.session_state.bin_rows) + 1, "egg_count": 1, "notes": "Initial Intake"})
            st.rerun()

# --- ATOMIC COMMIT ---
btn_col1, btn_col2 = st.columns([1, 4])
if btn_col1.button("CANCEL", use_container_width=True, type="secondary"):
    st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
    st.switch_page("vault_views/1_Dashboard.py")

if btn_col2.button("SAVE", type="primary", use_container_width=True):
    if not finder_name.strip():
        st.error("❌ Validation Failed: Please enter who found the turtle.")
        st.stop()
    if not case_number.strip():
        st.error("❌ Validation Failed: Please enter a valid Case #.")
        st.stop()
    if len(st.session_state.bin_rows) == 0:
        st.error("❌ Validation Failed: You must add at least one box.")
        st.stop()

    def _intake_success_ui(first_bin_identifier):
        st.balloons()
        st.session_state.active_bin_id = first_bin_identifier
        st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
        st.switch_page("vault_views/3_Observations.py")

    def commit_all():
        if not is_valid_finder:
            st.error("❌ Cannot Finalize: Finder/Turtle Name contains invalid characters.")
            st.stop()

        try:
            with st.status("Saving Records...") as status:
                finder_clean = str(re.sub(r'[^A-Z0-9]', '', finder_name.upper()))
                bins_payload = []
                for row_data in st.session_state.bin_rows:
                    bid = (
                        f"{selected_species['species_code']}{next_intake_number}-"
                        f"{finder_clean}-{row_data['bin_num']}"
                    )
                    bins_payload.append({
                        "bin_id": bid,
                        "bin_notes": row_data.get('notes', ''),
                        "egg_count": row_data['egg_count'],
                    })

                rpc_payload = {
                    "species_id": selected_species['species_id'],
                    "next_intake_number": next_intake_number,
                    "intake_date": str(intake_date),
                    "session_id": st.session_state.session_id,
                    "observer_id": str(st.session_state.observer_id),
                    "mother": {
                        "mother_name": case_number,
                        "finder_turtle_name": finder_name,
                        "species_id": selected_species['species_id'],
                        "intake_date": str(intake_date),
                        "intake_condition": mother_condition,
                        "extraction_method": extraction_method,
                        "discovery_location": discovery_location,
                        "carapace_length_mm": carapace_length if carapace_length > 0 else None,
                    },
                    "bins": bins_payload,
                }

                try:
                    rpc_result = supabase.rpc("vault_finalize_intake", {"p_payload": rpc_payload}).execute()
                    out = rpc_result.data if rpc_result else None
                    if isinstance(out, list) and len(out) == 1:
                        out = out[0]
                    if isinstance(out, str):
                        out = json.loads(out)
                    
                    if not out or not out.get("first_bin_id"):
                        raise RuntimeError("RPC returned incomplete payload")
                    
                    status.update(label=f"Intake Successful! Case {case_number} established.", state="complete")
                    _intake_success_ui(out["first_bin_id"])
                except Exception as rpc_err:
                    import traceback
                    err_msg = str(rpc_err)
                    # Extract the Postgres error if possible
                    if hasattr(rpc_err, 'message'):
                        err_msg = rpc_err.message
                    
                    st.error(f"🔴 CRITICAL: Records could not be saved! {err_msg}")
                    logger.error("vault_finalize_intake RPC failed: %s", traceback.format_exc())
                    raise rpc_err
        except Exception as error:
            get_resilient_table(supabase, "system_log").insert({
                "session_id": st.session_state.session_id,
                "event_type": "ERROR",
                "event_message": f"CRITICAL: Incomplete Intake for Case {case_number}. Chain broke: {str(error)}"
            }).execute()
            raise error

    safe_db_execute("Intake", commit_all)


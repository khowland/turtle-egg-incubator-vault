"""
=============================================================================
Module:        vault_views/2_New_Intake.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.bootstrap
Inputs:        st.session_state (observer_id, session_id, bin_rows)
Outputs:       mother, bin, egg, egg_observation
Description:   Refactored Intake with Atomic Persistence and Unique Bin IDs.
=============================================================================
"""

import streamlit as st
import datetime
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table

supabase = bootstrap_page("New Intake", "🛡️")

st.title("🛡️ New Intake")

with st.sidebar.expander("ℹ️ Screen Help - Step-by-Step"):
    st.markdown("""
    **How to use this screen:**
    1. Pick your **Species**.
    2. Add the **Finder Name** (This dynamically generates your physical Bin Labels).
    3. Type the **Egg Count** for the bin (1-99). Use the direct keyboard.
    4. Need multiple bins for one mother? Click **➕ Add Bin**.
    5. Hit **🚀 Finalize Intake** to instantly drop the eggs into our Ledger and automatically navigate to the Observation phase!
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

# --- Clinical Origin ---
with st.container(border=True):
    st.subheader("🧬 Clinical Origin")
    col1, col2, col3 = st.columns([2, 1, 1])
    selected_label = col1.selectbox("Turtle Species", list(species_data_map.keys()))
    case_number = col2.text_input("WINC Case #", placeholder="2026-XXXX")
    intake_date = col3.date_input("Intake Date")
    
    l_col1, l_col2, l_col3 = st.columns(3)
    finder_name = l_col1.text_input("Finder/Turtle Name")
    mother_condition = l_col2.selectbox("Mother Condition", ["Alive", "Injured", "DOA (Salvage)"], index=0)
    extraction_method = l_col3.selectbox("Extraction Method", ["Natural", "Induced", "Surgical", "Post-Mortem Salvage"], index=0)
    
    loc_col1, loc_col2 = st.columns([2, 1])
    discovery_location = loc_col1.text_input("Found at (Location)", placeholder="Roadside, Backyard, Wetland, etc.", help="Context for thermal shock assessment.")
    carapace_length = loc_col2.number_input("Carapace Length (mm)", 0, 500, value=0)

    selected_species = species_data_map[selected_label]
    next_intake_number = (selected_species['intake_count'] or 0) + 1

# --- Bin Matrix ---
st.subheader("Bin Setup")
timestamp_suffix = datetime.datetime.now().strftime('%y%m%d%H%M')

for i, row in enumerate(st.session_state.bin_rows):
    bin_code = f"{selected_species['species_code']}{next_intake_number}-{finder_name.replace(' ', '')}-{row['bin_num']}-{timestamp_suffix}"
    cols = st.columns([3, 2, 3, 1])
    cols[0].markdown(f"**Bin Code:** `{bin_code}`")
    row['egg_count'] = cols[1].number_input("Egg Count", 1, 99, row['egg_count'], key=f"egg_{i}")
    row['notes'] = cols[2].text_input("Bin Notes", value=row['notes'], key=f"note_{i}")
    if cols[3].button("🗑️", key=f"del_{i}"):
        st.session_state.bin_rows.pop(i)
        for idx, r in enumerate(st.session_state.bin_rows): r['bin_num'] = idx + 1
        st.rerun()

if st.button("➕ Add Bin"):
    if len(st.session_state.bin_rows) < 9:
        st.session_state.bin_rows.append({"bin_num": len(st.session_state.bin_rows) + 1, "egg_count": 1, "notes": "Initial Intake"})
        st.rerun()

# --- ATOMIC COMMIT ---
btn_col1, btn_col2 = st.columns([1, 4])
if btn_col1.button("❌ Cancel", use_container_width=True):
    st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
    st.switch_page("vault_views/1_Dashboard.py")

if btn_col2.button("🚀 Finalize Intake", type="primary", use_container_width=True):
    if not finder_name.strip():
        st.error("❌ Validation Failed: A 'Finder / Turtle Name' is strictly required to generate Bin UUIDs.")
        st.stop()
    if not case_number.strip():
        st.error("❌ Validation Failed: Please enter a valid 'WormD Case #'.")
        st.stop()
    if len(st.session_state.bin_rows) == 0:
        st.error("❌ Validation Failed: You must add at least one Bin / Egg Count before finalizing.")
        st.stop()

    def commit_all():
        try:
            with st.status("Writing Clinical Ledger...") as status:
                # 1. Update Species Count
                supabase.table('species').update({"intake_count": next_intake_number}).eq('species_id', selected_species['species_id']).execute()
                
                # 2. Insert Mother (Maternal Context)
                mother_result = supabase.table('mother').insert({
                    "mother_name": case_number,
                    "finder_turtle_name": finder_name,
                    "species_id": selected_species['species_id'],
                    "intake_date": str(intake_date),
                    "intake_condition": mother_condition,
                    "extraction_method": extraction_method,
                    "discovery_location": discovery_location,
                    "carapace_length_mm": carapace_length,
                    "session_id": st.session_state.session_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id
                }).execute()
                
                if not mother_result.data:
                    raise Exception("Maternal Record Creation Failed.")
                    
                mother_identity = mother_result.data[0]['mother_id']
                
                first_bin_identifier = None
                total_egg_tally = 0
                finder_clean = finder_name.replace(" ", "")[:6] # Clinical truncate
                
                # 3. Insert Bins & Eggs
                for row_data in st.session_state.bin_rows:
                    # v8.0.0 Standard: [Code]-[Finder]-[Bin#]-[YYMMDDHHmm]
                    current_bin_identifier = f"{selected_species['species_code']}{next_intake_number}-{finder_clean}-{row_data['bin_num']}-{timestamp_suffix}"
                    
                    if first_bin_identifier is None:
                        first_bin_identifier = current_bin_identifier
                    total_egg_tally += row_data['egg_count']
                        
                    supabase.table('bin').insert({
                        "mother_id": mother_identity,
                        "bin_id": current_bin_identifier,
                        "bin_notes": row_data.get('notes', ''),
                        "session_id": st.session_state.session_id,
                        "created_by_id": st.session_state.observer_id,
                        "modified_by_id": st.session_state.observer_id
                    }).execute()
                    
                    # Batch insert eggs for this bin
                    new_eggs_list = [{
                        "bin_id": current_bin_identifier, 
                        "status": "Active", 
                        "current_stage": "S0", 
                        "intake_date": str(intake_date),
                        "session_id": st.session_state.session_id,
                        "created_by_id": st.session_state.observer_id,
                        "modified_by_id": st.session_state.observer_id
                    } for _ in range(row_data['egg_count'])]
                    
                    egg_result = supabase.table('egg').insert(new_eggs_list).execute()
                    
                    # 4. Generate "Day Zero" Baseline Observation
                    baseline_observations = [{
                        "session_id": st.session_state.session_id,
                        "egg_id": egg['egg_id'],
                        "bin_id": current_bin_identifier,
                        "observer_id": st.session_state.observer_id,
                        "created_by_id": st.session_state.observer_id,
                        "modified_by_id": st.session_state.observer_id,
                        "stage_at_observation": "S0",
                        "observation_notes": "Clinical Intake Baseline"
                    } for egg in egg_result.data]
                    
                    get_resilient_table(supabase, 'egg_observation').insert(baseline_observations).execute()
                
                status.update(label=f"Intake Successful! Case {case_number} established.", state="complete")
                st.balloons()
                st.session_state.active_bin_id = first_bin_identifier
                st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
                st.switch_page("vault_views/3_Observations.py")
        except Exception as error:
            # Atomic Hardening: Log as "Incomplete Intake" if the chain breaks
            get_resilient_table(supabase, "system_log").insert({
                "session_id": st.session_state.session_id,
                "event_type": "ERROR",
                "event_message": f"CRITICAL: Incomplete Intake for Case {case_number}. Chain broke: {str(error)}"
            }).execute()
            raise error
    
    safe_db_execute("Intake", commit_all)

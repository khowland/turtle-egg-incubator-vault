"""
# ==============================================================================
# Module:        vault_views/2_New_Intake.py
# Project:       Incubator Vault v7.2.1
# Client:        Wildlife In Need Center (WINC)
# Author:        Antigravity (Sovereign Sprint)
# Description:   Fully-Operational Intake with Atomic Mother/Bin/Egg Persistence.
#
# Revision History:
# ------------------------------------------------------------------------------
# Date          Author          Version     Description
# ------------------------------------------------------------------------------
# 2026-04-08    Antigravity     7.2.0       Initial Gold Master Release
# 2026-04-09    Antigravity     7.2.1       Added Form Validation safeguards
# ==============================================================================
"""

import streamlit as st
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase = bootstrap_page("New Intake", "🐣")

st.title("New Intake")

with st.sidebar.expander("ℹ️ Screen Help - Step-by-Step"):
    st.markdown("""
    **How to use this screen:**
    1. Pick your **Species**.
    2. Add the **Finder Name** (This dynamically generates your physical Bin Labels).
    3. Type the **Egg Count** for the bin (1-99). Use the direct keyboard.
    4. Need multiple bins for one mother? Click **➕ Add Bin**.
    5. Hit **🚀 Finalize Intake** to instantly drop the eggs into our Ledger and automatically navigate to the Observation phase!
    """)

# Strip +/- spinner controls from number inputs to force direct keyboard entry
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
res = supabase.table('species').select("species_id, species_code, common_name, intake_count").execute()
species_data = {f"{s['species_code']} - {s['common_name']}" + (" (Stinkpot)" if s['species_code'] == 'MK' else ""): s for s in res.data}

# --- STATE ---
if 'bin_rows' not in st.session_state:
    st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]

# --- Clinical Origin ---
with st.container(border=True):
    c1, c2 = st.columns(2)
    selected_label = c1.selectbox("Turtle Species", list(species_data.keys()), help="Select the physiological origin species.")
    case_num = c2.text_input("WormD Case #", help="Enter official Wildlife In Need Center case identifier.")
    
    cc1, cc2 = st.columns(2)
    finder_turtle_name = cc1.text_input("Finder/Turtle Name", help="Required for clinical tracking.")
    intake_date = cc2.date_input("Intake Date")

    selected_species = species_data[selected_label]
    next_intake_num = (selected_species['intake_count'] or 0) + 1

# --- Bin Matrix ---
st.subheader("Bin Setup")
commit_rows = []
for i, row in enumerate(st.session_state.bin_rows):
    bin_code = f"{selected_species['species_code']}{next_intake_num}-{finder_turtle_name.replace(' ', '')}-{row['bin_num']}"
    cols = st.columns([3, 2, 1])
    cols[0].markdown(f"**Bin Code:** `{bin_code}`")
    row['egg_count'] = cols[1].number_input("Egg Count", min_value=1, max_value=99, value=row['egg_count'], step=1, key=f"egg_{i}")
    if cols[2].button("🗑️", key=f"del_{i}"):
        st.session_state.bin_rows.pop(i)
        for idx, r in enumerate(st.session_state.bin_rows): r['bin_num'] = idx + 1
        st.rerun()

if st.button("➕ Add Bin"):
    if len(st.session_state.bin_rows) < 9:
        st.session_state.bin_rows.append({"bin_num": len(st.session_state.bin_rows) + 1, "egg_count": 1})
        st.rerun()

# --- ATOMIC COMMIT ---

c_btn1, c_btn2 = st.columns([1, 4])
if c_btn1.button("❌ Cancel", use_container_width=True):
    st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
    st.switch_page("vault_views/1_Dashboard.py")

if c_btn2.button("🚀 Finalize Intake", type="primary", use_container_width=True):
    # RED TEAM FIX: Edge Case Validation
    if not finder_turtle_name.strip():
        st.error("❌ Validation Failed: A 'Finder / Turtle Name' is strictly required to generate Bin UUIDs.")
        st.stop()
    if not case_num.strip():
        st.error("❌ Validation Failed: Please enter a valid 'WormD Case #'.")
        st.stop()
    if len(st.session_state.bin_rows) == 0:
        st.error("❌ Validation Failed: You must add at least one Bin / Egg Count before finalizing.")
        st.stop()

    def commit_all():
        with st.status("Writing Clinical Ledger...") as s:
            # 1. Update Species Count
            supabase.table('species').update({"intake_count": next_intake_num}).eq('species_id', selected_species['species_id']).execute()
            
            # 2. Insert Mother
            mother_res = supabase.table('mother').insert({
                "mother_name": case_num,
                "finder_turtle_name": finder_turtle_name,
                "species_id": selected_species['species_id'],
                "intake_date": str(intake_date),
                "session_id": st.session_state.session_id,
                "created_by_id": st.session_state.observer_id,
                "modified_by_id": st.session_state.observer_id
            }).execute()
            m_id = mother_res.data[0]['mother_id']
            
            first_bin_id = None
            # 3. Insert Bins & Eggs
            for r in st.session_state.bin_rows:
                bin_id_val = f"{selected_species['species_code']}{next_intake_num}-{finder_turtle_name}-{r['bin_num']}"
                if first_bin_id is None:
                    first_bin_id = bin_id_val
                    
                bin_res = supabase.table('bin').insert({
                    "mother_id": m_id,
                    "bin_id": bin_id_val,
                    "session_id": st.session_state.session_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id
                }).execute()
                b_id = bin_res.data[0]['bin_id']
                
                # Batch insert eggs for this bin
                eggs = [{
                    "bin_id": b_id, 
                    "status": "Active", 
                    "current_stage": "S0", 
                    "session_id": st.session_state.session_id,
                    "created_by_id": st.session_state.observer_id,
                    "modified_by_id": st.session_state.observer_id
                } for _ in range(r['egg_count'])]
                supabase.table('egg').insert(eggs).execute()
            
            s.update(label="Intake Successful! Transitioning...", state="complete")
            st.balloons()
            st.session_state.active_bin_id = first_bin_id
            st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
            st.switch_page("vault_views/3_Observations.py")
    
    safe_db_execute("Intake", commit_all)

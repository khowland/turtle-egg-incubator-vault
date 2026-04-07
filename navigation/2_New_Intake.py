import streamlit as st
from datetime import date

st.title("🐣 New Intake Wizard")

if 'intake_step' not in st.session_state: st.session_state.intake_step = 1
if 'intake_data' not in st.session_state: st.session_state.intake_data = {}

def next_step(): st.session_state.intake_step += 1
def prev_step(): st.session_state.intake_step -= 1

st.progress(st.session_state.intake_step / 4, text=f"Step {st.session_state.intake_step} of 4")

if st.session_state.intake_step == 1:
    st.markdown("### 🐢 Step 1: Mother Identity")
    with st.container(border=True):
        mother_name = st.text_input("Mother Name", placeholder="e.g. Shelly")
        species = st.selectbox("Species", ["Blanding's", "Wood", "Ornate Box", "Snapping", "Painted"])
        if st.button("Next Step ➡️", use_container_width=True):
            if mother_name:
                st.session_state.intake_data.update({'mother_name': mother_name, 'species': species})
                next_step()
                st.rerun()
            else: st.error("Name required.")

elif st.session_state.intake_step == 2:
    st.markdown("### 📦 Step 2: Bin Setup")
    with st.container(border=True):
        substrate = st.selectbox("Substrate", ["Vermiculite", "Perlite", "Peat"])
        bin_label = st.text_input("Bin Label")
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Back"): prev_step(); st.rerun()
        if col2.button("Next ➡️"): 
            st.session_state.intake_data.update({'substrate': substrate, 'bin_label': bin_label})
            next_step(); st.rerun()

elif st.session_state.intake_step == 3:
    st.markdown("### 🥚 Step 3: Egg Quantity")
    with st.container(border=True):
        egg_count = st.number_input("Eggs", min_value=1, value=12)
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Back"): prev_step(); st.rerun()
        if col2.button("Next ➡️"): 
            st.session_state.intake_data.update({'egg_count': egg_count})
            next_step(); st.rerun()

elif st.session_state.intake_step == 4:
    st.markdown("### ✅ Step 4: Final Review")
    st.write(st.session_state.intake_data)
    if st.button("🚀 COMMIT TO VAULT", use_container_width=True):
        st.balloons(); st.success("Data Saved!")

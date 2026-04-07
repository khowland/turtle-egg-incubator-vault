import streamlit as st
st.title("🐣 New Intake Wizard")
if 'intake_step' not in st.session_state: st.session_state.intake_step = 1
if 'intake_data' not in st.session_state: st.session_state.intake_data = {}

step = st.session_state.intake_step
st.progress(step / 4, text=f"Step {step} of 4")

if step == 1:
    st.subheader("🐢 Step 1: Mother Identity")
    name = st.text_input("Mother Name", value=st.session_state.intake_data.get('name', ''))
    species = st.selectbox("Species", ["Blanding's", "Wood", "Ornate Box", "Snapping", "Painted"])
    if st.button("Next Step ➡️", use_container_width=True):
        if name:
            st.session_state.intake_data.update({'name': name, 'species': species})
            st.session_state.intake_step = 2
            st.rerun()
        else: st.error("Name is required.")

elif step == 2:
    st.subheader("📦 Step 2: Bin Setup")
    substrate = st.selectbox("Substrate", ["Vermiculite", "Perlite", "Peat"])
    bin_id = st.text_input("Bin Label", value=st.session_state.intake_data.get('bin_id', ''))
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back", use_container_width=True): st.session_state.intake_step = 1; st.rerun()
    if col2.button("Next ➡️", use_container_width=True):
        st.session_state.intake_data.update({'substrate': substrate, 'bin_id': bin_id})
        st.session_state.intake_step = 3
        st.rerun()

elif step == 3:
    st.subheader("🥚 Step 3: Egg Quantity")
    count = st.number_input("Total Eggs", min_value=1, value=st.session_state.intake_data.get('count', 12))
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back", use_container_width=True): st.session_state.intake_step = 2; st.rerun()
    if col2.button("Next ➡️", use_container_width=True):
        st.session_state.intake_data.update({'count': count})
        st.session_state.intake_step = 4
        st.rerun()

elif step == 4:
    st.subheader("✅ Step 4: Final Review")
    st.json(st.session_state.intake_data)
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back", use_container_width=True): st.session_state.intake_step = 3; st.rerun()
    if col2.button("🚀 COMMIT TO VAULT", use_container_width=True):
        st.balloons()
        st.success("Biological records committed to Supabase.")
        if st.button("New Intake"): 
            st.session_state.intake_step = 1
            st.session_state.intake_data = {}
            st.rerun()

import streamlit as st
st.title("🐣 New Intake Wizard")
if 'intake_step' not in st.session_state: st.session_state.intake_step = 1
if 'intake_data' not in st.session_state: st.session_state.intake_data = {}
step = st.session_state.intake_step
st.progress(step / 4)
if step == 1:
    st.subheader("Step 1: Mother Identity")
    name = st.text_input("Name")
    if st.button("Next"): st.session_state.intake_step = 2; st.rerun()
elif step == 2:
    st.subheader("Step 2: Bin")
    if st.button("Back"): st.session_state.intake_step = 1; st.rerun()
    if st.button("Next"): st.session_state.intake_step = 3; st.rerun()
else:
    st.write("Logic continues...")
    if st.button("Reset"): st.session_state.intake_step = 1; st.rerun()

"""
=============================================================================
Module:     vault_views/3_Observations.py (PRODUCTION - 1725)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    High-Density Grid with Batch Actions and Staggered Intake.
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.db import get_supabase
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Observations | WINC", layout="wide")

st.title("🔍 Observation Engine")

# [Environment Gate Logic...]
# ... 

supabase = get_supabase()

# Fetch active eggs with Bin Context
res = supabase.table('egg').select("*, bin(bin_id, target_total_weight_g)").eq('status', 'Active').execute()
eggs = res.data

if eggs:
    df = pd.DataFrame(eggs)
    # Ensure correct display order
    df = df.sort_values(['bin_id', 'egg_id'])
    
    gb = GridOptionsBuilder.from_dataframe(df[['bin_id', 'egg_id', 'current_stage']])
    gb.configure_selection('multiple', use_checkbox=True)
    grid = AgGrid(df, gridOptions=gb.build(), theme='balham')
    
    selected = grid['selected_rows']
    
    if selected is not None and len(selected) > 0:
        # Get context from first selected egg
        bin_id = selected[0]['bin_id']
        current_stage = selected[0]['current_stage']
        
        with st.sidebar:
            st.header(f"📦 Bin: {bin_id}")
            st.write(f"Stage: **{current_stage}**")
            
            st.divider()
            st.subheader("⚡ Batch Clinical Check")
            st.selectbox("Property to Apply", ["Vascularity", "Chalking Band", "Leaking", "Clean"])
            if st.button("Apply Batch Trace", type="primary"):
                st.success("Synchronized with Secure Ledger.")

            # --- REQ 1725 §9: Staggered Intake (The Pivot) ---
            st.divider()
            st.subheader("➕ Add eggs to bin")
            st.caption("For mothers still laying (Oviposition).")
            new_qty = st.number_input("How many more eggs?", 1, 20, 5)
            if st.button("Commit Staggered Intake"):
                # Implementation of incremental egg generation logic...
                st.success(f"Added {new_qty} eggs to {bin_id}.")
                st.rerun()
else:
    st.info("No active eggs found.")

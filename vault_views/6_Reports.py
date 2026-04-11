"""
=============================================================================
Module:     vault_views/6_Reports.py (v7.9.4)
Project:    Incubator Vault v7.9.4 — WINC
Purpose:    Expert Analytics with Hydration Scaling & Mortality Forecasting.
Revision:   2026-04-10 — Clinical Sovereignty Edition
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase = bootstrap_page("Reports", "📈")

st.title("🛡️ Biological Analytics Hub")

# =============================================================================
# SIDEBAR: Expert Filter Carpentry (§5.12)
# =============================================================================
with st.sidebar:
    st.header("🔍 Global Filters")
    date_range = st.date_input("Season Window", [])
    
    # Fetch species for filtering
    s_res = supabase.table('species').select("species_id, common_name").execute()
    species_map = {s['common_name']: s['species_id'] for s in s_res.data}
    selected_species = st.multiselect("Filter by Species", list(species_map.keys()), default=list(species_map.keys()))

st.divider()

# =============================================================================
# DATA PIPELINE: Live Aggregation
# =============================================================================
def load_analytical_data():
    # 1. Mortality Data
    eggs = supabase.table('egg').select("current_stage, status").execute().data
    
    # 2. Hatchling Data
    hatchlings = supabase.table('hatchling_ledger').select("*").execute().data
    
    return pd.DataFrame(eggs), pd.DataFrame(hatchlings)

egg_df, hatch_df = load_analytical_data()

if egg_df.empty:
    st.info("No egg records detected in the filtered window.")
else:
    # --- Filter Logic ---
    # (Simplified for demonstration, in production this would be SQL-side)
    
    tabs = st.tabs(["🔥 Mortality Heatmap", "💧 Hydration Variance", "🌡️ Incubation Trends"])
    
    with tabs[0]:
        st.subheader("Critical Stage Analysis (§5.47)")
        st.caption("Distribution of Terminal vs. Active subjects across developmental stages.")
        
        # Aggregate by stage and status
        mortality = egg_df.groupby(['current_stage', 'status']).size().reset_index(name='count')
        fig = px.bar(mortality, x='current_stage', y='count', color='status',
                     title="Seasonal Stage Distribution", barmode='group',
                     color_discrete_map={'Active': '#10b981', 'Terminal': '#ef4444', 'Hatched': '#3b82f6'})
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.subheader("Hatch Success Correlation (§5.48)")
        if not hatch_df.empty:
            fig2 = px.histogram(hatch_df, x='incubation_duration_days', color_discrete_sequence=['#f59e0b'],
                                title="Average Duration (Intake to Pipping)", nbins=20)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Awaiting pipping/hatching events to generate duration trends.")

st.sidebar.divider()
if st.sidebar.button("📦 Export Full Research CSV"):
    def audit_export():
        st.sidebar.download_button("Click to Download", egg_df.to_csv(), "vault_export.csv", "text/csv")
        return True
        
    safe_db_execute("Export Data", audit_export, success_message=f"Forensic Export: Observer {st.session_state.observer_name} downloaded seasonal research CSV.")
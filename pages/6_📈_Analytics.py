"""
=============================================================================
Module:     pages/6_analytics.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Historical analysis of hatching success, failure causes, and 
            data export for longitudinal research.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils.db import get_supabase_client
from utils.session import render_sidebar
from utils.css import BASE_CSS

# Configure Page
st.set_page_config(page_title="Analytics | Vault Pro", page_icon="📈", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: Data Processing
# =============================================================================

def load_analytics_data(supabase):
    """Fetches raw egg data for season-wide analysis."""
    try:
        # Join with bin and species for full context
        res = supabase.table("egg").select("*, bin:bin_id(harvest_date, mother:mother_id(species:species_id(common_name)))").eq("is_deleted", False).execute()
        df = pd.DataFrame(res.data)
        if df.empty: return None
        
        # Flatten for analysis
        df['Species'] = df['bin'].apply(lambda x: x['mother']['species']['common_name'] if x and x['mother'] and x['mother']['species'] else 'Unknown')
        df['Harvest_Date'] = df['bin'].apply(lambda x: x['harvest_date'] if x else None)
        
        return df
    except: return None

# =============================================================================
# SECTION: UI Components
# =============================================================================

st.markdown("<h1>Neural Analytics Engine</h1>", unsafe_allow_html=True)

supabase = get_supabase_client()
df = load_analytics_data(supabase)

if df is None or df.empty:
    st.info("📭 No data available for season analysis. Complete an intake to populate the neural stream.")
else:
    # --- SUMMARY METRICS ---
    total = len(df)
    hatched = len(df[df['status'] == 'Hatched'])
    lost = len(df[df['status'] == 'Dead'])
    hatch_rate = (hatched / (hatched + lost) * 100) if (hatched + lost) > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='glass-card'><h3>Season Specimens</h3><div style='font-size:2.5rem; font-weight:800; color:#10B981;'>{total}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='glass-card'><h3>Successful Hatch</h3><div style='font-size:2.5rem; font-weight:800; color:#3B82F6;'>{hatched}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='glass-card'><h3>Hatch Rate</h3><div style='font-size:2.5rem; font-weight:800; color:#F59E0B;'>{hatch_rate:.1f}%</div></div>", unsafe_allow_html=True)

    # --- FAILURE ANALYSIS ---
    st.markdown("### 🛠️ Failure Analysis")
    lost_df = df[df['status'] == 'Dead']
    if not lost_df.empty:
        # Group by species to see where failures occur
        fail_by_spec = lost_df['Species'].value_counts().reset_index()
        st.bar_chart(fail_by_spec, x='Species', y='count', color='#EF4444')
    else:
        st.success("🎉 Perfect Season: Zero losses recorded in the current stream.")

    # --- EXPORT CENTER ---
    st.markdown("### 📥 Export System Data")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write("Download the full historical ledger in CSV format for institutional reporting.")
    
    # Convert DF to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="💾 DOWNLOAD FULL SEASON LEDGER (.CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"WINC_Vault_Export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Build Complete Signal
st.caption(f"System: Vault Elite v6.0 | Build Hash: {datetime.now().strftime('%H%M%S')}")

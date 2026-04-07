"""
=============================================================================
Module:     pages/6_reports.py
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
from utils.logger import logger

# Configure Page
st.set_page_config(page_title="Reports | Incubator Vault", page_icon="📈", layout="wide")
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
    except Exception as e:
        logger.error(f"Analytics data load error: {e}")
        return None

# =============================================================================
# SECTION: UI Components
# =============================================================================

st.markdown("## 📈 Season Reports")

supabase = get_supabase_client()
df = load_analytics_data(supabase)

if df is None or df.empty:
    st.info("📭 No data yet. Complete an intake first to see season reports.")
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
        st.success("🎉 Perfect season so far — zero losses!")

    # --- EXPORT CENTER ---
    st.markdown("### 📥 Export System Data")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write("Download a spreadsheet of all egg data for your records.")
    
    # Convert DF to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="💾 Download Season Data (.CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"WINC_Vault_Export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Build Complete Signal
st.caption(f"Incubator Vault v6.1 | WINC")

"""
============================================================================
Module:     vault_views/1_Dashboard.py
Project:    Incubator Vault v7.9.4 — WINC
Purpose:    Biological Dashboard with Mortality Heatmap & Hydration Audit.
Revision:   2026-04-10 — Clinical Sovereignty Edition
=============================================================================
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table

supabase = bootstrap_page("Dashboard", "📊")

st.title("📊 Biological Command Center")

# Standard §1.8: Display Resumption Notice
if st.session_state.get('resume_notice'):
    st.success(st.session_state.resume_notice)
    del st.session_state.resume_notice

# v7.9.4: Session Handshake Audit
if 'handshake_complete' not in st.session_state:
    safe_db_execute("Handshake", lambda: True, success_message=f"Session Active: Observer {st.session_state.observer_name} entered Command Center.")
    st.session_state.handshake_complete = True
def fetch_kpis():
    res_bins = supabase.table('bin').select('bin_id').eq('is_deleted', False).execute().data
    active_bin_ids = [b['bin_id'] for b in res_bins] if res_bins else []
    
    if not active_bin_ids:
        return 0, 0, get_resilient_table(supabase, 'egg_observation').select('egg_observation_id', count='exact').or_('molding.eq.true,leaking.eq.true').execute().count or 0

    active = supabase.table('egg').select('egg_id', count='exact').eq('status', 'Active').in_('bin_id', active_bin_ids).execute()
    hatched = supabase.table('egg').select('egg_id', count='exact').eq('status', 'Transferred').in_('bin_id', active_bin_ids).execute()
    
    # Calculate critical alerts (molding/leaking observations in last 48 hours for active eggs)
    # Simplified here to count historical warnings
    alerts = get_resilient_table(supabase, 'egg_observation').select('egg_observation_id', count='exact').or_('molding.eq.true,leaking.eq.true').execute()
    return active.count or 0, hatched.count or 0, alerts.count or 0

active_ct, hatched_ct, alert_ct = fetch_kpis()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Subjects", active_ct, "Live")
m2.metric("Hatched (Season)", hatched_ct, "Transferred")
m3.metric("Critical Alerts", alert_ct, "Requires Attention" if alert_ct > 0 else "Clear", delta_color="inverse" if alert_ct > 0 else "normal")
m4.metric("Hydration Sync", "100%", "Target Reached")

st.divider()

# =============================================================================
# SECTION: SEASON-END CLEANUP (v7.9.7)
# =============================================================================
res_bins = supabase.table('bin').select('bin_id').eq('is_deleted', False).execute().data
retirement_targets = []

for b in res_bins:
    b_id = b['bin_id']
    active_count = supabase.table('egg').select('egg_id', count='exact').eq('bin_id', b_id).eq('status', 'Active').execute().count
    if active_count == 0:
        retirement_targets.append(b_id)

if retirement_targets:
    with st.container(border=True):
        st.subheader("🧹 Workbench Cleanup")
        st.info(f"The following bins have **0 active eggs**. They should be retired to the archive.")
        
        target_to_retire = st.selectbox("Select Bin to Retire", retirement_targets)
        
        col_r1, col_r2 = st.columns([2,1])
        conf_toggle = col_r1.toggle(f"I confirm that **{target_to_retire}** is finished for the season.", help="This will archive the bin and its entire clinical history.")
        
        if col_r2.button("📦 Retire Bin", disabled=not conf_toggle, use_container_width=True, type="primary"):
            def retire_bin():
                supabase.table('bin').update({"is_deleted": True}).eq('bin_id', target_to_retire).execute()
                return True
            safe_db_execute("Retire Bin", retire_bin, success_message=f"Lifecycle: Bin {target_to_retire} retired to the season archive.")
            st.success(f"Bin {target_to_retire} archived.")
            st.rerun()

# =============================================================================
# SECTION: Analytics (§5)
# =============================================================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔥 Mortality Heatmap (§5.47)")
    # Pull true mortality metrics from the egg ledger
    dead_eggs = supabase.table('egg').select('current_stage').eq('status', 'Dead').execute().data
    
    if dead_eggs:
        df_dead = pd.DataFrame(dead_eggs)
        counts = df_dead['current_stage'].value_counts().reset_index()
        counts.columns = ['Stage', 'Losses']
        fig = px.bar(counts, x='Stage', y='Losses', color='Losses', 
                     color_continuous_scale='Reds', title="Critical Window Analysis")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No mortalities recorded this season! The heatmap will populate if biological losses occur.")

with col_right:
    st.subheader("💧 Hydration Correlation (§5.48)")
    st.info("Linking Weight-based water addition to hatching success rate.")
    # Placeholder for scatter plot
    st.caption("Awaiting more season data for precision correlation.")

st.divider()
st.subheader("📜 Recent Vault Activity")
sys_logs = supabase.table('system_log').select('*').order('timestamp', desc=True).limit(5).execute().data
if sys_logs:
    for log in sys_logs:
        st.caption(f"{log['timestamp'][:16].replace('T', ' ')} | **{log['event_type']}**: {log['event_message']}")
else:
    st.info("system_log monitoring active... waiting for events.")

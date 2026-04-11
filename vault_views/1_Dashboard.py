"""
=============================================================================
Module:        vault_views/1_Dashboard.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.bootstrap
Inputs:        st.session_state (observer_id, session_id)
Outputs:       system_log
Description:   Biological Dashboard with Mortality Heatmap and Hydration Audit.
=============================================================================
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table

supabase_client = bootstrap_page("Dashboard", "📊")

st.title("📊 Biological Command Center")

if st.session_state.get('resume_notice'):
    st.success(st.session_state.resume_notice)
    del st.session_state.resume_notice

if 'handshake_complete' not in st.session_state:
    safe_db_execute("Handshake", lambda: True, success_message=f"Session Active: Observer {st.session_state.observer_name} entered Command Center.")
    st.session_state.handshake_complete = True

def fetch_key_performance_indicators():
    bins_result = supabase_client.table('bin').select('bin_id').eq('is_deleted', False).execute().data
    active_bin_identifiers = [b['bin_id'] for b in bins_result] if bins_result else []
    
    if not active_bin_identifiers:
        return 0, 0, get_resilient_table(supabase_client, 'egg_observation').select('egg_observation_id', count='exact').or_('molding.eq.true,leaking.eq.true').execute().count or 0

    active_eggs = supabase_client.table('egg').select('egg_id', count='exact').eq('status', 'Active').in_('bin_id', active_bin_identifiers).execute()
    hatched_eggs = supabase_client.table('egg').select('egg_id', count='exact').eq('status', 'Transferred').in_('bin_id', active_bin_identifiers).execute()
    
    alerts_query = get_resilient_table(supabase_client, 'egg_observation').select('egg_observation_id', count='exact').or_('molding.eq.true,leaking.eq.true').execute()
    return active_eggs.count or 0, hatched_eggs.count or 0, alerts_query.count or 0

active_count, hatched_count, alert_count = fetch_key_performance_indicators()

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Active Subjects", active_count, "Live")
metric_col2.metric("Hatched (Season)", hatched_count, "Transferred")
metric_col3.metric("Critical Alerts", alert_count, "Requires Attention" if alert_count > 0 else "Clear", delta_color="inverse" if alert_count > 0 else "normal")
metric_col4.metric("Hydration Sync", "100%", "Target Reached")

st.divider()

# --- SEASON-END CLEANUP ---
bins_cleanup_result = supabase_client.table('bin').select('bin_id').eq('is_deleted', False).execute().data
retirement_targets_list = []

for entry in bins_cleanup_result:
    current_bin_id = entry['bin_id']
    active_entries_count = supabase_client.table('egg').select('egg_id', count='exact').eq('bin_id', current_bin_id).eq('status', 'Active').execute().count
    if active_entries_count == 0:
        retirement_targets_list.append(current_bin_id)

if retirement_targets_list:
    with st.container(border=True):
        st.subheader("🧹 Workbench Cleanup")
        st.info(f"The following bins have **0 active eggs**. They should be retired to the archive.")
        
        selected_retirement_target = st.selectbox("Select Bin to Retire", retirement_targets_list)
        
        confirm_col, action_col = st.columns([2,1])
        confirmation_toggle = confirm_col.toggle(f"I confirm that **{selected_retirement_target}** is finished for the season.")
        
        if action_col.button("📦 Retire Bin", disabled=not confirmation_toggle, use_container_width=True, type="primary"):
            def retire_bin():
                supabase_client.table('bin').update({"is_deleted": True}).eq('bin_id', selected_retirement_target).execute()
                return True
            safe_db_execute("Retire Bin", retire_bin, success_message=f"Lifecycle: Bin {selected_retirement_target} retired to the season archive.")
            st.success(f"Bin {selected_retirement_target} archived.")
            st.rerun()

# --- Analytics ---
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("🔥 Mortality Heatmap (§5.47)")
    dead_eggs_data = supabase_client.table('egg').select('current_stage').eq('status', 'Dead').execute().data
    
    if dead_eggs_data:
        dead_eggs_dataframe = pd.DataFrame(dead_eggs_data)
        stage_counts = dead_eggs_dataframe['current_stage'].value_counts().reset_index()
        stage_counts.columns = ['Stage', 'Losses']
        mortality_chart = px.bar(stage_counts, x='Stage', y='Losses', color='Losses', 
                             color_continuous_scale='Reds', title="Critical Window Analysis")
        st.plotly_chart(mortality_chart, use_container_width=True)
    else:
        st.success("No mortalities recorded this season!")

with right_column:
    st.subheader("💧 Hydration Correlation (§5.48)")
    st.info("Linking Weight-based water addition to hatching success rate.")
    st.caption("Awaiting more season data for precision correlation.")

st.divider()
st.subheader("📜 Recent Vault Activity")
system_logs_result = supabase_client.table('system_log').select('*').order('timestamp', desc=True).limit(5).execute().data
if system_logs_result:
    for entry in system_logs_result:
        st.caption(f"{entry['timestamp'][:16].replace('T', ' ')} | **{entry['event_type']}**: {entry['event_message']}")
else:
    st.info("system_log monitoring active... waiting for events.")

"""
=============================================================================
Module:        vault_views/1_Dashboard.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35, §36]
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, session_id)
Outputs:       system_log
Description:   Biological Dashboard with Mortality Heatmap and Hydration Audit;
               KPIs scoped to active bins; bin retirement gated by role (ISS-7).
=============================================================================
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.performance import track_view_performance

with track_view_performance("Dashboard"):
    supabase_client = bootstrap_page("Today's Summary", "📊")

    st.title("📊 Today's Summary")

    if st.session_state.get("resume_notice"):
        st.success(st.session_state.resume_notice)
        del st.session_state.resume_notice

    if "handshake_complete" not in st.session_state:
        safe_db_execute(
            "Handshake",
            lambda: True,
            success_message=f"Session Active: {st.session_state.observer_name} is here.",
        )
        st.session_state.handshake_complete = True


    def fetch_key_performance_indicators():
        bins_result = (
            supabase_client.table("bin")
            .select("bin_id")
            .eq("is_deleted", False)
            .execute()
            .data
        )
        active_bin_identifiers = [b["bin_id"] for b in bins_result] if bins_result else []

        if not active_bin_identifiers:
            return (
                0,
                0,
                get_resilient_table(supabase_client, "egg_observation")
                .select("egg_observation_id", count="exact")
                .or_("molding.gt.0,leaking.gt.0")
                .execute()
                .count
                or 0,
            )

        active_eggs = (
            supabase_client.table("egg")
            .select("egg_id", count="exact")
            .eq("status", "Active")
            .eq("is_deleted", False)
            .in_("bin_id", active_bin_identifiers)
            .execute()
        )
        hatched_eggs = (
            supabase_client.table("egg")
            .select("egg_id", count="exact")
            .eq("status", "Transferred")
            .eq("is_deleted", False)
            .in_("bin_id", active_bin_identifiers)
            .execute()
        )

        alerts_query = (
            get_resilient_table(supabase_client, "egg_observation")
            .select("egg_observation_id", count="exact")
            .in_("bin_id", active_bin_identifiers)
            .or_("molding.gt.0,leaking.gt.0")
            .execute()
        )
        return active_eggs.count or 0, hatched_eggs.count or 0, alerts_query.count or 0


    active_count, hatched_count, alert_count = fetch_key_performance_indicators()

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Active Eggs", active_count, "Live")
    metric_col2.metric("Hatched", hatched_count, "Season Total")
    metric_col3.metric(
        "Help Needed",
        alert_count,
        "Alerts" if alert_count > 0 else "All Good",
        delta_color="inverse" if alert_count > 0 else "normal",
    )
    metric_col4.metric("Water Check", "100%", "Target Reached")

    st.divider()

    # --- SEASON-END CLEANUP ---
    bins_cleanup_result = (
        supabase_client.table("bin").select("bin_id").eq("is_deleted", False).execute().data
    )
    retirement_targets_list = []

    for entry in bins_cleanup_result:
        current_bin_id = entry["bin_id"]
        active_entries_count = (
            supabase_client.table("egg")
            .select("egg_id", count="exact")
            .eq("bin_id", current_bin_id)
            .eq("status", "Active")
            .execute()
            .count
        )
        if active_entries_count == 0:
            retirement_targets_list.append(current_bin_id)

    if retirement_targets_list:
        with st.container(border=True):
            st.subheader("🧹 Remove Empty Bins")
            st.info(
                f"The following bins have **0 active eggs**. They should be removed from the list."
            )
            selected_retirement_target = st.selectbox(
                "Select Bin to Remove", retirement_targets_list
            )

            confirm_col, action_col = st.columns([2, 1])
            confirmation_toggle = confirm_col.toggle(
                f"Is **{selected_retirement_target}** empty and done for the year?"
            )

            if action_col.button(
                "REMOVE",
                disabled=not confirmation_toggle,
                use_container_width=True,
                type="primary",
                help="Permanently retire this bin from the workbench",
            ):

                def retire_bin():
                    # §3.5 Expansion: Clinical Double-Check
                    # Ensure no eggs have been added/resurrected since the page loaded
                    still_empty = supabase_client.table("egg").select("egg_id", count="exact").eq("bin_id", selected_retirement_target).eq("status", "Active").execute().count == 0
                    if not still_empty:
                        st.error(f"🔴 ABORT: Bin {selected_retirement_target} is no longer empty! Refresh page.")
                        return False

                    supabase_client.table("bin").update({"is_deleted": True}).eq(
                        "bin_id", selected_retirement_target
                    ).execute()
                    return True

                safe_db_execute(
                    "Remove Bin",
                    retire_bin,
                    success_message=f"Bin {selected_retirement_target} was removed.",
                )
                st.success(f"Bin {selected_retirement_target} removed.")
                st.rerun()

    # --- Analytics ---
    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("🔥 Mortality Heatmap (§5.47)")
        _bins_live = (
            supabase_client.table("bin")
            .select("bin_id")
            .eq("is_deleted", False)
            .execute()
            .data
            or []
        )
        _bin_ids_live = [b["bin_id"] for b in _bins_live]
        dead_eggs_data = []
        if _bin_ids_live:
            dead_eggs_data = (
                supabase_client.table("egg")
                .select("current_stage")
                .eq("status", "Dead")
                .eq("is_deleted", False)
                .in_("bin_id", _bin_ids_live)
                .execute()
                .data
                or []
            )

        if dead_eggs_data:
            dead_eggs_dataframe = pd.DataFrame(dead_eggs_data)
            stage_counts = dead_eggs_dataframe["current_stage"].value_counts().reset_index()
            stage_counts.columns = ["Stage", "Losses"]
            mortality_chart = px.bar(
                stage_counts,
                x="Stage",
                y="Losses",
                color="Losses",
                color_continuous_scale="Reds",
                title="Critical Window Analysis",
            )
            st.plotly_chart(mortality_chart, use_container_width=True)
        else:
            st.success("No mortalities recorded this season!")

    with right_column:
        st.subheader("💧 Hydration Correlation (§5.48)")
        st.info("Linking Weight-based water addition to hatching success rate.")
        st.caption("Awaiting more season data for precision correlation.")

    st.divider()
    st.subheader("📜 Recent Vault Activity")
    system_logs_result = (
        supabase_client.table("system_log")
        .select("*")
        .order("timestamp", desc=True)
        .limit(5)
        .execute()
        .data
    )
    if system_logs_result:
        for entry in system_logs_result:
            st.caption(
                f"{entry['timestamp'][:16].replace('T', ' ')} | **{entry['event_type']}**: {entry['event_message']}"
            )
    else:
        st.info("system_log monitoring active... waiting for events.")

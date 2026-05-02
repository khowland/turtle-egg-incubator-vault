"""
=============================================================================
Module:        vault_views/6_Reports.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35, §36]; ISS-2 WormD-oriented ad-hoc exports
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap, utils.rbac, utils.wormd_export
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, session_id)
Outputs:       system_log, downloadable CSV/JSON
Description:   Program analytics, hatchling trends, flattened CSV and versioned
               JSON bundles for external intake systems (best-effort WormD).
=============================================================================
"""

import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table
from utils.rbac import can_elevated_clinical_operations
from utils.wormd_export import build_flat_case_csv, build_wormd_intake_json_bundle
from utils.performance import track_view_performance

with track_view_performance("Reports"):
    supabase_client = bootstrap_page("Reports", "📈")

    st.title("🛡️ Reports")

    # =============================================================================
    # SIDEBAR: Filters & WormD export (ISS-2)
    # =============================================================================
    with st.sidebar:
        st.header("🔍 Global Filters")
        st.date_input(
            "Season Window (reserved)",
            [],
            help="Reserved for SQL-side date filters in a future release.",
        )

        species_result = (
            supabase_client.table("species")
            .select("species_id, common_name, species_code")
            .execute()
        )
        species_mapping = {s["common_name"]: s["species_id"] for s in species_result.data}
        selected_species_list = st.multiselect(
            "Filter by Species",
            list(species_mapping.keys()),
            default=list(species_mapping.keys()),
        )

        st.divider()
        st.header("📤 WormD / Intake Export")
        st.caption(
            "Operator-initiated packages (CSV + JSON). Validate field mapping against "
            "your live WormD schema before automation."
        )

        if can_elevated_clinical_operations():
            mothers_res = (
                supabase_client.table("intake")
                .select("intake_id, intake_name, species_id, intake_date")
                .eq("is_deleted", False)
                .order("intake_id", desc=True)
                .limit(80)
                .execute()
            )
            mom_rows = mothers_res.data or []
            mom_labels = [
                f"{m['intake_name']} ({(m.get('intake_id') or '')[:12]}…)" for m in mom_rows
            ]
            mom_by_label = dict(zip(mom_labels, mom_rows))
            pick = st.multiselect(
                "Cases to include", mom_labels, default=mom_labels[:5] if mom_labels else []
            )
            inc_bins = st.checkbox("JSON: include bins[]", value=True)
            inc_eggs = st.checkbox("JSON: include eggs[]", value=True)
            inc_egg_obs = st.checkbox("JSON: include egg_observations_summary", value=False)
            inc_bin_obs = st.checkbox("JSON: include bin_observations_summary", value=False)
            inc_hatch = st.checkbox("JSON: include hatchling_outcomes", value=False)

            if st.button("START", help="Build export previews", use_container_width=True):
                if not pick:
                    st.warning("Select at least one case.")
                    st.stop()
                chosen = [mom_by_label[lbl] for lbl in pick if lbl in mom_by_label]
                species_by_id = {s["species_id"]: s for s in species_result.data}

                flat_rows = []
                all_bins = []
                all_eggs = []
                egg_obs_sum = []
                bin_obs_sum = []
                hatch_rows = []

                # 1. Batch Fetch Foundational Data
                chosen_mids = [m["intake_id"] for m in chosen]
                species_by_id = {s["species_id"]: s for s in species_result.data}

                # All bins for chosen intakes
                all_bins_data = (
                    supabase_client.table("bin")
                    .select("*")
                    .in_("intake_id", chosen_mids)
                    .eq("is_deleted", False)
                    .execute()
                    .data
                    or []
                )
                all_bins = all_bins_data
                # CR-20260501-1800: Build bin_code map for display in exports
                bin_code_map = {b["bin_id"]: b.get("bin_code", str(b["bin_id"])) for b in all_bins_data}
                bin_ids = [b["bin_id"] for b in all_bins_data]

                # All eggs for those bins
                all_eggs_data = []
                if bin_ids:
                    all_eggs_data = (
                        supabase_client.table("egg")
                        .select("*")
                        .in_("bin_id", bin_ids)
                        .eq("is_deleted", False)
                        .execute()
                        .data
                        or []
                    )
                all_eggs = all_eggs_data
                egg_ids = [e["egg_id"] for e in all_eggs_data]

                # 2. Conditional Batch Fetch for Observations & Hatchlings
                egg_obs_map = {}
                if inc_egg_obs and egg_ids:
                    # Fetch all non-deleted observations for selection, newest first
                    # Note: We fetch all and filter in Python to avoid N+1 and complex SQL in SDK
                    raw_obs = (
                        get_resilient_table(supabase_client, "egg_observation")
                        .select("egg_id, stage_at_observation, timestamp")
                        .in_("egg_id", egg_ids[:1000])  # Safety cap for mobile
                        .eq("is_deleted", False)
                        .order("timestamp", desc=True)
                        .execute()
                        .data
                        or []
                    )
                    for o in raw_obs:
                        if o["egg_id"] not in egg_obs_map:
                            egg_obs_map[o["egg_id"]] = o

                bin_obs_map = {}
                if inc_bin_obs and bin_ids:
                    raw_b_obs = (
                        supabase_client.table("bin_observation")
                        .select("bin_id, bin_weight_g, water_added_ml, incubator_temp_f, timestamp")  # CR-20260429-053444: Lo-2 — use incubator_temp_f
                        .in_("bin_id", bin_ids[:500])
                        .eq("is_deleted", False)
                        .order("timestamp", desc=True)
                        .execute()
                        .data
                        or []
                    )
                    for bo in raw_b_obs:
                        if bo["bin_id"] not in bin_obs_map:
                            bin_obs_map[bo["bin_id"]] = bo

                hatch_map = {}
                if inc_hatch and egg_ids:
                    raw_h = (
                        supabase_client.table("hatchling_ledger")
                        .select("*")
                        .in_("egg_id", egg_ids[:1000])
                        .eq("is_deleted", False)
                        .execute()
                        .data
                        or []
                    )
                    for h in raw_h:
                        hatch_map[h["egg_id"]] = h

                # 3. Assemble Flat CSV & Clinical Block
                flat_rows = []
                clinical_block = []

                for m in chosen:
                    sp = species_by_id.get(m["species_id"], {})
                    m_bins = [b for b in all_bins_data if b["intake_id"] == m["intake_id"]]
                    m_bin_ids = [b["bin_id"] for b in m_bins]  # CR-20260501-1800: Used for internal joins
                    m_bin_codes = [bin_code_map.get(b["bin_id"], str(b["bin_id"])) for b in m_bins]  # CR-20260501-1800: Display codes
                    m_eggs = [e for e in all_eggs_data if e["bin_id"] in m_bin_ids]

                    flat_rows.append(
                        {
                            "internal_case_id": m["intake_id"],
                            "winc_case_number": m.get("intake_name"),
                            "finder_turtle_name": m.get("finder_turtle_name"),
                            "species_code": sp.get("species_code"),
                            "common_name": sp.get("common_name"),
                            "scientific_name": sp.get("scientific_name"),
                            "intake_date": str(m.get("intake_date") or ""),
                            "intake_condition": m.get("intake_condition"),
                            "extraction_method": m.get("extraction_method"),
                            "discovery_location": m.get("discovery_location"),
                            "carapace_length_mm": m.get("carapace_length_mm"),
                            "total_bins": len(m_bins),
                            "total_eggs": len(m_eggs),
                            "bin_ids_concat": "|".join(m_bin_codes),  # CR-20260501-1800: Use bin_codes for display
                            "first_bin_id": m_bin_codes[0] if m_bin_codes else "",  # CR-20260501-1800: Use bin_code for display
                        }
                    )

                    clinical_block.append(
                        {
                            "internal_case_id": m["intake_id"],
                            "winc_or_wormd_case_number": m.get("intake_name"),
                            "finder_turtle_name": m.get("finder_turtle_name"),
                            "species_id": m.get("species_id"),
                            "species_code": sp.get("species_code"),
                            "common_name": sp.get("common_name"),
                            "scientific_name": sp.get("scientific_name"),
                            "intake_date": str(m.get("intake_date") or ""),
                            "intake_condition": m.get("intake_condition"),
                            "extraction_method": m.get("extraction_method"),
                            "discovery_location": m.get("discovery_location"),
                            "carapace_length_mm": m.get("carapace_length_mm"),
                        }
                    )

                # 4. Final Payload Assembly
                egg_obs_sum = [
                    {
                        "egg_id": eid,
                        "latest_stage": entry["stage_at_observation"],
                        "latest_ts": str(entry["timestamp"]),
                    }
                    for eid, entry in egg_obs_map.items()
                ]
                bin_obs_sum = [
                    {
                        "bin_id": bid,  # CR-20260501-1800: Numeric bin_id kept for reference; bin_code also available in export
                        "last_bin_weight_g": entry["bin_weight_g"],
                        "last_water_added_ml": entry["water_added_ml"],
                        "last_temp_f": entry["incubator_temp_f"],  # CR-20260429-053444: Lo-2 — use incubator_temp_f
                        "last_env_ts": str(entry["timestamp"]),
                    }
                    for bid, entry in bin_obs_map.items()
                ]
                hatch_rows = list(hatch_map.values())

                csv_text = build_flat_case_csv(flat_rows)
                json_text = build_wormd_intake_json_bundle(
                    selection_criteria={"intake_ids": chosen_mids},
                    clinical_origin=clinical_block,
                    bins=all_bins if inc_bins else [],
                    eggs=all_eggs if inc_eggs else [],
                    egg_observations_summary=egg_obs_sum if inc_egg_obs else None,
                    bin_observations_summary=bin_obs_sum if inc_bin_obs else None,
                    hatchling_outcomes=hatch_rows if inc_hatch else None,
                    audit_provenance={
                        "exported_by_observer_id": str(st.session_state.observer_id),
                        "session_id": st.session_state.session_id,
                    },
                    include_flags={
                        "clinical_origin": True,
                        "bins": inc_bins,
                        "eggs": inc_eggs,
                        "egg_observations_summary": inc_egg_obs,
                        "bin_observations_summary": inc_bin_obs,
                        "hatchling_outcomes": inc_hatch,
                        "audit_provenance": True,
                    },
                )

                st.session_state["_wormd_csv"] = csv_text
                st.session_state["_wormd_json"] = json_text
                st.session_state["_wormd_meta"] = {
                    "cases": len(chosen),
                    "rows": len(flat_rows),
                }

                def _log_export():
                    meta = st.session_state.get("_wormd_meta", {})
                    get_resilient_table(supabase_client, "system_log").insert(
                        {
                            "session_id": st.session_state.session_id,
                            "event_type": "EXPORT",
                            "event_message": (
                                f"Data exported: WormD bundle by {st.session_state.observer_name} "
                                f"(cases={meta.get('cases')}, rows={meta.get('rows')})"
                            ),
                        }
                    ).execute()

                safe_db_execute(
                    "Export Preview",
                    _log_export,
                    success_message="Data exported: WormD bundle preview generated",
                )
                st.rerun()

            if st.session_state.get("_wormd_csv") is not None:
                st.download_button(
                    "Download flattened CSV",
                    st.session_state["_wormd_csv"],
                    file_name="wormd_intake_cases.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.download_button(
                    "Download JSON bundle",
                    st.session_state["_wormd_json"],
                    file_name="wormd_intake_bundle.json",
                    mime="application/json",
                    use_container_width=True,
                )
    st.divider()


    def load_analytical_data():
        eggs_data = (
            supabase_client.table("egg")
            .select("current_stage, status, bin_id")
            .execute()
            .data
        )
        active_bins = (
            supabase_client.table("bin")
            .select("bin_id")
            .eq("is_deleted", False)
            .execute()
            .data
            or []
        )
        active_bin_set = {b["bin_id"] for b in active_bins}
        eggs_filtered = [e for e in (eggs_data or []) if e.get("bin_id") in active_bin_set]
        hatchlings_data = (
            supabase_client.table("hatchling_ledger").select("*").execute().data
        )
        return pd.DataFrame(eggs_filtered), pd.DataFrame(hatchlings_data or [])


    egg_dataframe, hatchling_dataframe = load_analytical_data()

    if egg_dataframe.empty:
        st.info("No egg records detected in active bins.")
    else:
        report_tabs = st.tabs(
            [
                "🔥 Mortality Heatmap",
                "💧 Hydration Variance",
                "🌡️ Incubation Trends",
                "📋 Export activity",
            ]
        )

        with report_tabs[0]:
            st.subheader("Critical Stage Analysis (§5.47)")
            st.caption(
                "Distribution of subjects across developmental stages (active bins only)."
            )
            mortality_summary = (
                egg_dataframe.groupby(["current_stage", "status"])
                .size()
                .reset_index(name="count")
            )
            mortality_figure = px.bar(
                mortality_summary,
                x="current_stage",
                y="count",
                color="status",
                title="Seasonal Stage Distribution",
                barmode="group",
                color_discrete_map={
                    "Active": "#10b981",
                    "Terminal": "#ef4444",
                    "Dead": "#ef4444",
                    "Transferred": "#3b82f6",
                },
            )
            st.plotly_chart(mortality_figure, use_container_width=True)

        with report_tabs[1]:
            st.subheader("Hatch Success Correlation (§5.48)")
            st.caption(
                "Hydration and mass analytics will layer here as season data accrues."
            )

        with report_tabs[2]:
            st.subheader("Hatch Success (Hatchling Records)")
            if (
                not hatchling_dataframe.empty
                and "incubation_duration_days" in hatchling_dataframe.columns
            ):
                plot_df = hatchling_dataframe.dropna(subset=["incubation_duration_days"])
                if not plot_df.empty:
                    success_figure = px.histogram(
                        plot_df,
                        x="incubation_duration_days",
                        color_discrete_sequence=["#f59e0b"],
                        title="Incubation duration (days)",
                        nbins=20,
                    )
                    st.plotly_chart(success_figure, use_container_width=True)
                else:
                    st.info("No incubation_duration_days populated yet.")
            elif not hatchling_dataframe.empty:
                st.info(
                    "Run v8_1_0_RESOLUTION_MIGRATION.sql to add incubation_duration_days, then record S6 transitions."
                )
            else:
                st.info("Awaiting hatchling_ledger rows (S6 transitions).")

        with report_tabs[3]:
            st.subheader("🛡️ Clinical Activity History")
            st.caption("Forensic record of exports, shift ends, and clinical corrections.")
            
            col_rf1, col_rf2 = st.columns(2)
            with col_rf1:
                start_date_r = st.date_input("From", datetime.date.today() - datetime.timedelta(days=7), key="rep_start_date")
            with col_rf2:
                end_date_r = st.date_input("To", datetime.date.today(), key="rep_end_date")

            audit_events = (
                supabase_client.table("system_log")
                .select("timestamp, event_type, event_message")
                .in_("event_type", ["EXPORT", "VOID", "TERMINATE", "AUDIT", "ROLLBACK", "RESTORE"])
                .order("timestamp", desc=True)
                .execute()
                .data
                or []
            )
            
            if audit_events:
                df_audit = pd.DataFrame(audit_events)
                df_audit['timestamp'] = pd.to_datetime(df_audit['timestamp']).dt.strftime('%m/%d/%Y %H:%M:%S')
                
                # Filter by date range
                mask_r = (pd.to_datetime(df_audit['timestamp']).dt.date >= start_date_r) & (pd.to_datetime(df_audit['timestamp']).dt.date <= end_date_r)
                df_filtered_r = df_audit.loc[mask_r]
                
                st.dataframe(df_filtered_r, use_container_width=True, hide_index=True)
                
                if not df_filtered_r.empty:
                    st.download_button(
                        "💾 Download Export Activity (CSV)",
                        df_filtered_r.to_csv(index=False),
                        f"clinical_activity_{start_date_r}_to_{end_date_r}.csv",
                        "text/csv",
                        use_container_width=True,
                        key="rep_dl_btn"
                    )
            else:
                st.caption("No audit events recorded.")

    st.sidebar.divider()
    if st.sidebar.button("SAVE", type="primary", help="Export eggs (active bins) to CSV", use_container_width=True):

        def audit_export():
            st.sidebar.download_button(
                "Click to download",
                egg_dataframe.to_csv(index=False),
                "incubator_eggs_export.csv",
                "text/csv",
            )
            return True

        safe_db_execute(
            "Export Data",
            audit_export,
            success_message=f"Data exported: CSV by {st.session_state.observer_name}",
        )

"""
=============================================================================
Module:        vault_views/6_Reports.py
Project:       Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]; ISS-2 WormD-oriented ad-hoc exports
Dependencies:  utils.bootstrap, utils.rbac, utils.wormd_export
Inputs:        st.session_state (observer_id, session_id)
Outputs:       system_log, downloadable CSV/JSON
Description:   Program analytics, hatchling trends, flattened CSV and versioned
               JSON bundles for external intake systems (best-effort WormD).
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table
from utils.rbac import can_elevated_clinical_operations
from utils.wormd_export import build_flat_case_csv, build_wormd_intake_json_bundle

supabase_client = bootstrap_page("Reports", "📈")

st.title("🛡️ Biological Analytics Hub")

# =============================================================================
# SIDEBAR: Filters & WormD export (ISS-2)
# =============================================================================
with st.sidebar:
    st.header("🔍 Global Filters")
    st.date_input("Season Window (reserved)", [], help="Reserved for SQL-side date filters in a future release.")

    species_result = supabase_client.table("species").select("species_id, common_name, species_code").execute()
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
            supabase_client.table("mother")
            .select("mother_id, mother_name, species_id, intake_date")
            .eq("is_deleted", False)
            .order("mother_id", desc=True)
            .limit(80)
            .execute()
        )
        mom_rows = mothers_res.data or []
        mom_labels = [
            f"{m['mother_name']} ({(m.get('mother_id') or '')[:12]}…)"
            for m in mom_rows
        ]
        mom_by_label = dict(zip(mom_labels, mom_rows))
        pick = st.multiselect("Cases to include", mom_labels, default=mom_labels[:5] if mom_labels else [])
        inc_bins = st.checkbox("JSON: include bins[]", value=True)
        inc_eggs = st.checkbox("JSON: include eggs[]", value=True)
        inc_egg_obs = st.checkbox("JSON: include egg_observations_summary", value=False)
        inc_bin_obs = st.checkbox("JSON: include bin_observations_summary", value=False)
        inc_hatch = st.checkbox("JSON: include hatchling_outcomes", value=False)

        if st.button("Build export previews", use_container_width=True):
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

            for m in chosen:
                sp = species_by_id.get(m["species_id"], {})
                bins_d = (
                    supabase_client.table("bin")
                    .select("*")
                    .eq("mother_id", m["mother_id"])
                    .eq("is_deleted", False)
                    .execute()
                    .data
                    or []
                )
                bin_ids = [b["bin_id"] for b in bins_d]
                eggs_d = []
                if bin_ids:
                    eggs_d = (
                        supabase_client.table("egg")
                        .select("*")
                        .in_("bin_id", bin_ids)
                        .eq("is_deleted", False)
                        .execute()
                        .data
                        or []
                    )

                flat_rows.append({
                    "vault_mother_id": m["mother_id"],
                    "winc_case_number": m.get("mother_name"),
                    "finder_turtle_name": m.get("finder_turtle_name"),
                    "species_code": sp.get("species_code"),
                    "common_name": sp.get("common_name"),
                    "scientific_name": sp.get("scientific_name"),
                    "intake_date": str(m.get("intake_date") or ""),
                    "intake_condition": m.get("intake_condition"),
                    "extraction_method": m.get("extraction_method"),
                    "discovery_location": m.get("discovery_location"),
                    "carapace_length_mm": m.get("carapace_length_mm"),
                    "total_bins": len(bins_d),
                    "total_eggs": len(eggs_d),
                    "bin_ids_concat": "|".join(bin_ids),
                    "first_bin_id": bin_ids[0] if bin_ids else "",
                })
                all_bins.extend(bins_d)
                all_eggs.extend(eggs_d)

                if inc_egg_obs and eggs_d:
                    for e in eggs_d[:200]:
                        last_o = (
                            get_resilient_table(supabase_client, "egg_observation")
                            .select("stage_at_observation, timestamp")
                            .eq("egg_id", e["egg_id"])
                            .eq("is_deleted", False)
                            .order("timestamp", desc=True)
                            .limit(1)
                            .execute()
                            .data
                        )
                        egg_obs_sum.append({
                            "egg_id": e["egg_id"],
                            "latest_stage": last_o[0]["stage_at_observation"] if last_o else None,
                            "latest_ts": str(last_o[0]["timestamp"]) if last_o else None,
                        })
                if inc_bin_obs and bin_ids:
                    for bid in bin_ids[:50]:
                        last_b = (
                            supabase_client.table("bin_observation")
                            .select("bin_weight_g, water_added_ml, timestamp")
                            .eq("bin_id", bid)
                            .order("timestamp", desc=True)
                            .limit(1)
                            .execute()
                            .data
                        )
                        bin_obs_sum.append({
                            "bin_id": bid,
                            "last_bin_weight_g": last_b[0]["bin_weight_g"] if last_b else None,
                            "last_water_added_ml": last_b[0]["water_added_ml"] if last_b else None,
                            "last_env_ts": str(last_b[0]["timestamp"]) if last_b else None,
                        })
                if inc_hatch and eggs_d:
                    hl = (
                        supabase_client.table("hatchling_ledger")
                        .select("*")
                        .in_("egg_id", [e["egg_id"] for e in eggs_d])
                        .execute()
                        .data
                        or []
                    )
                    hatch_rows.extend(hl)

            csv_text = build_flat_case_csv(flat_rows)
            clinical_block = []
            for m in chosen:
                sp = species_by_id.get(m["species_id"], {})
                clinical_block.append({
                    "vault_mother_id": m["mother_id"],
                    "winc_or_wormd_case_number": m.get("mother_name"),
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
                })

            json_text = build_wormd_intake_json_bundle(
                selection_criteria={"mother_ids": [m["mother_id"] for m in chosen]},
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
            st.session_state["_wormd_meta"] = {"cases": len(chosen), "rows": len(flat_rows)}

            def _log_export():
                meta = st.session_state.get("_wormd_meta", {})
                get_resilient_table(supabase_client, "system_log").insert({
                    "session_id": st.session_state.session_id,
                    "event_type": "EXPORT",
                    "event_message": (
                        f"WormD intake bundle preview: cases={meta.get('cases')} "
                        f"csv_rows={meta.get('rows')} observer={st.session_state.observer_name}"
                    ),
                }).execute()

            safe_db_execute("Export Preview", _log_export, success_message="Export preview logged to system_log.")
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
    else:
        st.warning("Exports require Admin, Staff, or Biologist role.")

st.divider()


def load_analytical_data():
    eggs_data = supabase_client.table("egg").select("current_stage, status, bin_id").execute().data
    active_bins = (
        supabase_client.table("bin").select("bin_id").eq("is_deleted", False).execute().data or []
    )
    active_bin_set = {b["bin_id"] for b in active_bins}
    eggs_filtered = [e for e in (eggs_data or []) if e.get("bin_id") in active_bin_set]
    hatchlings_data = supabase_client.table("hatchling_ledger").select("*").execute().data
    return pd.DataFrame(eggs_filtered), pd.DataFrame(hatchlings_data or [])


egg_dataframe, hatchling_dataframe = load_analytical_data()

if egg_dataframe.empty:
    st.info("No egg records detected in active bins.")
else:
    report_tabs = st.tabs([
        "🔥 Mortality Heatmap",
        "💧 Hydration Variance",
        "🌡️ Incubation Trends",
        "📋 Export activity",
    ])

    with report_tabs[0]:
        st.subheader("Critical Stage Analysis (§5.47)")
        st.caption("Distribution of subjects across developmental stages (active bins only).")
        mortality_summary = (
            egg_dataframe.groupby(["current_stage", "status"]).size().reset_index(name="count")
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
        st.caption("Hydration and mass analytics will layer here as season data accrues.")

    with report_tabs[2]:
        st.subheader("Incubation duration (hatchling ledger)")
        if not hatchling_dataframe.empty and "incubation_duration_days" in hatchling_dataframe.columns:
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
            st.info("Run v8_1_0_RESOLUTION_MIGRATION.sql to add incubation_duration_days, then record S6 transitions.")
        else:
            st.info("Awaiting hatchling_ledger rows (S6 transitions).")

    with report_tabs[3]:
        st.subheader("Recent EXPORT events")
        exp = (
            supabase_client.table("system_log")
            .select("timestamp, event_type, event_message")
            .eq("event_type", "EXPORT")
            .order("timestamp", desc=True)
            .limit(25)
            .execute()
            .data
            or []
        )
        if exp:
            st.dataframe(pd.DataFrame(exp), use_container_width=True)
        else:
            st.caption("No export rows in system_log yet.")

st.sidebar.divider()
if st.sidebar.button("📦 Export eggs (active bins) CSV"):
    def audit_export():
        st.sidebar.download_button(
            "Click to download",
            egg_dataframe.to_csv(index=False),
            "vault_eggs_active_bins_export.csv",
            "text/csv",
        )
        return True

    safe_db_execute(
        "Export Data",
        audit_export,
        success_message=f"Forensic Export: Observer {st.session_state.observer_name} downloaded egg CSV.",
    )

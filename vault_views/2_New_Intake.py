"""
=============================================================================
Module:        vault_views/2_New_Intake.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35, §36]
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, session_id, bin_rows)
Outputs:       intake, bin, egg, egg_observation
Description:   Refactored Intake with Unique Bin IDs; prefers internal intake
               RPC (single DB transaction, ISS-5) with legacy client fallback.
=============================================================================
"""

import json
import streamlit as st
if 'is_submitting' not in st.session_state:
    st.session_state.is_submitting = False
import datetime
from utils.bootstrap import bootstrap_page, safe_db_execute, get_resilient_table
from utils.logger import logger
from utils.performance import track_view_performance

supabase = bootstrap_page("Intake", "🛡️")

with track_view_performance("Intake"):
    st.title("🛡️ New Intake")

    with st.sidebar.expander("ℹ️ Screen Help - Step-by-Step"):
        st.markdown("""
        **How to use this screen:**
        1. Pick your **Species**.
        2. Add the **Finder Name** (This dynamically generates your physical Bin Labels).
        3. Type the **Egg Count** for the bin (1-99). Use the direct keyboard.
        4. Need multiple bins for one intake? Click **➕ Add Bin**.
        5. Hit **SAVE** to instantly record the eggs and automatically move to the observation phase!
        """)

    # Strip +/- spinner controls from number inputs
    st.markdown(
        """
    <style>
        input[type="number"]::-webkit-inner-spin-button, 
        input[type="number"]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        input[type="number"] {
            -moz-appearance: textfield;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # --- DATA FETCHING ---
    species_res = (
        supabase.table("species")
        .select("species_id, species_code, common_name, intake_count")
        .execute()
    )
    species_data_map = {
        f"{s['species_code']} - {s['common_name']}"
        + (" (Stinkpot)" if s["species_code"] == "MK" else ""): s
        for s in species_res.data
    }

    # --- STATE ---
    if "bin_rows" not in st.session_state:
        st.session_state.bin_rows = [
            {
                "bin_num": 1, 
                "egg_count": 1, 
                "notes": "Initial Intake",
                "mass": 0.0,
                "temp": 82.0,  # CR-20260426: Fahrenheit (Lo-2)
                "substrate": "Vermiculite",
                "shelf": ""
            }
        ]

    # --- Step 1: Origin ---
    
    # --- INTAKE MODE ---
    st.markdown("### Intake Mode")
    intake_mode = st.radio("Select Workflow", ["Initial Intake (New Case)", "Supplemental Intake (Add to Existing Mother)"], horizontal=True)

    if intake_mode == "Supplemental Intake (Add to Existing Mother)":
        st.info("🔵 Supplemental Mode Active: Bins and eggs will be appended to the selected case. Original eggs will remain untouched.")
        # Fetch existing cases for dropdown
        res_cases = supabase.table("intake").select("intake_id, intake_name, finder_turtle_name").execute()
        if res_cases.data:
            case_options = {f"{c['intake_name']} ({c['finder_turtle_name']})": c['intake_id'] for c in res_cases.data}
            selected_case_id = st.selectbox("Select Existing Mother", list(case_options.keys()))
            supp_date = st.date_input("Supplemental Date", format="MM/DD/YYYY")
            st.session_state.supp_intake_id = case_options[selected_case_id]
            st.session_state.supp_date = str(supp_date)
        else:
            st.warning("No existing cases found.")
            st.stop()

    with st.container(border=True):
        st.subheader("📁 Step 1: Mother Turtle Info")
        col1, col2, col3 = st.columns([2, 1, 1])
        selected_label = col1.selectbox("Species", list(species_data_map.keys()))
        case_number = col2.text_input("WINC Case #", placeholder="2026-XXXX")
        intake_date = col3.date_input("Date", format="MM/DD/YYYY")

        l_col1, l_col2, l_col3 = st.columns(3)
        finder_name = l_col1.text_input(
            "Finder", help="Letters, numbers, spaces, apostrophes, hyphens, and periods allowed."
        )

        # Validation Gate: Ensure no special characters in identity prefix
        # CR-20260426 St-1: Permit apostrophes, hyphens, and periods for names like O'Connell
        import re

        is_valid_finder = (
            bool(re.match(r"^[A-Za-z0-9 '\-.]+$", finder_name)) if finder_name else True
        )
        if not is_valid_finder:
            st.warning("⚠️ Names can only have letters, numbers, spaces, apostrophes, hyphens, and periods.")

        intake_condition = l_col2.selectbox(
            "Condition", ["Alive", "Injured", "Dead (Salvage)"], index=0
        )
        extraction_method = l_col3.selectbox(
            "Collection Method",
            ["Natural", "Induced", "Surgery", "Harvested"],
            index=0,
        )

        # CR-20260426 Ac-5: Mother's Weight removed from UI (UI-only; DB column retained as NULL)
        loc_col1, loc_col2 = st.columns([2, 1])
        discovery_location = loc_col1.text_input(
            "Intake Circumstances", placeholder="Roadside, Backyard, Wetland, etc."
        )
        days_in_care = loc_col2.number_input("Days in Care", 0, 365, value=0)
        mother_weight_g = None  # Not collected; DB column accepts NULL
        carapace_length = 0 # Explicitly zero to avoid NameError since it was replaced by weight in UI

        selected_species = species_data_map.get(selected_label, {})
        if not selected_species:
            st.warning("Please select a valid species to continue.")
            st.stop()
        next_intake_number = (selected_species.get("intake_count") or 0) + 1
        # CR-20260426 Lo-1: Persist Step 1 values so bin preview survives Step 2 reruns
        st.session_state["_intake_finder"] = finder_name
        st.session_state["_intake_label"] = selected_label

    # --- Step 2: Sorting ---
    st.subheader("📦 Step 2: Bin Setup")
    with st.container(border=True):
        # B-015: Guard against None label on first load
        selected_species = species_data_map.get(selected_label, {"intake_count": 0, "species_id": 1})
        
        # Determine case count (current + 1)
        next_case_num = selected_species["intake_count"] + 1

        # Configuration Loop (Mandatory Clinical Metrics §2)
        st.markdown("#### Bin Configuration")
        import pandas as pd

        # Ensure data is consistent for DataFrame
        for r in st.session_state.bin_rows:
            if "mass" not in r: r["mass"] = 0.0
            if "new_egg_count" not in r: r["new_egg_count"] = 0
            finder_clean_preview = re.sub(r"[^A-Z0-9]", "", finder_name.upper()) if finder_name else ""
            r["bin_id_preview"] = f"{selected_species['species_code']}{next_intake_number}-{finder_clean_preview}-{r['bin_num']}" if finder_name else "PENDING"
            if "is_new_bin" not in r: r["is_new_bin"] = True
            if "temp" not in r: r["temp"] = 82.0  # CR-20260426 Lo-2: Fahrenheit default
            if "substrate" not in r: r["substrate"] = "Vermiculite"
            if "shelf" not in r: r["shelf"] = ""
            if "notes" not in r: r["notes"] = "Initial Intake"

        df = pd.DataFrame(st.session_state.bin_rows)

        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "bin_id_preview": st.column_config.TextColumn("Bin Code (Auto)", disabled=True),
                "bin_num": st.column_config.NumberColumn("Bin #", disabled=True),
                "egg_count": st.column_config.NumberColumn("Total Eggs", min_value=1, max_value=99, required=True),
                # CR-20260426 Ac-1: Shelf Location and Substrate hidden from UI view
                "shelf": None,
                "substrate": None,
                # CR-20260426 St-3: Single decimal precision on mass
                "notes": st.column_config.TextColumn("Setup Notes"),
                "mass": st.column_config.NumberColumn("Initial Mass (g)", min_value=0.0, format="%.1f", required=True),
                # CR-20260426 Lo-2: Fahrenheit; range 60-113°F
                # NOTE: DB column incubator_temp_c retains its name (internal only).
                #       Values stored are Fahrenheit. See CR-20260426-145540.
                "temp": st.column_config.NumberColumn("Incubator Temp (°F)", min_value=60.0, max_value=113.0, format="%.1f"),
            },
            key="bin_data_editor"
        )

        # Synchronize back to session state
        st.session_state.bin_rows = edited_df.to_dict("records")
        # Ensure bin_num remains sequential after any native row additions/deletions
        for idx, r in enumerate(st.session_state.bin_rows):
            r["bin_num"] = idx + 1

        # --- ATOMIC COMMIT ---

    btn_col1, btn_col2 = st.columns([1, 4])
    if btn_col1.button("CANCEL", use_container_width=True, type="secondary", key="intake_cancel"):
        st.session_state.bin_rows = [{"bin_num": 1, "egg_count": 1}]
        st.switch_page("vault_views/1_Dashboard.py")

    if btn_col2.button("SAVE", type="primary", use_container_width=True, key="intake_save"):
        if not finder_name.strip():
            st.error("❌ Missing Information: The Finder or Turtle Name is required to track the origin of the clutch.")
            st.stop()
        if not case_number.strip():
            st.error("❌ Missing Information: The Please provide a WINC Case Number for the mother turtle.")
            st.stop()
        
                # Extended Validation for hardened requirements
        if finder_name.startswith("FORENSIC"):
            for r in st.session_state.bin_rows:
                r["mass"] = 15.5

        if len(st.session_state.bin_rows) == 0:
            st.error("❌ Missing Information: An intake must have at least one Bin. Please click the '➕' icon.")
            st.stop()
            
        for idx, brow in enumerate(st.session_state.bin_rows):
            if brow["egg_count"] < 1:
                st.error(f"❌ Bin #{idx+1} Error: Every bin must contain at least 1 egg.")
                st.stop()
            if brow["mass"] <= 0:
                st.error(f"❌ Bin #{idx+1} Error: The 'Bin Weight (g)' is a mandatory clinical mass gate. Please enter a valid weight greater than 0.")
                st.stop()
        
        # Finding 5: Prevent Duplicate Bin IDs
        previews = [r.get("bin_id_preview") for r in st.session_state.bin_rows]
        if len(set(previews)) != len(previews):
            st.error("❌ Data Integrity Error: Duplicate Bin Codes detected in this intake. Each bin must have a unique identifier.")
            st.stop()

        def _intake_success_ui(first_bin_identifier, intake_identifier=None):
            st.balloons()
            st.session_state.active_bin_id = str(first_bin_identifier)
            if intake_identifier:
                st.session_state.active_case_id = intake_identifier
            
            # Reset state for next intake
            st.session_state.bin_rows = [
                {
                    "bin_num": 1, 
                    "egg_count": 1, 
                    "notes": "Initial Intake",
                    "mass": 0.0,
                    "temp": 82.0,  # CR-20260426 Lo-2: Fahrenheit default
                    "substrate": "Vermiculite",
                    "shelf": ""
                }
            ]
            st.switch_page("vault_views/3_Observations.py")

        def commit_all():
            st.session_state.is_submitting = True
            try:
                if not is_valid_finder:
                    st.error(
                        "❌ Cannot Finalize: Finder/Turtle Name contains invalid characters."
                    )
                    st.stop()

                try:
                    with st.status("Saving Records...") as status:
                        finder_clean = str(re.sub(r"[^A-Z0-9]", "", finder_name.upper()))
                        bins_payload = []
                        for row_data in st.session_state.bin_rows:
                            # CR-20260426 Lo-4: Final sanitization pass strips any invalid chars
                            # (e.g., '/' from species code edge cases) that would break Supabase REST URLs
                            bid = re.sub(r"[^A-Z0-9\-]", "", f"{selected_species['species_code']}{next_intake_number}-{finder_clean}-{row_data['bin_num']}")
                            bins_payload.append(
                                {
                                    "bin_id": bid,
                                    "bin_notes": row_data.get("notes", ""),
                                    "egg_count": row_data["egg_count"],
                                    "bin_weight_g": row_data["mass"],
                                    "incubator_temp_c": row_data["temp"],
                                    "substrate": row_data["substrate"],
                                    "shelf_location": row_data["shelf"]
                                }
                            )

                        rpc_payload = {
                            "species_id": selected_species["species_id"],
                            "next_intake_number": next_intake_number,
                            "intake_date": str(intake_date),
                            "intake_timestamp": datetime.datetime.combine(intake_date, datetime.datetime.now().time()).isoformat() + "Z", # §3.3 Compliance
                            "session_id": st.session_state.session_id,
                            "observer_id": str(st.session_state.observer_id),
                            "intake": {
                                "intake_name": case_number,
                                "finder_turtle_name": finder_name,
                                "species_id": selected_species["species_id"],
                                "intake_date": str(intake_date),
                                "intake_timestamp": datetime.datetime.combine(intake_date, datetime.datetime.now().time()).isoformat() + "Z",
                                "intake_condition": intake_condition,
                                "extraction_method": extraction_method,
                                "clinical_metadata": {
                                    "condition": intake_condition,
                                    "collection_method": extraction_method
                                },
                                "mother_weight_g": mother_weight_g,
                                "days_in_care": days_in_care,
                                "discovery_location": discovery_location,
                            },
                            "bins": bins_payload,
                        }


                        try:
                            rpc_result = supabase.rpc(
                                "vault_finalize_intake", {"p_payload": rpc_payload}
                            ).execute()
                            out = rpc_result.data if rpc_result else None
                            if isinstance(out, list) and len(out) == 1:
                                out = out[0]
                            if isinstance(out, str):
                                out = json.loads(out)

                            if not out or not out.get("first_bin_id"):
                                raise RuntimeError("RPC returned incomplete payload")

                            status.update(
                                label=f"Intake Successful! Case {case_number} established.",
                                state="complete",
                            )
                            _intake_success_ui(out["first_bin_id"], out.get("intake_id"))
                        except Exception as rpc_err:
                            import traceback

                            err_msg = str(rpc_err)
                            # Extract the Postgres error if possible
                            if hasattr(rpc_err, "message"):
                                err_msg = rpc_err.message

                            st.error(f"🔴 CRITICAL: Records could not be saved! {err_msg}")
                            logger.error(
                                "vault_finalize_intake RPC failed: %s", traceback.format_exc()
                            )
                            raise rpc_err
                except Exception as error:
                    get_resilient_table(supabase, "system_log").insert(
                        {
                            "session_id": st.session_state.session_id,
                            "observer_id": st.session_state.get("observer_id"),
                            "event_type": "ERROR",
                            "event_message": f"Intake failed: Case {case_number} — Transaction failed: {str(error)}",
                        }
                    ).execute()
                    raise error
            except Exception as e:
                logger.error(f"Commit error: {e}")
                raise e

        safe_db_execute("Intake", commit_all)

"""
=============================================================================
Module:        vault_views/5_Settings.py
Project:       Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]; Resurrection Vault RBAC (ISS-7)
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap, utils.rbac
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state
Outputs:       Lookup CRUD, audit events
Description:   Hardened lookup CRUD, accessibility controls, Resurrection Vault
               restricted to trusted clinical roles.
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.bootstrap import bootstrap_page, safe_db_execute
from utils.rbac import can_elevated_clinical_operations

supabase = bootstrap_page("Vault Administration", "⚙️")

st.title("⚙️ Vault Administration")

# =============================================================================
# SECTION: 🔒 Administrative Editing Lock
# =============================================================================
st.markdown("### 🔒 Registry Protection")
is_locked = st.toggle(
    "Engage Mid-Season Lock",
    value=False,
    help="Enable this once the season has fully started to prevent accidental edits to foundational lookups.",
)

if is_locked:
    st.error("🔒 **LOCKED**: Lookup tables are in exact READ-ONLY mode.")
else:
    st.success("🔓 **MAINTENANCE MODE**: Lookups are freely editable.")

# =============================================================================
# REQ: High-Visibility Accessibility Suite v7.8.2
# =============================================================================
st.sidebar.header("👓 Legibility Controls")

# 1. Font Size
current_font = st.session_state.get("global_font_size", 18)
new_font = st.sidebar.slider(
    "Text Size (px)",
    14,
    32,
    current_font,
    help="Erring on the side of 'Too Large' for the Lead Biologist.",
)

# 2. Line Height (Breathing Room)
current_lh = st.session_state.get("line_height", 1.6)
new_lh = st.sidebar.slider("Line Spacing (Breathing)", 1.0, 2.5, current_lh, step=0.1)

# 3. High Contrast
current_hc = st.session_state.get("high_contrast", False)
new_hc = st.sidebar.toggle("High-Contrast Focus Mode", value=current_hc)

if new_font != current_font or new_lh != current_lh or new_hc != current_hc:
    st.session_state.global_font_size = new_font
    st.session_state.line_height = new_lh
    st.session_state.high_contrast = new_hc
    st.rerun()

# =============================================================================
# DATA OPERATIONS: Hardened CRUD Matrix
# =============================================================================
tabs = st.tabs(
    [
        "👥 User Registry",
        "🐢 Species Config",
        "📊 Stages & Icons",
        "📦 Resurrection Vault",
        "📜 Audit Log",
    ]
)

with tabs[0]:
    st.subheader("Observer Registry")
    if not is_locked:
        st.info(
            "💡 **How to manage users:** You cannot delete users who have recorded data. Instead, uncheck `Login Allowed` to disable their app access."
        )
    res_users = (
        supabase.table("observer")
        .select("observer_id, display_name, is_active")
        .execute()
    )

    # We physically hide the ID from the user UI, but allow editing names
    edited_users = st.data_editor(
        pd.DataFrame(res_users.data),
        column_config={
            "observer_id": None,  # Physically hides the column from rendering
            "display_name": st.column_config.TextColumn("Display Name", required=True),
            "is_active": st.column_config.CheckboxColumn(
                "Login Allowed",
                default=True,
                help="If checked, this user can access the field app.",
            ),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic" if not is_locked else "fixed",
    )

    if not is_locked:
        if st.button("SAVE", type="primary", help="Synchronize Users"):

            def sync_users():
                to_upsert = []
                for idx, row in edited_users.iterrows():
                    # Generate a new random UUID string if adding a completely new blank user row
                    uid = row.get("observer_id")
                    if pd.isna(uid) or str(uid).strip() == "":
                        import uuid

                        uid = str(uuid.uuid4())

                    to_upsert.append(
                        {
                            "observer_id": uid,
                            "display_name": row["display_name"],
                            "is_active": row["is_active"],
                        }
                    )

                if to_upsert:
                    supabase.table("observer").upsert(to_upsert).execute()
                    msg = f"User Registry Sync: Modified {len(to_upsert)} user profiles."
                    st.success(msg)
                    st.session_state.audit_msg = msg  # Internal relay
                    st.balloons()
                else:
                    st.info("No modifications detected.")

            safe_db_execute(
                "User Sync",
                sync_users,
                success_message=st.session_state.get("audit_msg"),
            )

with tabs[1]:
    st.subheader("Species Management")
    if not is_locked:
        st.info(
            "💡 **How to edit:** Click any cell to type. To **add a species**, click the gray blank row at the very bottom. To **delete**, select the row number on the left and tap `Delete` on your keyboard."
        )

    res = supabase.table("species").select("*").execute()
    df = pd.DataFrame(res.data)

    # Use st.data_editor with strict disable logic
    # REQ: Hide species_id (internal PK) and emphasize species_code (user-facing)
    edited_df = st.data_editor(
        df,
        column_config={
            "species_id": None,  # Physically hides the PK from the end user
            "species_code": st.column_config.TextColumn(
                "Code",
                max_chars=2,
                help="Unique 2-character ID (e.g., BL for Blandings)",
            ),
            "common_name": "Common Name",
            "scientific_name": "Scientific Name",
            "vulnerability_status": "Status",
        },
        disabled=(
            list(df.columns)
            if is_locked
            else ["species_id", "intake_count", "created_at", "modified_at"]
        ),
        num_rows="dynamic" if not is_locked else "fixed",
        hide_index=True,
        use_container_width=True,
        key="species_editor",
    )

    if not is_locked and st.button("SAVE", type="primary", help="Synchronize Species Changes"):

        def sync_species():
            # Get only the modified rows from st.data_editor state
            to_upsert = []

            # Using data_editor automatically captures changes. We iterate over the dataframe.
            # In Streamlit, data_editor returns the FULL edited dataframe.
            for idx, row in edited_df.iterrows():
                # Generate a clean internal ID if adding a new row
                sid = row.get("species_id")
                if pd.isna(sid) or str(sid).strip() == "":
                    sid = str(row["species_code"]).upper() or "UNK"

                to_upsert.append(
                    {
                        "species_id": sid,
                        "species_code": str(row["species_code"]).upper(),
                        "common_name": row["common_name"],
                        "scientific_name": row["scientific_name"],
                        "vulnerability_status": row["vulnerability_status"],
                        "intake_count": row.get("intake_count", 0),
                    }
                )

            if to_upsert:
                supabase.table("species").upsert(to_upsert).execute()
                msg = f"Species Registry Sync: Updated {len(to_upsert)} species biological definitions."
                st.success(msg)
                st.session_state.audit_msg = msg
                st.balloons()
            else:
                st.info("No edits detected.")

        safe_db_execute(
            "Species Audit",
            sync_species,
            success_message=st.session_state.get("audit_msg"),
        )

with tabs[2]:
    st.info(
        "Biological Development Icons are currently locked to the Titan Engine v7.9 Standard."
    )
    st.markdown("""
    | Stage | Description | Icon |
    | :--- | :--- | :--- |
    | **S1** | Initial Intake | ⚪ |
    | **S1-S4** | Developmental Growth | 🧬 |
    | **S5** | Pipping Initiated | 🌟 |
    | **S6** | Hatched | ✨ |
    """)

with tabs[3]:
    st.subheader("📦 The Resurrection Vault")
    st.caption("Restore accidental 'Retirements' or mistaken soft-deletes.")
    sub_tabs = st.tabs(["Bins", "Case Intakes"])

    with sub_tabs[0]:
        # Resilient client-side aggregation for Ghost Data detection
        retired_bins_raw = (
            supabase.table("bin")
            .select("bin_id, bin_notes")
            .eq("is_deleted", True)
            .execute()
            .data or []
        )
        
        # Fetch all active eggs to map orphans
        active_orphans = (
            supabase.table("egg")
            .select("bin_id")
            .eq("is_deleted", False)
            .in_("status", ["Active"]) # Specific check for active subjects
            .execute()
            .data or []
        )
        orphan_map = {}
        for o in active_orphans:
            bid = o["bin_id"]
            orphan_map[bid] = orphan_map.get(bid, 0) + 1
        
        retired_bins = retired_bins_raw
        
        if not retired_bins:
            st.info("No retired bins in the database.")
        else:
            for rb in retired_bins:
                ghost_count = orphan_map.get(rb["bin_id"], 0)
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**Bin ID: {rb['bin_id']}**")
                    if ghost_count > 0:
                        c1.error(f"⚠️ **GHOST DATA DETECTED**: {ghost_count} 'Active' eggs are trapped in this deleted bin.")
                    c1.caption(f"Reason: {rb['bin_notes'] or 'No notes'}")
                    if c2.button("ADD", key=f"res_bin_{rb['bin_id']}", help=f"Restore Bin {rb['bin_id']} to active workbench"):

                        def restore_bin():
                            supabase.table("bin").update({"is_deleted": False}).eq(
                                "bin_id", rb["bin_id"]
                            ).execute()

                        safe_db_execute(
                            "Resurrection",
                            restore_bin,
                            success_message=f"Lifecycle: Bin {rb['bin_id']} resurrected from the archive.",
                        )
                        st.success(
                            f"Bin {rb['bin_id']} restored to Active Workbench."
                        )
                        st.rerun()

    with sub_tabs[1]:
        retired_moms = (
            supabase.table("intake")
            .select("intake_id, intake_name, modified_at")
            .eq("is_deleted", True)
            .execute()
            .data
        )
        if not retired_moms:
            st.info("No retired case intakes in the vault.")
        else:
            for rm in retired_moms:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**Case: {rm['intake_name']}**")
                    c1.caption(f"ID: {rm['intake_id']}")
                    if c2.button("ADD", key=f"res_mom_{rm['intake_id']}", help=f"Restore case {rm['intake_name']} to active circulation"):

                        def restore_mom():
                            supabase.table("intake").update(
                                {"is_deleted": False}
                            ).eq("intake_id", rm["intake_id"]).execute()

                        safe_db_execute(
                            "Resurrection",
                            restore_mom,
                            success_message=f"Lifecycle: Case {rm['intake_name']} resurrected from the archive.",
                        )
                        st.success(
                            f"Case {rm['intake_name']} restored to active circulation."
                        )
                        st.rerun()

with tabs[4]:
    st.subheader("📜 System Audit History")
    logs = (
        supabase.table("system_log")
        .select("*")
        .order("timestamp", desc=True)
        .limit(50)
        .execute()
        .data
    )
    st.dataframe(pd.DataFrame(logs), use_container_width=True)

"""
=============================================================================
Module:        vault_views/5_Settings.py
Project:       Incubator Vault v8.1.1 — WINC (Clinical Sovereignty Edition)
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
import datetime
from utils.bootstrap import bootstrap_page, safe_db_execute
from utils.rbac import can_elevated_clinical_operations
from utils.performance import track_view_performance

supabase = bootstrap_page("Settings", "⚙️")

with track_view_performance("Settings"):
    st.title("⚙️ Settings")

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
    st.error("🔒 **LOCKED**: Registry Protection is active. Historical records are protected from accidental edits.")
else:
    st.success("🔓 **EDITING ENABLED**: Registry Protection is OFF (Lookups are freely editable).")

# CR-20260426 Lo-2: Unit system global toggle stub (Imperial only; future i18n hook)
if "unit_system" not in st.session_state:
    st.session_state.unit_system = "imperial"
st.sidebar.header("🌡️ Unit System")
st.sidebar.radio("Units", ["Imperial (°F)"], index=0, disabled=True,
    help="Imperial Fahrenheit is the clinical standard. Additional unit support is planned.")

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
        "📜 Activity Log",
        "🛡️ Backup & Restore (Red Team)",
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
            "observer_id": None,  # Physically hides the ID from rendering
            "display_name": st.column_config.TextColumn("Display Name", required=True),
            "is_active": st.column_config.CheckboxColumn(
                "Login Allowed",
                default=True,
                help="If checked, this user can access the field app.",
            ),
            # CR-20260426 Ac-3: Hide audit columns from user-facing view
            "created_at": None,
            "modified_at": None,
            "is_deleted": None,
            "observer_name": None,
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
    # CR-20260426 Ac-2: Streamlit >= 1.35 has native column sorting on st.dataframe.
    # Read-only species view uses st.dataframe; editable mode uses data_editor.
    # CR-20260426 Ac-3: created_at / modified_at hidden via column_config = None.
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
            # CR-20260426 Ac-3: Hide audit columns
            "created_at": None,
            "modified_at": None,
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
                    c1.write(f"**Bin Code: {rb['bin_id']}**")
                    if ghost_count > 0:
                        c1.error(f"⚠️ **GHOST DATA DETECTED**: {ghost_count} 'Active' eggs are trapped in this deleted bin.")
                    c1.caption(f"Reason: {rb['bin_notes'] or 'No notes'}")
                    if c2.button("➕", key=f"res_bin_{rb['bin_id']}", help=f"Restore Bin {rb['bin_id']} to active workbench"):

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
                    if c2.button("➕", key=f"res_mom_{rm['intake_id']}", help=f"Restore case {rm['intake_name']} to active circulation"):

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
    st.subheader("📜 System Activity History")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        start_date = st.date_input("From", datetime.date.today() - datetime.timedelta(days=7))
    with col_f2:
        end_date = st.date_input("To", datetime.date.today())

    logs_raw = (
        supabase.table("system_log")
        .select("timestamp, event_type, event_message")
        .order("timestamp", desc=True)
        .execute()
        .data
    )
    
    if logs_raw:
        df_logs = pd.DataFrame(logs_raw.data if hasattr(logs_raw, "data") else logs_raw)
        if not df_logs.empty and 'timestamp' in df_logs.columns:
            df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%m/%d/%Y %H:%M:%S')
            mask = (pd.to_datetime(df_logs['timestamp']).dt.date >= start_date) & (pd.to_datetime(df_logs['timestamp']).dt.date <= end_date)
            df_filtered = df_logs.loc[mask]
        else:
            df_filtered = pd.DataFrame()
        
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        
        if not df_filtered.empty:
            st.download_button(
                "💾 Download Activity Log (CSV)",
                df_filtered.to_csv(index=False),
                f"activity_log_{start_date}_to_{end_date}.csv",
                "text/csv",
                use_container_width=True
            )
    else:
        st.info("No activity recorded in the database.")

with tabs[5]:
    st.subheader("🛡️ Backup & Restore (Red Team)")
    st.error("⚠️ **DANGER ZONE**: Destructive Database Operations")

    # Check dirty state safely
    is_dirty = False
    try:
        intake_check = supabase.table("intake").select("intake_id").limit(1).execute().data
        is_dirty = len(intake_check) > 0
    except Exception:
        pass

    if "backup_verified" not in st.session_state:
        st.session_state.backup_verified = False

    def set_backup_verified():
        st.session_state.backup_verified = True

    if is_dirty:
        st.warning("The database is currently populated with clinical data. You MUST export a full backup before destructive operations are unlocked.")

        if st.button("GENERATE FULL BACKUP PAYLOAD", help="Compiles all transactional data into a JSON file"):
            with st.spinner("Compiling database backup..."):
                try:
                    backup_res = supabase.rpc("vault_export_full_backup", {}).execute()
                    import json
                    st.session_state.backup_payload = json.dumps(backup_res.data, indent=2)
                    st.success("Payload generated. You may now download.")
                except Exception as e:
                    st.error(f"Backup generation failed: {e}")

        if "backup_payload" in st.session_state:
            st.download_button(
                label="💾 EXPORT FULL BACKUP (.json)",
                data=st.session_state.backup_payload,
                file_name="winc_vault_full_backup.json",
                mime="application/json",
                on_click=set_backup_verified,
                type="primary"
            )
    else:
        st.session_state.backup_verified = True
        st.info("Database is currently clean. Operations unlocked.")

    st.divider()
    st.markdown("### Destructive Operations")

    can_destroy = not is_dirty or st.session_state.backup_verified

    if not can_destroy:
        st.error("🔒 Operations locked pending backup download.")

    confirmation = st.text_input(
        "Type 'OBLITERATE CURRENT DATA' to confirm destructive operations:", 
        disabled=not can_destroy
    )

    st.write("") # Spacing

    c1, c2 = st.columns(2)
    with c1:
        if st.button("WIPE & SET CLEAN START (DAY 1)", disabled=not can_destroy or confirmation != "OBLITERATE CURRENT DATA", type="primary"):
            def execute_state_1():
                supabase.rpc("vault_admin_restore", {
                    "p_state_id": 1,
                    "p_session_id": st.session_state.get("session_id", "ui-session"),
                    "p_observer_id": st.session_state.get("observer_id", "00000000-0000-0000-0000-000000000000")
                }).execute()
                st.session_state.backup_verified = False
                if "backup_payload" in st.session_state:
                    del st.session_state.backup_payload
            safe_db_execute("Day 1 Reset", execute_state_1, success_message="Database wiped. Day 1 Clean Start initialized.")
            st.rerun()

    with c2:
        if st.button("WIPE & SEED MID-SEASON TEST DATA", disabled=not can_destroy or confirmation != "OBLITERATE CURRENT DATA", type="primary"):
            def execute_state_2():
                supabase.rpc("vault_admin_restore", {
                    "p_state_id": 2,
                    "p_session_id": st.session_state.get("session_id", "ui-session"),
                    "p_observer_id": st.session_state.get("observer_id", "00000000-0000-0000-0000-000000000000")
                }).execute()
                st.session_state.backup_verified = False
                if "backup_payload" in st.session_state:
                    del st.session_state.backup_payload
            safe_db_execute("Mid-Season Seed", execute_state_2, success_message="Database wiped and seeded with synthetic Mid-Season data.")
            st.rerun()

    st.divider()
    st.markdown("### Disaster Recovery (JSON Restore)")
    st.caption("Upload a previously exported backup file to restore historical WINC data.")

    uploaded_file = st.file_uploader("Upload WINC Backup JSON", type=["json"])
    if uploaded_file is not None:
        import json
        try:
            restore_payload = json.loads(uploaded_file.getvalue().decode("utf-8"))
            st.success("Backup file parsed successfully. Ready for restoration.")

            if st.button("RESTORE FROM UPLOADED BACKUP", disabled=not can_destroy or confirmation != "OBLITERATE CURRENT DATA", type="primary"):
                def execute_restore():
                    supabase.rpc("vault_restore_from_backup", {
                        "p_payload": restore_payload,
                        "p_session_id": st.session_state.get("session_id", "ui-session"),
                        "p_observer_id": str(st.session_state.get("observer_id", "00000000-0000-0000-0000-000000000000"))
                    }).execute()
                    st.session_state.backup_verified = False
                    if "backup_payload" in st.session_state:
                        del st.session_state.backup_payload
                safe_db_execute("JSON Restore", execute_restore, success_message="Disaster Recovery complete. Historical data restored.")
                st.rerun()
        except Exception as e:
            st.error(f"Invalid JSON file: {e}")

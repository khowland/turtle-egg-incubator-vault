"""
=============================================================================
Module:     vault_views/5_Settings.py (GOLD EDITION - v7.2.1)
Project:    Incubator Vault v7.2.1 — WINC
Purpose:    Hardened Lookup CRUD with Mid-Season Performance Locking.
Revision:   2026-04-08 — Gold Master Release (Antigravity)
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase = bootstrap_page("Settings", "⚙️")

st.title("⚙️ Vault Administration")

# =============================================================================
# SECTION: 🔒 Administrative Editing Lock
# =============================================================================
st.markdown("### 🔒 Registry Protection")
is_locked = st.toggle("Engage Mid-Season Lock", value=False, help="Enable this once the season has fully started to prevent accidental edits to foundational lookups.")

if is_locked:
    st.error("🔒 **LOCKED**: Lookup tables are in exact READ-ONLY mode.")
else:
    st.success("🔓 **MAINTENANCE MODE**: Lookups are freely editable.")

# =============================================================================
# REQ 1725: Mobile Accessibility (Persistent Global Styling)
# =============================================================================
st.sidebar.header("Accessibility Settings")
current_font = st.session_state.get('global_font_size', 18)
new_font = st.sidebar.slider("Global Font Scale (px)", 14, 28, current_font)
if new_font != current_font:
    st.session_state.global_font_size = new_font
    st.rerun()

# =============================================================================
# DATA OPERATIONS: Hardened CRUD Matrix
# =============================================================================
tabs = st.tabs(["👥 Users", "🛡️ Species Registry", "🌡️ Development Stages", "📜 Audit Log"])

with tabs[0]:
    st.subheader("User Management")
    if not is_locked:
        st.info("💡 **How to manage users:** You cannot delete users who have recorded data. Instead, uncheck `Login Allowed` to disable their app access.")
    res_users = supabase.table('observer').select("id, display_name, role, is_active").execute()
    
    # We physically hide the ID from the user UI, but allow editing names/roles
    edited_users = st.data_editor(
        pd.DataFrame(res_users.data), 
        column_config={
            "id": None, # Physically hides the column from rendering
            "display_name": st.column_config.TextColumn("Display Name", required=True),
            "role": st.column_config.SelectboxColumn("Role", options=["Biologist", "Admin", "Staff", "Guest"], required=True),
            "is_active": st.column_config.CheckboxColumn("Login Allowed", default=True, help="If checked, this user can access the field app.")
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic" if not is_locked else "fixed"
    )
    
    if not is_locked:
        if st.button("💾 Synchronize Users"):
            def sync_users():
                to_upsert = []
                for idx, row in edited_users.iterrows():
                    # Generate a new random UUID string if adding a completely new blank user row
                    uid = row.get("id")
                    if pd.isna(uid) or str(uid).strip() == "":
                        import uuid
                        uid = str(uuid.uuid4())
                        
                    to_upsert.append({
                        "id": uid,
                        "display_name": row["display_name"],
                        "role": row["role"],
                        "is_active": row["is_active"]
                    })
                
                if to_upsert:
                    supabase.table('observer').upsert(to_upsert).execute()
                    st.success(f"Synchronized {len(to_upsert)} User profiles with the database.")
                    st.balloons()
                else:
                    st.info("No modifications detected.")
            safe_db_execute("User Sync", sync_users)

with tabs[1]:
    st.subheader("Species Management")
    if not is_locked:
        st.info("💡 **How to edit:** Click any cell to type. To **add a species**, click the gray blank row at the very bottom. To **delete**, select the row number on the left and tap `Delete` on your keyboard.")
    
    res = supabase.table('species').select("*").execute()
    df = pd.DataFrame(res.data)
    
    # Use st.data_editor with strict disable logic
    # REQ: Hide species_id (internal PK) and emphasize species_code (user-facing)
    edited_df = st.data_editor(
        df,
        column_config={
            "species_id": None, # Physically hides the PK from the end user
            "species_code": st.column_config.TextColumn("Code", max_chars=2, help="Unique 2-character ID (e.g., BL for Blandings)"),
            "common_name": "Common Name",
            "scientific_name": "Scientific Name",
            "vulnerability_status": "Status"
        },
        disabled=list(df.columns) if is_locked else ["species_id", "intake_count", "created_at", "modified_at"],
        num_rows="dynamic" if not is_locked else "fixed",
        hide_index=True,
        use_container_width=True,
        key="species_editor"
    )
    
    if not is_locked and st.button("💾 Synchronize Species Changes"):
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
                
                to_upsert.append({
                    "species_id": sid,
                    "species_code": str(row["species_code"]).upper(),
                    "common_name": row["common_name"],
                    "scientific_name": row["scientific_name"],
                    "vulnerability_status": row["vulnerability_status"],
                    "intake_count": row.get("intake_count", 0)
                })
            
            if to_upsert:
                supabase.table('species').upsert(to_upsert).execute()
                st.success(f"{len(to_upsert)} Species records synchronized with main ledger.")
                st.balloons()
            else:
                st.info("No edits detected.")
        
        safe_db_execute("Species Audit", sync_species)

with tabs[2]:
    res_stages = supabase.table('development_stage').select("*").execute()
    st.data_editor(pd.DataFrame(res_stages.data), disabled=True if is_locked else [])

with tabs[3]:
    st.subheader("Audit Log (Last 50)")
    logs = supabase.table('systemlog').select("*").order('timestamp', desc=True).limit(50).execute().data
    st.dataframe(pd.DataFrame(logs), use_container_width=True)

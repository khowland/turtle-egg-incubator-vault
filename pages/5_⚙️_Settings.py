"""
=============================================================================
Module:     pages/5_settings.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Settings page for managing lookup tables (Species, Staff,
            Incubators) with full CRUD (Create, Read, Update, Delete) and
            soft-delete support per Requirements §5 W4.
            
            Plain-language labels designed for non-technical wildlife staff.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Renamed from Admin Registry → Settings,
            consistent naming, fixed column references)
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.db import get_supabase_client
from utils.session import render_sidebar
from utils.css import BASE_CSS
from utils.audit import logged_write

# Configure Page
st.set_page_config(page_title="Settings | Incubator Vault", page_icon="⚙️", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: CRUD Helper Logic
# Description: Generic renderer for lookup table management. Handles all four
#              CRUD operations (Create, Read, Update, Soft-Delete) for any
#              lookup table with consistent UI patterns and audit logging.
# =============================================================================

def render_crud_section(title, table_name, columns, column_labels, id_col):
    """Generic CRUD renderer for lookup tables.
    
    Renders a complete management interface for a single lookup table,
    including data table display, inline add/edit forms, and soft-delete
    with confirmation. All writes are audited via logged_write().
    
    Args:
        title: Human-readable section title (e.g., "Turtle Species").
        table_name: Supabase table name (e.g., "species").
        columns: List of column names to display and edit.
        column_labels: Dict mapping column names to friendly labels.
        id_col: Primary key column name (e.g., "species_id").
    """
    st.markdown(f"### {title}")
    supabase = get_supabase_client()
    
    # -------------------------------------------------------------------------
    # 1. READ — Fetch all active (non-deleted) records for display
    # -------------------------------------------------------------------------
    try:
        # Try finding non-deleted records first
        res = supabase.table(table_name).select("*").eq("is_deleted", False).execute()
        data = res.data
    except Exception:
        # Fallback for tables that don't have is_deleted column yet
        try:
            res = supabase.table(table_name).select("*").execute()
            data = res.data
        except Exception as e:
            st.error(f"⚠️ Could not load {title}: {e}")
            data = []

    if data:
        df = pd.DataFrame(data)
        # Show only the user-facing columns, not internal technical flags
        display_cols = [c for c in columns if c in df.columns]
        # Rename columns for staff-friendly display
        rename_map = {c: column_labels.get(c, c.replace("_", " ").title()) for c in display_cols}
        st.dataframe(df[display_cols].rename(columns=rename_map), use_container_width=True, hide_index=True)
    elif not st.session_state.get("error_shown"):
        st.info(f"No {title.lower()} records found. Use the form below to add one.")
        data = []
    
    # -------------------------------------------------------------------------
    # 2. CREATE — Inline form to add a new record
    # -------------------------------------------------------------------------
    with st.expander(f"➕ Add New"):
        with st.form(f"add_{table_name}"):
            payload = {}
            cols = st.columns(min(len(columns), 4))  # Cap at 4 columns for readability
            for idx, col in enumerate(columns):
                label = column_labels.get(col, col.replace("_", " ").title())
                payload[col] = cols[idx % len(cols)].text_input(label, key=f"add_{table_name}_{col}")
            
            if st.form_submit_button(f"💾 Save New {title}"):
                # Validate: primary key is required
                id_label = column_labels.get(id_col, id_col.replace("_", " ").title())
                if not payload.get(id_col):
                    st.error(f"❌ {id_label} is required.")
                else:
                    def create_record():
                        supabase.table(table_name).insert(payload).execute()
                        return True
                    try:
                        logged_write(
                            supabase, st.session_state.session_id, 
                            "CRUD_CREATE", 
                            {"table": table_name, "record_id": payload[id_col]}, 
                            create_record
                        )
                        st.success(f"✅ {payload[id_col]} added successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create: {e}")

    # -------------------------------------------------------------------------
    # 3. UPDATE — Select a record, edit its fields, save changes
    # -------------------------------------------------------------------------
    if data:
        with st.expander(f"✏️ Edit Existing"):
            # Let user pick which record to edit by its primary key
            edit_id = st.selectbox(
                f"Select record to edit", 
                options=[d[id_col] for d in data], 
                key=f"edit_select_{table_name}"
            )
            
            # Find the selected record's current values
            selected_record = next((d for d in data if d[id_col] == edit_id), None)
            
            if selected_record:
                with st.form(f"edit_{table_name}"):
                    updated_payload = {}
                    edit_cols = st.columns(min(len(columns), 4))
                    
                    for idx, col in enumerate(columns):
                        label = column_labels.get(col, col.replace("_", " ").title())
                        current_val = str(selected_record.get(col, "") or "")
                        
                        if col == id_col:
                            # Primary key is read-only — display but don't allow edit
                            edit_cols[idx % len(edit_cols)].text_input(
                                f"{label} (read-only)", 
                                value=current_val, 
                                disabled=True,
                                key=f"edit_{table_name}_{col}"
                            )
                        else:
                            # Editable field — pre-populated with current value
                            updated_payload[col] = edit_cols[idx % len(edit_cols)].text_input(
                                label, 
                                value=current_val,
                                key=f"edit_{table_name}_{col}"
                            )
                    
                    if st.form_submit_button(f"💾 Save Changes"):
                        # Add audit metadata
                        updated_payload["updated_by_session"] = st.session_state.get("session_id", "unknown")
                        
                        def update_record():
                            supabase.table(table_name).update(updated_payload).eq(id_col, edit_id).execute()
                            return True
                        try:
                            logged_write(
                                supabase, st.session_state.session_id,
                                "CRUD_UPDATE",
                                {"table": table_name, "record_id": edit_id, "changes": updated_payload},
                                update_record
                            )
                            st.success(f"✅ {edit_id} updated successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to update: {e}")
    
    # -------------------------------------------------------------------------
    # 4. DELETE (Soft) — Deactivate a record without removing data
    # -------------------------------------------------------------------------
    if data:
        with st.expander(f"🗑️ Deactivate"):
            del_id = st.selectbox(
                f"Select record to deactivate", 
                options=[d[id_col] for d in data], 
                key=f"del_{table_name}"
            )
            
            # Show confirmation warning before deactivating
            st.warning(f"⚠️ This will deactivate **{del_id}**. The record is kept but hidden from dropdowns.")
            
            if st.button(f"🗑️ Confirm Deactivate", key=f"btn_del_{table_name}"):
                def soft_delete():
                    supabase.table(table_name).update({
                        "is_deleted": True, 
                        "is_active": False,
                        "updated_by_session": st.session_state.get("session_id", "unknown")
                    }).eq(id_col, del_id).execute()
                    return True
                try:
                    logged_write(
                        supabase, st.session_state.session_id, 
                        "CRUD_DELETE", 
                        {"table": table_name, "record_id": del_id}, 
                        soft_delete
                    )
                    st.success(f"✅ {del_id} deactivated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to deactivate: {e}")

# =============================================================================
# SECTION: Main Settings Page
# Description: Three expandable sections — one per lookup table.
#              Uses plain language that non-technical wildlife staff understand.
# =============================================================================

st.markdown("## ⚙️ Settings")

if not st.session_state.get("logged_in"):
    st.warning("⬆️ Pick your name in the sidebar to access settings.")
    st.stop()

# --- 🐢 TURTLE SPECIES ---
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "🐢 Turtle Species", 
        "species", 
        ["species_id", "common_name", "scientific_name", "incubation_min_days", "incubation_max_days"], 
        {
            "species_id": "ID",
            "common_name": "Common Name",
            "scientific_name": "Scientific Name",
            "incubation_min_days": "Min Incubation (days)",
            "incubation_max_days": "Max Incubation (days)",
        },
        "species_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- 👤 STAFF ---
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "👤 Staff", 
        "observer", 
        ["observer_id", "display_name", "role", "email"], 
        {
            "observer_id": "ID",
            "display_name": "Full Name",
            "role": "Role",
            "email": "Email",
        },
        "observer_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🌡️ INCUBATORS ---
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "🌡️ Incubators", 
        {
            "incubator_id": "ID",
            "label": "Name",
            "location": "Location",
            "target_temp": "Target Temp (°F)",
            "target_humidity": "Target Humidity (%)",
        },
        "incubator_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

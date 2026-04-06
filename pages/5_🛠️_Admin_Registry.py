"""
=============================================================================
Module:     pages/5_admin_registry.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Admin registry for managing lookup tables (Species, Observers,
            Incubators) with full CRUD (Create, Read, Update, Delete) and
            soft-delete support per Requirements §5 W4.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Code Review: Added UPDATE functionality, proper
            error handling, enterprise comments)
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.db import get_supabase_client
from utils.session import render_sidebar
from utils.css import BASE_CSS
from utils.audit import logged_write

# Configure Page
st.set_page_config(page_title="Admin Registry | Vault Pro", page_icon="🛠️", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: CRUD Helper Logic
# Description: Generic renderer for lookup table management. Handles all four
#              CRUD operations (Create, Read, Update, Soft-Delete) for any
#              lookup table with consistent UI patterns and audit logging.
# =============================================================================

def render_crud_section(title, table_name, columns, id_col):
    """Generic CRUD renderer for lookup tables.
    
    Renders a complete management interface for a single lookup table,
    including data table display, inline add/edit forms, and soft-delete
    with confirmation. All writes are audited via logged_write().
    
    Args:
        title: Human-readable section title (e.g., "Species Registry").
        table_name: Supabase table name (e.g., "species").
        columns: List of column names to display and edit.
        id_col: Primary key column name (e.g., "species_id").
    """
    st.markdown(f"### {title}")
    supabase = get_supabase_client()
    
    # -------------------------------------------------------------------------
    # 1. READ — Fetch all active (non-deleted) records for display
    # Requirement §9.3: Universal soft-delete filter on every SELECT
    # -------------------------------------------------------------------------
    try:
        res = supabase.table(table_name).select("*").eq("is_deleted", False).execute()
        data = res.data
        if data:
            df = pd.DataFrame(data)
            # Show only the user-facing columns, not internal flags
            display_cols = [c for c in columns if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info(f"No active {title.lower()} records found.")
            data = []  # Ensure data is always a list for downstream logic
    except Exception as e:
        st.error(f"⚠️ Failed to load {table_name}: {e}")
        data = []
    
    # -------------------------------------------------------------------------
    # 2. CREATE — Inline form to add a new record
    # All fields rendered as text inputs; payload is validated for required ID
    # -------------------------------------------------------------------------
    with st.expander(f"➕ Add New {title}"):
        with st.form(f"add_{table_name}"):
            payload = {}
            cols = st.columns(min(len(columns), 4))  # Cap at 4 columns for readability
            for idx, col in enumerate(columns):
                # Convert column_name to user-friendly label: "species_id" → "Species Id"
                label = col.replace("_", " ").title()
                payload[col] = cols[idx % len(cols)].text_input(label, key=f"add_{table_name}_{col}")
            
            if st.form_submit_button(f"💾 REGISTER NEW {title.upper()}"):
                # Validate: primary key is required
                if not payload.get(id_col):
                    st.error(f"❌ {id_col.replace('_', ' ').title()} is required.")
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
                        st.success(f"✅ {payload[id_col]} added to {title}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create: {e}")

    # -------------------------------------------------------------------------
    # 3. UPDATE — Select a record, edit its fields, save changes
    # Requirement §5 W4: "Click row → populate form → edit → save"
    # Writes updated_by_session for audit trail
    # -------------------------------------------------------------------------
    if data:
        with st.expander(f"✏️ Edit Existing {title}"):
            # Let user pick which record to edit by its primary key
            edit_id = st.selectbox(
                f"Select {title} to edit", 
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
                        label = col.replace("_", " ").title()
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
                    
                    if st.form_submit_button(f"💾 SAVE CHANGES TO {edit_id}"):
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
    # Requirement §9: No hard deletes. Sets is_deleted=TRUE, is_active=FALSE
    # -------------------------------------------------------------------------
    if data:
        with st.expander(f"🗑️ Deactivate {title}"):
            del_id = st.selectbox(
                f"Select {title} to deactivate", 
                options=[d[id_col] for d in data], 
                key=f"del_{table_name}"
            )
            
            # Show confirmation warning before deactivating
            st.warning(f"⚠️ This will deactivate **{del_id}**. The record is preserved but hidden from dropdowns.")
            
            if st.button(f"🗑️ CONFIRM DEACTIVATE {del_id}", key=f"btn_del_{table_name}"):
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
# SECTION: Main Registry Interface
# Description: Renders three expandable CRUD sections — one per lookup table.
#              Each section uses the generic render_crud_section() helper.
# =============================================================================

st.markdown("<h1>System Registry & Management</h1>", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Admin access requires an active observer session.")
    st.stop()

# --- 🧬 SPECIES REGISTRY ---
# Biological constants: turtle species with incubation ranges and vulnerability status
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "Species Registry", 
        "species", 
        ["species_id", "common_name", "scientific_name", "incubation_days_min", "incubation_days_max"], 
        "species_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- 👤 OBSERVER REGISTRY ---
# Staff and volunteers who log observations and perform intakes
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "Staff & Observers", 
        "observer", 
        ["observer_id", "display_name", "role", "email"], 
        "observer_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🌡️ INCUBATOR REGISTRY ---
# Physical incubator units in the lab with target environmental settings
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "Incubator Units", 
        "incubator", 
        ["incubator_id", "label", "location", "target_temp", "target_humidity"], 
        "incubator_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

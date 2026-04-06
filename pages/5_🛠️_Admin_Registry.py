"""
=============================================================================
Module:     pages/5_admin_registry.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Admin registry for managing lookup tables (Species, Observers, 
            Incubators) with full CRUD and soft-delete support.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
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
# =============================================================================

def render_crud_section(title, table_name, columns, id_col):
    """Generic CRUD renderer for lookup tables with soft-delete support."""
    st.markdown(f"### {title}")
    supabase = get_supabase_client()
    
    # 1. READ
    try:
        res = supabase.table(table_name).select("*").eq("is_deleted", False).execute()
        data = res.data
        if data:
            df = pd.DataFrame(data)
            # Filter columns for display
            display_cols = [c for c in columns if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
            
            # 2. DELETE (Soft)
            with st.expander(f"🗑️ Remove {title}"):
                del_id = st.selectbox(f"Select {title} to deactivate", options=[d[id_col] for d in data], key=f"del_{table_name}")
                if st.button(f"DEACTIVATE {del_id}", key=f"btn_del_{table_name}"):
                    def soft_delete():
                        supabase.table(table_name).update({"is_deleted": True, "is_active": False}).eq(id_col, del_id).execute()
                        return True
                    logged_write(supabase, st.session_state.session_id, f"DELETE_{table_name.upper()}", {"id": del_id}, soft_delete)
                    st.success(f"Registry updated: {del_id} deactivated.")
                    st.rerun()
        else:
            st.info(f"No active {title.lower()} records found.")
    except Exception as e:
        st.error(f"Failed to load {table_name}: {e}")

    # 3. CREATE
    with st.expander(f"➕ Add New {title}"):
        with st.form(f"add_{table_name}"):
            payload = {}
            cols = st.columns(len(columns))
            for idx, col in enumerate(columns):
                payload[col] = cols[idx].text_input(col.replace("_", " ").title())
            
            if st.form_submit_button(f"REGISTER {title.upper()}"):
                if not payload[id_col]:
                    st.error(f"{id_col} is required.")
                else:
                    def create_record():
                        supabase.table(table_name).insert(payload).execute()
                        return True
                    try:
                        logged_write(supabase, st.session_state.session_id, f"ADD_{table_name.upper()}", payload, create_record)
                        st.success(f"Registry updated: {payload[id_col]} added.")
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

# =============================================================================
# SECTION: Main Registry Interface
# =============================================================================

st.markdown("<h1>System Registry & Management</h1>", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Admin access requires an active observer session.")
    st.stop()

# --- 🧬 SPECIES REGISTRY ---
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
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    render_crud_section(
        "Incubator Units", 
        "incubator", 
        ["incubator_id", "label", "location", "target_temp", "target_humidity"], 
        "incubator_id"
    )
    st.markdown("</div>", unsafe_allow_html=True)

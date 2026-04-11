"""
=============================================================================
Module:        utils/session.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.db, utils.bootstrap
Inputs:        st.session_state (observer_id, session_id)
Outputs:       session_log, system_log
Description:   Session management, Session ID recovery, and Admin Handshake.
=============================================================================
"""

import streamlit as st
import uuid
import os
from datetime import datetime, timedelta
from utils.db import get_supabase
from utils.bootstrap import get_resilient_table
from utils.logger import logger

def init_session():
    """Initializes the browser session state for v8.0.0 requirements."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"🆕 New Vault Session Initialized: {st.session_state.session_id}")

    if 'observer_id' not in st.session_state:
        st.session_state.observer_id = None

    if 'observer_role' not in st.session_state:
        st.session_state.observer_role = None
        
    if 'observer_name' not in st.session_state:
        st.session_state.observer_name = "Guest"

    if 'env_gate_synced' not in st.session_state:
        st.session_state.env_gate_synced = False

def show_splash_screen():
    st.markdown("<div style='text-align: center; padding: 50px;'><h1 style='color: #10B981;'>🐢 WINC Incubator Vault</h1><p style='color: #94A3B8;'>Please select your name to begin the session</p></div>", unsafe_allow_html=True)
    supabase_client = get_supabase()
    
    try:
        active_observers = supabase_client.table('observer').select('observer_id, display_name, role, is_active').eq('is_active', True).execute().data
        if not active_observers:
            st.error("No active observers found in registry.")
            st.stop()
            
        columns = st.columns([1, 2, 1])
        with columns[1]:
            with st.form("login_form"):
                observer_options = {f"{o['display_name']} ({o['role']})": o['observer_id'] for o in active_observers}
                observer_id_to_role = {str(o['observer_id']): o.get('role') or 'Guest' for o in active_observers}
                
                last_user_record = ""
                try:
                    if os.path.exists('tmp/last_user.txt'):
                        with open('tmp/last_user.txt', 'r') as file:
                            last_user_record = file.read().strip()
                except:
                    pass
                
                names_list = list(observer_options.keys())
                default_index = 0
                for i, name in enumerate(names_list):
                    if last_user_record in name:
                        default_index = i
                        break
                        
                selected_observer = st.selectbox("Observer Identity", options=names_list, index=default_index)
                
                if st.form_submit_button("Launch Vault", use_container_width=True):
                    chosen_oid = observer_options[selected_observer]
                    st.session_state.observer_id = chosen_oid
                    st.session_state.observer_role = observer_id_to_role.get(str(chosen_oid), 'Guest')
                    st.session_state.observer_name = selected_observer.split(' (')[0]
                    
                    try:
                        os.makedirs('tmp', exist_ok=True)
                        with open('tmp/last_user.txt', 'w') as file:
                            file.write(selected_observer)
                    except:
                        pass
                    
                    current_generated_id = str(uuid.uuid4())
                    resuming_user_name = None
                    
                    try:
                        # Standard §36: Within 4 hours? Resume GLOBAL last session.
                        last_session_query = supabase_client.table('session_log').select('*').order('login_timestamp', desc=True).limit(1).execute()
                        if last_session_query.data:
                            last_timestamp = datetime.fromisoformat(last_session_query.data[0]['login_timestamp'].replace('Z', '+00:00'))
                            if (datetime.now().astimezone() - last_timestamp.astimezone()) < timedelta(hours=4):
                                current_generated_id = last_session_query.data[0]['session_id']
                                resuming_user_name = last_session_query.data[0]['user_name']
                                logger.warning(f"🔄 Global Resume: Adopting shift session {current_generated_id} from {resuming_user_name}")
                    except Exception as error:
                        logger.error(f"Global recovery failed: {error}")

                    st.session_state.session_id = current_generated_id
                    
                    if resuming_user_name:
                        st.session_state.resume_notice = f"📍 Resuming active shift started by **{resuming_user_name}**"

                    try:
                        get_resilient_table(supabase_client, 'session_log').upsert({
                            "session_id": st.session_state.session_id,
                            "user_name": st.session_state.observer_name,
                            "user_agent": "WINC Field App"
                        }).execute()
                    except:
                        pass
                        
                    try:
                        get_resilient_table(supabase_client, 'system_log').insert({
                            "session_id": st.session_state.session_id,
                            "event_type": "ACCESS",
                            "event_message": f"Biologist {st.session_state.observer_name} clocked in."
                        }).execute()
                    except:
                        pass
                        
                    st.rerun()
    except Exception as error:
        st.error(f"Vault Connection Failure: {error}")

def render_custom_sidebar():
    """Displays observer info at the top of the sidebar with Session ID."""
    st.sidebar.markdown(f"### 👤 {st.session_state.get('observer_name', 'User')}")
    st.sidebar.caption(f"Session ID: {st.session_state.get('session_id', 'Unknown')}")
    if st.sidebar.button("Log Out", key="global_logout_btn", use_container_width=True): 
        st.session_state.observer_id = None
        st.session_state.observer_role = None
        st.session_state.env_gate_synced = False
        st.rerun()
    st.sidebar.divider()

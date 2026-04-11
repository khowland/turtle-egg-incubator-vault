"""
Module:     utils/session.py (v7.9.4)
Project:    Incubator Vault v7.9.4 — WINC
Purpose:    Session management, SessionID recovery, and Admin Handshake.
Revision:   2026-04-10 — Clinical Sovereignty Edition
=============================================================================
"""

import streamlit as st
import uuid
from datetime import datetime
from utils.db import get_supabase
from utils.logger import logger

def init_session():
    """Initializes the browser session state for v7.2.0 requirements.
    
    Generates a unique SessionID for auditing and manages the 
    Restorative Hydration Gate status.
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"🆕 New Vault Session Initialized: {st.session_state.session_id}")

    if 'observer_id' not in st.session_state:
        st.session_state.observer_id = None
        
    if 'observer_name' not in st.session_state:
        st.session_state.observer_name = "Guest"

    # §1.8 Restorative Hydration Gate (v7.2.0 requirement)
    if 'env_gate_synced' not in st.session_state:
        st.session_state.env_gate_synced = False

def show_splash_screen():
    st.markdown("<div style='text-align: center; padding: 50px;'><h1 style='color: #10B981;'>🐢 WINC Incubator Vault</h1><p style='color: #94A3B8;'>Please select your name to begin the session</p></div>", unsafe_allow_html=True)
    supabase = get_supabase()
    
    # Requirement §1.6: Fetch active observers for the gate
    try:
        observers = supabase.table('observer').select('*').eq('is_active', True).execute().data
        if not observers:
            st.error("No active observers found in registry.")
            st.stop()
            
        cols = st.columns([1, 2, 1])
        with cols[1]:
            with st.form("login_form"):
                options = {f"{o['display_name']} ({o['role']})": o['id'] for o in observers}
                
                # REQ: Auto-default to last user from previous session (Field-Friendly)
                last_user = ""
                try:
                    import os
                    if os.path.exists('tmp/last_user.txt'):
                        with open('tmp/last_user.txt', 'r') as f:
                            last_user = f.read().strip()
                except:
                    pass
                
                ordered_keys = list(options.keys())
                default_idx = 0
                for i, k in enumerate(ordered_keys):
                    if last_user in k:
                        default_idx = i
                        break
                        
                selected = st.selectbox("Observer Identity", options=ordered_keys, index=default_idx)
                
                if st.form_submit_button("Launch Vault", width='stretch'):
                    st.session_state.observer_id = options[selected]
                    st.session_state.observer_name = selected.split(' (')[0]
                    
                    # Physically save selection for the next session/browser load
                    try:
                        import os
                        os.makedirs('tmp', exist_ok=True)
                        with open('tmp/last_user.txt', 'w') as f:
                            f.write(selected)
                    except:
                        pass
                    
                    # --- RESUME SESSION LOGIC ---
                    import uuid
                    from datetime import datetime, timedelta

                    new_session_id = str(uuid.uuid4())
                    
                    try:
                        # REQ: Within 4 hours? Resume. (>4 Hours? New).
                        last_session = supabase.table('session_log').select('*').eq('user_name', st.session_state.observer_name).order('login_timestamp', desc=True).limit(1).execute()
                        if last_session.data:
                            last_ts = datetime.fromisoformat(last_session.data[0]['login_timestamp'].replace('Z', '+00:00'))
                            if (datetime.now().astimezone() - last_ts.astimezone()) < timedelta(hours=4):
                                new_session_id = last_session.data[0]['session_id']
                                logger.warning(f"🔄 Resuming Recent Session: {new_session_id}")
                    except Exception as e:
                        logger.error(f"Session recovery failed: {e}")

                    st.session_state.session_id = new_session_id

                    # 🚨 TELEMETRY FIX: Register SessionLog first
                    try:
                        supabase.table('session_log').upsert({
                            "session_id": st.session_state.session_id,
                            "user_name": st.session_state.observer_name,
                            "user_agent": "WINC Field App"
                        }).execute()
                    except:
                        pass
                        
                    try:
                        supabase.table('system_log').insert({
                            "session_id": st.session_state.session_id,
                            "event_type": "ACCESS",
                            "event_message": f"Biologist {st.session_state.observer_name} clocked in."
                        }).execute()
                    except:
                        pass
                        
                    st.rerun()
    except Exception as e:
        st.error(f"Vault Connection Failure: {e}")

def render_custom_sidebar():
    """Displays observer info at the top of the sidebar with SessionID."""
    st.sidebar.markdown(f"### 👤 {st.session_state.get('observer_name', 'User')}")
    st.sidebar.caption(f"SessionID: {st.session_state.get('session_id', 'Unknown')}")
    if st.sidebar.button("Log Out", key="global_logout_btn", width='stretch'): 
        st.session_state.observer_id = None
        st.session_state.env_gate_synced = False
        st.rerun()
    st.sidebar.divider()

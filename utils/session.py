"""
=============================================================================
Module:        utils/session.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35, §36]
Upstream:      app.py, vault_views/0_Login.py
Downstream:    utils.db, utils.bootstrap
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, session_id)
Outputs:       session_log, system_log
Description:   Session management, Session ID recovery, and Admin Handshake.
=============================================================================
"""

import streamlit as st
import uuid
import os
from datetime import datetime, timedelta, timezone
from utils.db import get_supabase
from utils.bootstrap import get_resilient_table, VERSION
from utils.logger import logger


def init_session():
    """Initializes the browser session state."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"🆕 New System Session Initialized: {st.session_state.session_id}")

    if "observer_id" not in st.session_state:
        st.session_state.observer_id = None

    if "observer_name" not in st.session_state:
        st.session_state.observer_name = "Guest"

    if "env_gate_synced" not in st.session_state:
        st.session_state.env_gate_synced = False


@st.cache_data(ttl=600)
def fetch_active_observers():
    """Fetches the list of active observers from Supabase, cached for 10 minutes."""
    try:
        supabase_client = get_supabase()
        response = (
            supabase_client.table("observer")
            .select("observer_id, display_name, is_active")
            .eq("is_active", True)
            .execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch observers: {e}")
        return []


def show_splash_screen():
    # Initialize client early to prevent NameError in exception blocks Standard §36
    supabase_client = get_supabase()

    # Render static Welcome message FIRST for instant feedback
    st.markdown(
        f"""<div style='
            text-align: center;
            padding: 6vh 2rem 1rem 2rem;
            max-width: 480px;
            margin: 0 auto;
        '>
        <h1 style='color: #10B981; margin-bottom: 0.4rem;'>🐢 Welcome!</h1>
        <p style='color: #94A3B8; margin: 0.2rem 0;'>Let's get started. Who is working today?</p>
        <p style='color: #94a3b8; font-size: 0.78em; margin-top: 0.6rem; letter-spacing: 0.04em;'>Clinical Standard {VERSION}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Use cached data to eliminate DB latency on repeated loads
    active_observers = fetch_active_observers()

    if not active_observers:
        st.error("No active observers found in registry or connection failed.")
        st.stop()

    try:
        columns = st.columns([1, 2, 1])
        with columns[1]:
            with st.form("login_form"):

                observer_options = {
                    f"{o['display_name']}": o["observer_id"] for o in active_observers
                }

                last_user_record = ""
                try:
                    if os.path.exists("tmp/last_user.txt"):
                        with open("tmp/last_user.txt", "r") as file:
                            last_user_record = file.read().strip()
                except:
                    pass

                names_list = list(observer_options.keys())
                default_index = 0
                for i, name in enumerate(names_list):
                    if last_user_record in name:
                        default_index = i
                        break

                selected_observer = st.selectbox(
                    "Select Your Name", options=names_list, index=default_index
                )

                if st.form_submit_button("START", use_container_width=True, key="login_start"):
                    chosen_oid = observer_options[selected_observer]
                    st.session_state.observer_id = chosen_oid

                    st.session_state.observer_name = selected_observer.split(" (")[0]

                    try:
                        os.makedirs("tmp", exist_ok=True)
                        with open("tmp/last_user.txt", "w") as file:
                            file.write(selected_observer)
                    except:
                        pass

                    current_generated_id = str(uuid.uuid4())
                    resuming_user_name = None

                    try:
                        # Standard §36: Within 4 hours? Resume personal last session.
                        last_session_query = (
                            supabase_client.table("session_log")
                            .select("*")
                            .eq("user_name", st.session_state.observer_name)
                            .order("login_timestamp", desc=True)
                            .limit(1)
                            .execute()
                        )
                        if last_session_query.data:
                            last_timestamp = datetime.fromisoformat(
                                last_session_query.data[0]["login_timestamp"].replace(
                                    "Z", "+00:00"
                                )
                            )
                            # Standard §36: Within 4 hours? Resume only if NOT terminated.
                            is_terminated = False
                            try:
                                term_res = supabase_client.table("system_log").select("id").eq("session_id", last_session_query.data[0]["session_id"]).eq("event_type", "TERMINATE").execute()
                                if term_res.data:
                                    is_terminated = True
                            except:
                                pass

                            diff = datetime.now(timezone.utc) - last_timestamp
                            if diff <= timedelta(hours=4) and not is_terminated:

                                # SUCCESS: Resume session
                                current_generated_id = last_session_query.data[0]["session_id"]
                                st.session_state.session_id = current_generated_id
                                
                                # CR-20260423-111948: Standardized audit vocabulary
                                st.success(f"✅ **Session resumed**: Welcome back, {st.session_state.observer_name}.")
                                st.info("💡 **Note**: If you just switched back from another app, your last recorded action is saved in the **Activity Log**.")
                                
                                resuming_user_name = last_session_query.data[0][
                                    "user_name"
                                ]
                                logger.warning(
                                    f"🔄 Personal Resume: Adopting shift session {current_generated_id} for {resuming_user_name}"
                                )
                    except Exception as error:
                        logger.error(f"Personal recovery failed: {error}")

                    st.session_state.session_id = current_generated_id
                    
                    if resuming_user_name:
                        st.session_state.resume_notice = f"🔄 Session resumed: {resuming_user_name}"

                    try:
                        display_name = st.session_state.observer_name

                        get_resilient_table(supabase_client, "session_log").upsert(
                            {
                                "session_id": st.session_state.session_id,
                                "user_name": display_name,
                                "user_agent": "WINC Field App",
                            }
                        ).execute()
                    except Exception as e:
                        logger.error(f"Failed to log session: {e}")

                    try:
                        get_resilient_table(supabase_client, "system_log").insert(
                            {
                                "session_id": st.session_state.session_id,
                                "event_type": "ACCESS",
                                "event_message": f"Session started: {st.session_state.observer_name}",
                            }
                        ).execute()
                    except:
                        pass

                    st.rerun()
    except Exception as error:
        st.error(f"Vault Connection Failure: {error}")



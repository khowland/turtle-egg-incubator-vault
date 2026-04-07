import streamlit as st
from utils.db import get_supabase
import pandas as pd

st.set_page_config(page_title='Settings | WINC', page_icon='⚙️', layout='wide')

# Header with Logout
col1, col2 = st.columns([4, 1])
with col1:
    st.title("⚙️ Administrative Settings")
with col2:
    if st.button("🚪 Log Out", width='stretch'):
        st.session_state.observer_id = None
        st.rerun()
st.divider()

tab1, tab2, tab3 = st.tabs(["👥 Observer Registry", "🐢 Species Management", "📜 System Logs"])

supabase = get_supabase()

with tab1:
    st.subheader("Staff & Observer Registry")
    st.caption("Manage personnel access and roles. Uncheck 'Active' to perform a soft-delete.")

    try:
        # Fetch current observers
        response = supabase.table('observer').select('*').order('display_name').execute()
        observers = response.data
        df = pd.DataFrame(observers)

        if not df.empty:
            # CRUD - Edit/Update/Soft-Delete using Data Editor
            st.write("### Edit Registry")
            # Clean up columns for display
            display_df = df[['id', 'display_name', 'role', 'is_active']].copy()

            edited_df = st.data_editor(
                display_df, 
                column_config={
                    "id": None, # Hide ID
                    "display_name": st.column_config.TextColumn("Name", help="Display name of staff", required=True),
                    "role": st.column_config.SelectboxColumn("Role", options=["Staff", "Volunteer", "Lead Biologist", "Intern"], required=True),
                    "is_active": st.column_config.CheckboxColumn("Active Status", help="Uncheck to soft-delete")
                },
                disabled=["id"],
                width='stretch',
                num_rows="dynamic"
            )

            # Save Changes Logic
            if st.button("💾 Save Changes to Registry", width='stretch'):
                # Identify changes
                for index, row in edited_df.iterrows():
                    orig_row = display_df.iloc[index] if index < len(display_df) else None
                    if orig_row is not None:
                        # Update existing
                        if not row.equals(orig_row):
                            supabase.table('observer').update({
                                'display_name': row['display_name'],
                                'role': row['role'],
                                'is_active': row['is_active']
                            }).eq('id', row['id']).execute()

                # Handle Deletions (if any - though we prefer soft-delete via checkbox)
                st.success("Registry updated successfully!")
                st.rerun()

        st.divider()

        # Create: Add New Staff Member
        with st.expander("➕ Add New Staff Member"):
            with st.form("new_observer_form", clear_on_submit=True):
                new_name = st.text_input("Full Name")
                new_role = st.selectbox("Role", ["Staff", "Volunteer", "Lead Biologist", "Intern"])
                if st.form_submit_button("Register New Staff", width='stretch'):
                    if new_name:
                        supabase.table('observer').insert({
                            'display_name': new_name, 
                            'role': new_role, 
                            'is_active': True
                        }).execute()
                        st.success(f"Registered {new_name}!")
                        st.rerun()
                    else:
                        st.error("Name is required")

    except Exception as e:
        st.error(f"Database connection error: {e}")

with tab2:
    st.subheader("Biological Lookup Tables")
    st.info("🚧 Species management (Blanding's, Wood, etc.) is currently hardcoded and will be moved to the database in v6.6.")

with tab3:
    st.subheader("Vault Audit Trail (Last 50 Events)")
    try:
        logs = supabase.table('systemlog').select('*').order('created_at', desc=True).limit(50).execute().data
        if logs:
            st.dataframe(pd.DataFrame(logs), width='stretch')
        else:
            st.info("No system logs found.")
    except:
        st.info("SystemLog table not yet initialized or accessible.")

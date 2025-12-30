import streamlit as st
import os

# Set page config FIRST
st.set_page_config(
    page_title="QuickPoll",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Init System
if 'db_initialized' not in st.session_state:
    from core.database import init_db
    init_db()
    st.session_state.db_initialized = True

# Router Logic
params = st.query_params
poll_id = params.get("poll")

# Main Routing
if poll_id:
    # --- VOTER MODE ---
    from views.voter_ui import render_voter_app
    try:
        render_voter_app(int(poll_id))
    except ValueError:
        st.error("Invalid Poll ID")
else:
    # --- ADMIN MODE ---
    from views.admin_ui import render_admin_page
    render_admin_page()

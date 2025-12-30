import streamlit as st
import hashlib
import os

ADMIN_PASSWORD = "admin123"

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login():
    """Verify login status from Session or Persistent Query Param"""
    # 1. Check Session
    if st.session_state.get('authenticated', False):
        return True
    
    # 2. Check Query Params (Auto-login)
    params = st.query_params
    token = params.get('auth')
    if token == hash_pass(ADMIN_PASSWORD):
        st.session_state['authenticated'] = True
        return True
        
    return False

def login_user(password, remember=False):
    if password == ADMIN_PASSWORD:
        st.session_state['authenticated'] = True
        if remember:
            st.query_params['auth'] = hash_pass(ADMIN_PASSWORD)
        return True
    return False

def logout_user():
    st.session_state['authenticated'] = False
    st.query_params.clear()

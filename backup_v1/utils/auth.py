"""
QuickPoll Authentication Module
Simple password-based admin authentication
"""

import os
import streamlit as st
import hashlib

# Default admin password (can be overridden by environment variable)
DEFAULT_PASSWORD = "admin123"


def get_admin_password() -> str:
    """Get admin password from environment or use default"""
    return os.environ.get('ADMIN_PASSWORD', DEFAULT_PASSWORD)


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str) -> bool:
    """Check if provided password matches admin password"""
    return password == get_admin_password()


def is_authenticated() -> bool:
    """Check if user is authenticated in current session or via query params"""
    # 1. Check Session State
    if st.session_state.get('admin_authenticated', False):
        return True
    
    # 2. Check Query Params (for persistent login)
    params = st.query_params
    auth_token = params.get("auth", None)
    if auth_token:
        # Simple hash check (In production, use secure token)
        expected_hash = hash_password(get_admin_password())
        if auth_token == expected_hash:
            st.session_state['admin_authenticated'] = True
            return True
            
    return False


def login(password: str, remember: bool = False) -> bool:
    """Attempt to login with provided password"""
    if check_password(password):
        st.session_state['admin_authenticated'] = True
        
        if remember:
            # Set query param for persistence
            token = hash_password(get_admin_password())
            st.query_params["auth"] = token
        
        return True
    return False

def logout():
    """Logout current admin session"""
    st.session_state['admin_authenticated'] = False
    # Clear query param
    st.query_params.clear()


def require_auth():
    """Decorator-like function to require authentication"""
    if not is_authenticated():
        st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนใช้งาน")
        return False
    return True


def render_login_form() -> bool:
    """Render login form in sidebar and return auth status"""
    with st.sidebar:
        st.markdown("### 🔐 เข้าสู่ระบบผู้ดูแล")
        
        if is_authenticated():
            st.success("✅ เข้าสู่ระบบแล้ว")
            if st.button("🚪 ออกจากระบบ", use_container_width=True):
                logout()
                st.rerun()
            return True
        else:
            password = st.text_input("รหัสผ่าน", type="password", key="admin_password")
            remember = st.checkbox("จำการเข้าสู่ระบบ (Keep me logged in)")
            
            if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
                if login(password, remember):
                    st.success("✅ เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ รหัสผ่านไม่ถูกต้อง")
            return False

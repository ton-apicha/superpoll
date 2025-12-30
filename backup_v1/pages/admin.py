"""
QuickPoll Admin Panel
Desktop-focused administration interface
"""

import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import base64
import time
import random
import os
import json
from utils.database import (
    create_campaign, get_campaign, get_all_campaigns, update_campaign,
    delete_campaign, toggle_campaign_status, create_question, get_questions,
    update_question, delete_question, get_response_count, get_responses,
    get_vote_statistics, get_demographic_breakdown, export_responses_data,
    DEMOGRAPHIC_OPTIONS
)
from utils.auth import render_login_form, is_authenticated
from utils.charts import (
    create_pie_chart, create_bar_chart, create_demographic_bar_chart,
    create_live_counter
)


def generate_qr_code(url: str) -> str:
    """Generate QR code and return as base64 image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def init_theme():
    """Initialize theme in session state"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True  # Default to dark mode


def toggle_theme():
    """Toggle between dark and light mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode


def render_theme_toggle():
    """Render theme toggle button"""
    init_theme()
    is_dark = st.session_state.dark_mode
    
    icon = "🌙 โหมดมืด" if is_dark else "☀️ โหมดสว่าง"
    if st.button(icon, key="admin_theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()


def render_admin_styles():
    """Apply admin panel CSS styles with Standard Slate Design System"""
    init_theme()
    is_dark = st.session_state.dark_mode
    
    # Standard Design System Tokens (Slate Theme)
    if is_dark:
        # DARK MODE PALETTE
        c = {
            'bg_app': '#0f172a',        # Slate 900
            'bg_content': '#1e293b',    # Slate 800
            'bg_card': '#1e293b',       # Slate 800
            'bg_sidebar': '#1e293b',    # Slate 800
            'bg_input': '#334155',      # Slate 700
            
            'text_main': '#f8fafc',     # Slate 50
            'text_sub': '#cbd5e1',      # Slate 300
            'text_muted': '#94a3b8',    # Slate 400
            
            'border': '#334155',        # Slate 700
            'primary': '#3b82f6',       # Blue 500
            'primary_hover': '#2563eb', # Blue 600
        }
    else:
        # LIGHT MODE PALETTE
        c = {
            'bg_app': '#f1f5f9',        # Slate 100
            'bg_content': '#ffffff',    # White
            'bg_card': '#ffffff',       # White
            'bg_sidebar': '#f8fafc',    # Slate 50
            'bg_input': '#ffffff',      # White
            
            'text_main': '#0f172a',     # Slate 900
            'text_sub': '#334155',      # Slate 700
            'text_muted': '#64748b',    # Slate 500
            
            'border': '#e2e8f0',        # Slate 200
            'primary': '#2563eb',       # Blue 600
            'primary_hover': '#1d4ed8', # Blue 700
        }
        
    st.markdown(f"""
    <style>
        /* --- GLOBAL RESET & TYPOGRAPHY --- */
        @import url('https://fonts.googleapis.com/css2?family=Internal:wght@400;600&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif, 'Sarabun', sans-serif;
            color: {c['text_main']};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {c['text_main']} !important;
            font-weight: 600 !important;
        }}
        
        p, label, span, div {{
            color: {c['text_sub']};
        }}
        
        .small-text, .text-muted {{
            color: {c['text_muted']} !important;
            font-size: 0.875rem;
        }}

        /* --- LAYOUT & BACKGROUND --- */
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {c['bg_app']} !important;
            background-image: none !important; /* Remove any default Streamlit gradient */
        }}
        
        /* Toolbar Styling */
        [data-testid="stToolbar"] {{
            background-color: {c['bg_app']} !important;
            color: {c['text_main']} !important;
            right: 2rem !important; /* Move it slightly so it doesn't stick to edge */
        }}
        
        [data-testid="stToolbar"] button {{
             color: {c['text_main']} !important;
        }}
        
        /* Header Decoration Removal */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
            background: transparent !important;
        }}
        
        .main .block-container {{
            background-color: transparent !important;
            max-width: 1200px;
            padding-top: 2rem;
        }}

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {{
            background-color: {c['bg_sidebar']} !important;
            border-right: 1px solid {c['border']} !important;
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: {c['text_sub']} !important;
        }}

        /* --- CARDS & CONTAINERS --- */
        /* Streamlit containers that act as cards */
        [data-testid="stForm"], .stExpander, div.css-1r6slb0 {{
            background-color: {c['bg_card']} !important;
            border: 1px solid {c['border']} !important;
            border-radius: 0.75rem !important;
            padding: 1.5rem !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }}
        
        /* Custom Classes */
        .card-box {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }}

        /* --- INPUTS & FORMS --- */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
            background-color: {c['bg_input']} !important;
            color: {c['text_main']} !important;
            border: 1px solid {c['border']} !important;
            border-radius: 0.5rem !important;
        }}
        
        .stSelectbox div[data-baseweb="select"]:hover {{
            border-color: {c['primary']} !important;
        }}

        .stSelectbox div[data-baseweb="popover"], .stSelectbox ul {{
            background-color: {c['bg_card']} !important;
            border: 1px solid {c['border']} !important;
        }}
        
        .stSelectbox li {{
            color: {c['text_main']} !important;
        }}
        
        /* --- BUTTONS --- */
        .stButton > button {{
            background-color: {c['bg_card']} !important;
            color: {c['primary']} !important;
            border: 1px solid {c['border']} !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            transition: all 0.2s;
        }}
        
        .stButton > button:hover {{
            background-color: {c['bg_app']} !important;
            border-color: {c['primary']} !important;
            color: {c['primary_hover']} !important;
        }}
        
        /* Primary Action Buttons */
        div[data-testid="stForm"] .stButton > button {{
            background-color: {c['primary']} !important;
            color: #ffffff !important;
            border: none !important;
        }}
        
        div[data-testid="stForm"] .stButton > button:hover {{
            background-color: {c['primary_hover']} !important;
            opacity: 0.9;
        }}

        /* --- METRICS --- */
        [data-testid="stMetricValue"] {{
            color: {c['text_main']} !important;
        }}
        
        [data-testid="stMetricLabel"] {{
             color: {c['text_muted']} !important;
        }}

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {{
            border-bottom: 2px solid {c['border']} !important;
            background-color: transparent !important;
            gap: 2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: {c['text_muted']} !important;
            border: none !important;
            padding-bottom: 0.5rem !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {c['primary']} !important;
            border-bottom: 2px solid {c['primary']} !important;
            font-weight: 600 !important;
        }}

        /* --- DATA EDITOR --- */
        [data-testid="stDataFrame"] {{
            border: 1px solid {c['border']} !important;
            border-radius: 0.5rem !important;
        }}

        /* --- UTILS --- */
        hr {{
            border-color: {c['border']} !important;
            margin: 2rem 0 !important;
        }}
        
        .admin-header {{
            background: linear-gradient(to right, #2563eb, #4f46e5);
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            color: white !important;
        }}
        
        .admin-header h2, .admin-header p {{
            color: white !important;
        }}

    </style>
    """, unsafe_allow_html=True)



def get_theme_colors():
    """Get current theme colors based on Standard Slate Design System"""
    init_theme()
    is_dark = st.session_state.dark_mode
    
    if is_dark:
        return {
            'bg_primary': '#0f172a',    # Slate 900
            'bg_secondary': '#1e293b',  # Slate 800
            'card_bg': '#1e293b',       # Slate 800
            'text_primary': '#f8fafc',  # Slate 50
            'text_secondary': '#cbd5e1', # Slate 300
            'text_muted': '#94a3b8',    # Slate 400
            'border_color': '#334155',  # Slate 700
            'is_dark': True
        }
    else:
        return {
            'bg_primary': '#f1f5f9',    # Slate 100
            'bg_secondary': '#ffffff',  # White
            'card_bg': '#ffffff',       # White
            'text_primary': '#0f172a',  # Slate 900
            'text_secondary': '#334155', # Slate 700
            'text_muted': '#64748b',    # Slate 500
            'border_color': '#e2e8f0',  # Slate 200
            'is_dark': False
        }


def render_campaign_list():
    """Render list of all campaigns"""
    st.markdown("## 📋 รายการแคมเปญ")
    
    campaigns = get_all_campaigns()
    theme = get_theme_colors()
    
    if not campaigns:
        st.info("ยังไม่มีแคมเปญ คลิก 'สร้างแคมเปญใหม่' เพื่อเริ่มต้น")
        return
    
    for campaign in campaigns:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                status_class = "status-active" if campaign['is_active'] else "status-inactive"
                status_text = "เปิดรับโหวต" if campaign['is_active'] else "ปิดรับโหวต"
                st.markdown(f"""
                <div style="
                    background: {theme['card_bg']};
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px {'rgba(0,0,0,0.3)' if theme['is_dark'] else 'rgba(0,0,0,0.08)'};
                    margin: 12px 0;
                    border-left: 4px solid #667eea;
                ">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <h3 style="margin: 0; color: {theme['text_primary']};">{campaign['title']}</h3>
                        <span class="{status_class}">{status_text}</span>
                    </div>
                    <p style="color: {theme['text_muted']}; margin: 0; font-size: 14px;">
                        {campaign.get('description', 'ไม่มีคำอธิบาย')}
                    </p>
                    <p style="color: {theme['text_muted']}; margin: 8px 0 0 0; font-size: 12px;">
                        สร้างเมื่อ: {campaign['created_at']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                vote_count = get_response_count(campaign['id'])
                st.metric("📊 ผู้ตอบ", f"{vote_count:,}")
            
            with col3:
                if st.button("📝 จัดการ", key=f"manage_{campaign['id']}"):
                    st.session_state.admin_view = 'campaign_detail'
                    st.session_state.selected_campaign_id = campaign['id']
                    st.rerun()


def render_create_campaign():
    """Render campaign creation form"""
    st.markdown("## ➕ สร้างแคมเปญใหม่")
    
    with st.form("create_campaign_form"):
        title = st.text_input("ชื่อแคมเปญ *", placeholder="เช่น ผลสำรวจความคิดเห็น 2568")
        description = st.text_area("คำอธิบาย", placeholder="อธิบายรายละเอียดของแบบสอบถาม")
        
        st.markdown("### 📊 ข้อมูลประชากรที่ต้องการเก็บ")
        st.caption("เลือกข้อมูลที่ต้องการให้ผู้ตอบกรอก")
        
        demographics_config = {}
        cols = st.columns(3)
        for idx, (key, info) in enumerate(DEMOGRAPHIC_OPTIONS.items()):
            with cols[idx % 3]:
                demographics_config[key] = st.checkbox(info['label'], value=True, key=f"demo_{key}")
        
        show_results = st.checkbox("แสดงผลโหวตให้ผู้ตอบดูหลังส่งคำตอบ", value=False)
        
        submitted = st.form_submit_button("สร้างแคมเปญ", type="primary", use_container_width=True)
        
        if submitted:
            if not title.strip():
                st.error("กรุณากรอกชื่อแคมเปญ")
            else:
                campaign_id = create_campaign(
                    title=title.strip(),
                    description=description.strip(),
                    demographics_config=demographics_config
                )
                update_campaign(campaign_id, show_results=1 if show_results else 0)
                st.success(f"✅ สร้างแคมเปญ '{title}' สำเร็จ!")
                st.session_state.admin_view = 'campaign_detail'
                st.session_state.selected_campaign_id = campaign_id
                st.rerun()


def render_campaign_detail(campaign_id: int):
    """Render detailed campaign management view"""
    campaign = get_campaign(campaign_id)
    
    if not campaign:
        st.error("ไม่พบแคมเปญ")
        return
    
    # Header with campaign info (uses gradient so keeps white text)
    st.markdown(f"""
    <div class="admin-header">
        <h2 style="margin: 0; color: white;">📊 {campaign['title']}</h2>
        <p style="opacity: 0.9; margin: 8px 0 0 0; color: white;">{campaign.get('description', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_text = "🔴 ปิดรับโหวต" if campaign['is_active'] else "🟢 เปิดรับโหวต"
        if st.button(status_text, use_container_width=True):
            toggle_campaign_status(campaign_id)
            st.rerun()
    
    with col2:
        if st.button("🔗 แชร์ลิงก์/QR", use_container_width=True):
            st.session_state.show_share_section = True
    
    with col3:
        if st.button("📥 Export CSV", use_container_width=True):
            export_data = export_responses_data(campaign_id)
            if export_data:
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "⬇️ ดาวน์โหลด CSV",
                    csv,
                    f"quickpoll_{campaign_id}_responses.csv",
                    "text/csv",
                    key="download_csv"
                )
            else:
                st.info("ยังไม่มีข้อมูลให้ดาวน์โหลด")
    
    with col4:
        if st.button("⬅️ กลับ", use_container_width=True):
            st.session_state.admin_view = 'campaign_list'
            st.rerun()
    
    # Share Section (Toggle)
    if st.session_state.get('show_share_section', False):
        st.info("🔗 แชร์แบบสอบถาม")
        
        config = load_config()
        base_url = config.get('base_url', 'http://localhost:8501')
        full_url = f"{base_url}/?poll={campaign_id}"
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**ลิงก์:**")
            st.code(full_url, language=None)
            
            # Simple Close Button
            if st.button("ปิดส่วนแชร์", key="close_share_section"):
                st.session_state.show_share_section = False
                st.rerun()

        with col2:
            st.markdown("**QR Code:**")
            # QR Code via API
            qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={full_url}"
            st.image(qr_api, width=200)
            st.caption("คลิกขวาที่รูปเพื่อบันทึก")
            
        st.markdown("---")
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📝 คำถาม", "📊 ผลสำรวจ", "🔍 วิเคราะห์เชิงลึก"])
    
    with tab1:
        render_question_builder(campaign_id)
    
    with tab2:
        render_results_dashboard(campaign_id)
    
    with tab3:
        render_cross_tabulation(campaign_id)


def get_image_options():
    """Get list of available images for dropdown"""
    uploads_dir = "static/uploads"
    if not os.path.exists(uploads_dir):
        return []
    
    files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    # Sort new files first
    files.sort(key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)
    
    # Return relative paths
    return [f"static/uploads/{f}" for f in files]

def render_question_builder(campaign_id: int):
    """Render question builder interface"""
    st.markdown("### ➕ เพิ่มคำถามใหม่")
    
    # Initialize session state for advanced mode
    if 'qb_advanced_mode' not in st.session_state:
        st.session_state.qb_advanced_mode = False
        
    on_change_mode = st.toggle("โหมดขั้นสูง (ใส่รูป/สี)", key="toggle_advanced_mode")
    
    if on_change_mode:
        st.info("💡 ในโหมดขั้นสูง คุณสามารถใส่ URL รูปภาพและเลือกสีพื้นหลังสำหรับแต่ละตัวเลือกได้")
        
        with st.expander("🖼️ อัพโหลดรูปภาพ (Helper)", expanded=False):
            uploaded_file = st.file_uploader("เลือกรูปภาพผู้สมัคร", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                # Save file
                file_ext = uploaded_file.name.split('.')[-1]
                stem = uploaded_file.name.rsplit('.', 1)[0]
                clean_stem = "".join([c for c in stem if c.isalnum() or c=='_']).lower()
                if not clean_stem: clean_stem = "candidate"
                
                file_name = f"{clean_stem}_{int(time.time())}.{file_ext}"
                save_path = f"static/uploads/{file_name}"
                
                os.makedirs("static/uploads", exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                rel_path = f"static/uploads/{file_name}"
                st.success(f"✅ อัพโหลดสำเร็จ! เลือกไฟล์ {file_name} ได้ในตารางด้านล่าง")
                st.image(save_path, width=100)
        
    with st.form("add_question_form"):
        question_text = st.text_input("คำถาม *", placeholder="เช่น ท่านจะเลือกผู้สมัครรายใด?")
        
        col1, col2 = st.columns(2)
        with col1:
            question_type = st.selectbox(
                "ประเภทคำถาม",
                options=['single', 'multi'],
                format_func=lambda x: "เลือกคำตอบเดียว (Radio)" if x == 'single' else "เลือกได้หลายข้อ (Checkbox)"
            )
        
        with col2:
            max_selections = st.number_input(
                "จำนวนที่เลือกได้สูงสุด",
                min_value=1,
                value=3,
                disabled=question_type == 'single'
            )
            
        if not on_change_mode:
            # Simple Mode
            options_text = st.text_area(
                "ตัวเลือก (แต่ละบรรทัดคือ 1 ตัวเลือก) *",
                placeholder="ตัวเลือก A\nตัวเลือก B\nตัวเลือก C"
            )
            options_data = options_text
        else:
            # Advanced Mode using Data Editor
            st.markdown("#### 📝 กำหนดตัวเลือก")
            # Default empty data
            default_data = [
                {"text": "ตัวเลือก 1", "image_url": None, "bg_color": "#ffffff"},
                {"text": "ตัวเลือก 2", "image_url": None, "bg_color": "#ffffff"},
            ]
            
            image_options = get_image_options()
            
            edited_df = st.data_editor(
                default_data,
                column_config={
                    "text": st.column_config.TextColumn(
                        "ข้อความตัวเลือก *",
                        help="สิ่งที่ผู้ตอบแบบสอบถามจะเห็น",
                        required=True,
                        width="medium"
                    ),
                    "image_url": st.column_config.SelectboxColumn(
                        "URL รูปภาพ",
                        help="เลือกรูปภาพที่อัพโหลดไว้",
                        width="medium",
                        options=image_options,
                        required=False
                    ),
                    "bg_color": st.column_config.TextColumn(
                        "สีพื้นหลัง (Hex Code)",
                        help="ใส่รหัสสีเช่น #ff0000 หรือ #3b82f6",
                        width="medium",
                        validate="^#[0-9a-fA-F]{6}$"
                    ),
                },
                num_rows="dynamic",
                key="advanced_options_editor"
            )
            options_data = edited_df

        submitted = st.form_submit_button("เพิ่มคำถาม", type="primary")
        
        if submitted:
            if not question_text.strip():
                st.error("กรุณากรอกคำถาม")
                return

            final_options = []
            if not on_change_mode:
                if not options_data.strip():
                     st.error("กรุณากรอกตัวเลือก")
                     return
                final_options = [opt.strip() for opt in options_data.strip().split('\n') if opt.strip()]
            else:
                for row in options_data:
                    if row.get('text') and str(row.get('text')).strip():
                        final_options.append({
                            'text': str(row.get('text')).strip(),
                            'image_url': row.get('image_url') if row.get('image_url') else None,
                            'bg_color': row.get('bg_color')
                        })
            
            if len(final_options) < 2:
                st.error("กรุณากรอกตัวเลือกอย่างน้อย 2 ตัวเลือก")
            else:
                create_question(
                    campaign_id=campaign_id,
                    question_text=question_text.strip(),
                    question_type=question_type,
                    max_selections=max_selections if question_type == 'multi' else 1,
                    options=final_options
                )
                st.success("✅ เพิ่มคำถามสำเร็จ!")
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 คำถามในแคมเปญ")
    
    questions = get_questions(campaign_id)
    
    if not questions:
        st.info("ยังไม่มีคำถาม")
        return
    
    for idx, question in enumerate(questions, 1):
        with st.container():
            is_dark = st.session_state.get('dark_mode', True)
            card_bg = "#2d3748" if is_dark else "#f8f9fa"
            text_color = "#ffffff" if is_dark else "#1e293b"
            muted_color = "#94a3b8" if is_dark else "#636e72"
            
            type_badge = "🔘 Single" if question['question_type'] == 'single' else "☑️ Multi"
            
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                # Helper to format options preview
                formatted_options = []
                for opt in question['options']:
                    opt_str = opt['option_text'][:20] + '...' if len(opt['option_text']) > 20 else opt['option_text']
                    extras = []
                    if opt.get('image_url'):
                        extras.append("🖼️")
                    if opt.get('bg_color'):
                        extras.append(f"<span style='color:{opt['bg_color']}'>■</span>")
                    
                    if extras:
                        opt_str += " " + " ".join(extras)
                    formatted_options.append(opt_str)

                st.markdown(f"""
                <div style="background: {card_bg}; padding: 16px; border-radius: 12px; margin: 8px 0;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <strong style="color: {text_color};">ข้อ {idx}.</strong>
                        <span style="background: {'#475569' if is_dark else '#e9ecef'}; color: {text_color}; padding: 2px 8px; border-radius: 8px; font-size: 12px;">{type_badge}</span>
                    </div>
                    <p style="margin: 0; color: {text_color};">{question['question_text']}</p>
                    <p style="color: {muted_color}; font-size: 13px; margin: 8px 0 0 0;">
                        ตัวเลือก: {', '.join(formatted_options)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✏️", key=f"edit_q_{question['id']}", help="แก้ไขคำถาม"):
                    st.session_state[f"editing_q_{question['id']}"] = True
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"del_q_{question['id']}", help="ลบคำถาม"):
                    delete_question(question['id'])
                    st.rerun()
            
            # Edit form (shown when editing)
            if st.session_state.get(f"editing_q_{question['id']}", False):
                with st.expander(f"✏️ แก้ไขคำถามข้อ {idx}", expanded=True):
                    
                    # Image Helper
                    with st.expander("🖼️ อัพโหลดรูปภาพ (Helper)", expanded=False):
                        uploaded_file = st.file_uploader(f"เลือกรูปภาพ ({question['id']})", type=['png', 'jpg', 'jpeg'], key=f"up_img_{question['id']}")
                        if uploaded_file:
                            file_ext = uploaded_file.name.split('.')[-1]
                            file_name = f"candidate_edit_{question['id']}_{int(time.time())}.{file_ext}"
                            save_path = f"static/uploads/{file_name}"
                            with open(save_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            rel_path = f"static/uploads/{file_name}"
                            st.success("✅ อัพโหลดสำเร็จ!")
                            st.text_input(
                                "Copy Path นี้ไปใส่ในตาราง", 
                                value=rel_path, 
                                key=f"path_show_{question['id']}_{int(time.time())}"
                            )
                            st.image(save_path, width=100)

                    with st.form(f"edit_q_form_{question['id']}"):
                        new_text = st.text_input(
                            "คำถาม",
                            value=question['question_text'],
                            key=f"edit_text_{question['id']}"
                        )
                        
                        new_type = st.selectbox(
                            "ประเภท",
                            options=['single', 'multi'],
                            index=0 if question['question_type'] == 'single' else 1,
                            format_func=lambda x: "Single Select" if x == 'single' else "Multi Select",
                            key=f"edit_type_{question['id']}"
                        )
                        
                        # Prepare data for editor
                        existing_data = []
                        for opt in question['options']:
                            existing_data.append({
                                "text": opt['option_text'],
                                "image_url": opt.get('image_url') if opt.get('image_url') else None,
                                "bg_color": opt.get('bg_color', '#ffffff')
                            })
                        
                        st.markdown("#### 📝 แก้ไขตัวเลือก")
                        image_options = get_image_options()
                        
                        edited_options = st.data_editor(
                            existing_data,
                            column_config={
                                "text": st.column_config.TextColumn(
                                    "ข้อความตัวเลือก *",
                                    required=True,
                                    width="medium"
                                ),
                                "image_url": st.column_config.SelectboxColumn(
                                    "URL รูปภาพ",
                                    width="medium",
                                    options=image_options,
                                    required=False
                                ),
                                "bg_color": st.column_config.TextColumn(
                                    "สีพื้นหลัง (Hex)",
                                    width="small",
                                    validate="^#[0-9a-fA-F]{6}$",
                                    help="เช่น #ff0000"
                                )
                            },
                            num_rows="dynamic",
                            key=f"edit_opts_editor_{question['id']}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 บันทึก", type="primary"):
                                final_options = []
                                for row in edited_options:
                                    if row.get('text') and str(row.get('text')).strip():
                                        final_options.append({
                                            'text': str(row.get('text')).strip(),
                                            'image_url': row.get('image_url') if row.get('image_url') else None,
                                            'bg_color': row.get('bg_color')
                                        })
                                
                                if len(final_options) >= 2:
                                    update_question(
                                        question['id'],
                                        question_text=new_text.strip(),
                                        question_type=new_type,
                                        options=final_options
                                    )
                                    st.session_state[f"editing_q_{question['id']}"] = False
                                    st.success("✅ บันทึกสำเร็จ!")
                                    st.rerun()
                                else:
                                    st.error("ต้องมีอย่างน้อย 2 ตัวเลือก")
                        
                        with col_cancel:
                            if st.form_submit_button("❌ ยกเลิก"):
                                st.session_state[f"editing_q_{question['id']}"] = False
                                st.rerun()


def render_results_dashboard(campaign_id: int):
    """Render real-time results dashboard using native Streamlit components"""
    # Live counter
    vote_count = get_response_count(campaign_id)
    st.markdown(create_live_counter(vote_count), unsafe_allow_html=True)
    
    st.markdown("")
    
    # Get statistics
    stats = get_vote_statistics(campaign_id)
    
    if stats['total_votes'] == 0:
        st.info("ยังไม่มีผู้ตอบแบบสอบถาม")
        return
    
    # Display results for each question using native components
    for q_stat in stats.get('questions', []):
        st.markdown("---")
        st.markdown(f"### {q_stat['text']}")
        
        # Sort options by count descending
        sorted_options = sorted(q_stat['options'], key=lambda x: x['count'], reverse=True)
        
        # Display as ranked list with progress bars
        for rank, opt in enumerate(sorted_options, 1):
            # Ranking badge
            if rank == 1:
                badge = "🥇"
                color = "#FFD700"
            elif rank == 2:
                badge = "🥈"
                color = "#C0C0C0"
            elif rank == 3:
                badge = "🥉"
                color = "#CD7F32"
            else:
                badge = f"#{rank}"
                color = "#6B7280"
            
            # Display row
            col1, col2, col3 = st.columns([1, 5, 1])
            
            with col1:
                st.markdown(f"<h2 style='text-align:center; margin:0;'>{badge}</h2>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{opt['text']}**")
                st.progress(opt['percentage'] / 100 if opt['percentage'] > 0 else 0.01)
            
            with col3:
                st.markdown(f"<h3 style='text-align:center; color:{color}; margin:0;'>{opt['percentage']}%</h3>", unsafe_allow_html=True)
                st.caption(f"{opt['count']} เสียง")
    
    # Add auto-refresh option
    st.markdown("---")
    auto_refresh = st.checkbox("🔄 รีเฟรชอัตโนมัติ (ทุก 30 วินาที)", key="auto_refresh_tab2")
    if auto_refresh:
        st.markdown("""
        <script>
            setTimeout(function() { window.location.reload(); }, 30000);
        </script>
        """, unsafe_allow_html=True)



def render_cross_tabulation(campaign_id: int):
    """Render cross-tabulation analysis interface using native Streamlit components"""
    st.markdown("### 🔍 กรอง/วิเคราะห์เชิงลึก (Cross-tabulation)")
    st.caption("เลือกกรองข้อมูลตามกลุ่มประชากร")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    filters = {}
    
    with col1:
        age_filter = st.selectbox(
            "ช่วงอายุ",
            options=["ทั้งหมด"] + DEMOGRAPHIC_OPTIONS['age_group']['options'],
            key="cross_age_filter"
        )
        if age_filter != "ทั้งหมด":
            filters['age_group'] = age_filter
    
    with col2:
        edu_filter = st.selectbox(
            "ระดับการศึกษา",
            options=["ทั้งหมด"] + DEMOGRAPHIC_OPTIONS['education']['options'],
            key="cross_edu_filter"
        )
        if edu_filter != "ทั้งหมด":
            filters['education'] = edu_filter
    
    with col3:
        region_filter = st.selectbox(
            "ภูมิภาค",
            options=["ทั้งหมด"] + DEMOGRAPHIC_OPTIONS['region']['options'],
            key="cross_region_filter"
        )
        if region_filter != "ทั้งหมด":
            filters['region'] = region_filter
    
    col4, col5 = st.columns(2)
    
    with col4:
        occ_filter = st.selectbox(
            "อาชีพ",
            options=["ทั้งหมด"] + DEMOGRAPHIC_OPTIONS['occupation']['options'],
            key="cross_occ_filter"
        )
        if occ_filter != "ทั้งหมด":
            filters['occupation'] = occ_filter
    
    with col5:
        income_filter = st.selectbox(
            "รายได้",
            options=["ทั้งหมด"] + DEMOGRAPHIC_OPTIONS['income']['options'],
            key="cross_income_filter"
        )
        if income_filter != "ทั้งหมด":
            filters['income'] = income_filter
    
    st.markdown("---")
    
    # Get filtered statistics
    stats = get_vote_statistics(campaign_id, filters)
    
    # Show filter summary
    if filters:
        filter_text = ", ".join([f"{DEMOGRAPHIC_OPTIONS[k]['label']}: {v}" for k, v in filters.items()])
        st.markdown(f"**ตัวกรองที่ใช้:** {filter_text}")
    
    st.metric("ผู้ตอบที่ตรงเงื่อนไข", f"{stats['total_votes']:,} คน")
    
    if stats['total_votes'] == 0:
        st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
        return
    
    # Display results as tables with progress bars (no plotly)
    for q_stat in stats.get('questions', []):
        st.markdown("---")
        st.markdown(f"**{q_stat['text']}**")
        
        # Sort options by count descending
        sorted_options = sorted(q_stat['options'], key=lambda x: x['count'], reverse=True)
        
        for rank, opt in enumerate(sorted_options, 1):
            # Ranking badge
            if rank == 1:
                badge = "🥇"
            elif rank == 2:
                badge = "🥈"
            elif rank == 3:
                badge = "🥉"
            else:
                badge = f"#{rank}"
            
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.markdown(f"### {badge}")
            with col2:
                st.markdown(f"**{opt['text'][:40]}{'...' if len(opt['text']) > 40 else ''}**")
                st.progress(opt['percentage'] / 100)
            with col3:
                st.markdown(f"**{opt['percentage']}%**")
                st.caption(f"{opt['count']} เสียง")
    
    # Demographic breakdown using native bar chart
    st.markdown("---")
    st.markdown("### 📊 การกระจายตามกลุ่มประชากร")
    
    demo_field = st.selectbox(
        "เลือกข้อมูลประชากรที่ต้องการดู",
        options=list(DEMOGRAPHIC_OPTIONS.keys()),
        format_func=lambda x: DEMOGRAPHIC_OPTIONS[x]['label'],
        key="cross_demo_field"
    )
    
    breakdown = get_demographic_breakdown(campaign_id, demo_field)
    
    if breakdown and breakdown.get('data'):
        # Convert to DataFrame for st.bar_chart
        import pandas as pd
        df = pd.DataFrame(breakdown['data'])
        df = df.set_index('value')
        st.bar_chart(df['count'])
    else:
        st.info("ยังไม่มีข้อมูล")

def render_media_gallery():
    """Render media gallery for bulk upload and management"""
    st.markdown("## 🖼️ คลังรูปภาพ (Media Gallery)")
    
    # 1. Bulk Upload
    with st.expander("📤 อัพโหลดรูปภาพใหม่", expanded=True):
        uploaded_files = st.file_uploader(
            "เลือกรูปภาพ (เลือกได้หลายไฟล์)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button(f"บันทึก {len(uploaded_files)} รูปภ่าพ", type="primary"):
                os.makedirs("static/uploads", exist_ok=True)
                count = 0
                for up_file in uploaded_files:
                    file_ext = up_file.name.split('.')[-1]
                    # Keep original filename stem but append timestamp to avoid collisions
                    stem = up_file.name.rsplit('.', 1)[0]
                    # Clean filename (keep only alphanumeric and underscore)
                    clean_stem = "".join([c for c in stem if c.isalnum() or c=='_']).lower()
                    if not clean_stem: clean_stem = "file"
                    
                    file_name = f"{clean_stem}_{int(time.time())}_{random.randint(1000,9999)}.{file_ext}"
                    save_path = f"static/uploads/{file_name}"
                    
                    with open(save_path, "wb") as f:
                        f.write(up_file.getbuffer())
                    count += 1
                
                st.success(f"✅ อัพโหลดสำเร็จ {count} ไฟล์!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    
    # 2. Gallery Grid
    st.markdown("### 📂 รูปภาพทั้งหมด")
    
    uploads_dir = "static/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)
    
    if not files:
        st.info("ยังไม่มีรูปภาพในคลัง")
        return
        
    # pagination
    cols = 4
    rows = len(files) // cols + 1
    
    for i in range(0, len(files), cols):
        cols_ui = st.columns(cols)
        for j in range(cols):
            if i + j < len(files):
                f_name = files[i+j]
                f_path = os.path.join(uploads_dir, f_name)
                rel_path = f"{uploads_dir}/{f_name}"
                
                with cols_ui[j]:
                    with st.container(): # Use container card style
                        st.image(f_path, use_container_width=True)
                        st.text_input("Path", value=rel_path, key=f"gal_path_{f_name}", label_visibility="collapsed")
                        st.caption(f_name)


def load_config():
    """Load configuration from file"""
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except:
            pass
    return {"base_url": "http://localhost:8501"}

def save_config(config):
    """Save configuration to file"""
    with open('config.json', 'w') as f:
        json.dump(config, f)

def render_settings():
    """Render settings page"""
    st.markdown("## ⚙️ ตั้งค่าระบบ (Settings)")
    
    config = load_config()
    
    with st.form("settings_form"):
        st.info("ℹ️ กำหนด URL หลักของระบบเพื่อใช้ในการสร้าง QR Code ให้ผู้อื่นสแกน")
        
        base_url = st.text_input(
            "Base URL (IP หรือ Domain Name พร้อม Port)",
            value=config.get('base_url', 'http://localhost:8501'),
            help="เช่น http://192.168.1.100:8501 หรือ http://mysuperpoll.com"
        )
        
        if st.form_submit_button("💾 บันทึกการตั้งค่า", type="primary"):
            # Remove trailing slash
            if base_url.endswith('/'):
                base_url = base_url[:-1]
                
            new_config = {"base_url": base_url}
            save_config(new_config)
            st.success("✅ บันทึกเรียบร้อย!")
            time.sleep(1)
            st.rerun()

def render_admin_page():
    """Main admin page renderer"""
    render_admin_styles()
    
    # Check authentication
    authenticated = render_login_form()
    
    if not authenticated:
        theme = get_theme_colors()
        st.markdown(f"""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 64px; margin-bottom: 20px;">🔐</div>
            <h2 style="color: {theme['text_primary']};">QuickPoll Admin Panel</h2>
            <p style="color: {theme['text_muted']};">กรุณาเข้าสู่ระบบเพื่อจัดการแบบสอบถาม</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if authenticated:
        # Load theme
        theme = get_theme_colors()

        # Check query params for campaign view at start (if not handled by internal state)
        params = st.query_params
        campaign_id_param = params.get("campaign_id")
        
        # Sidebar Navigation
        with st.sidebar:
            st.markdown("### 📌 เมนูหลัก")
            admin_view_select = st.radio(
                "เลือกเมนูการทำงาน",
                options=["polls", "media", "settings"],
                key="admin_main_nav",
                format_func=lambda x: {
                    "polls": "📊 จัดการแบบสอบถาม",
                    "media": "🖼️ คลังรูปภาพ",
                    "settings": "⚙️ ตั้งค่า (QR Code)"
                }[x]
            )
            st.markdown("---")
            render_theme_toggle()

        # Routing based on Sidebar
        if admin_view_select == "media":
            render_media_gallery()
            
        elif admin_view_select == "settings":
            render_settings()
            
        else: # polls
            # Managing Polls View Logic
            if 'admin_view' not in st.session_state:
                 st.session_state.admin_view = 'campaign_list'
            
            # Handle deep linking if present and not already navigating
            if campaign_id_param and st.session_state.admin_view == 'campaign_list':
                try:
                    c_id = int(campaign_id_param)
                    st.session_state.admin_view = 'campaign_detail'
                    st.session_state.selected_campaign_id = c_id
                except:
                    pass

            # Render Poll Sub-views
            view = st.session_state.admin_view
            
            if view == 'campaign_list':
                render_campaign_list()
            elif view == 'create_campaign':
                render_create_campaign()
            elif view == 'campaign_detail':
                c_id = st.session_state.get('selected_campaign_id')
                if c_id:
                    render_campaign_detail(c_id)
                else:
                    render_campaign_list()

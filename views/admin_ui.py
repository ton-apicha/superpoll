import streamlit as st
import pandas as pd
import os
import json
import time
import random
from datetime import datetime

# Core Modules
from core.database import (
    create_campaign, get_campaign, get_all_campaigns, update_campaign,
    delete_campaign, toggle_campaign_status, create_question, get_questions,
    update_question, delete_question, get_results, get_response_count,
    export_responses_data, get_vote_statistics, get_demographic_breakdown,
    reset_responses, DEMOGRAPHIC_OPTIONS
)
from core.auth import check_login, login_user, logout_user

# Chart Helpers
from views.charts_helper import (
    create_pie_chart, create_bar_chart, create_demographic_bar_chart,
    create_live_counter
)

# --- Configuration Helpers ---
def load_config():
    if os.path.exists('config.json'):
         try:
             with open('config.json') as f: return json.load(f)
         except: pass
    return {"base_url": "http://localhost:8501"}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def get_image_options():
    uploads_dir = "static/uploads"
    if not os.path.exists(uploads_dir): return []
    files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)
    return [f"static/uploads/{f}" for f in files]

# --- Sub-Pages ---
def render_settings():
    st.markdown("## ⚙️ ตั้งค่าระบบ (Settings)")
    config = load_config()
    with st.form("settings_form"):
        st.info("ℹ️ กำหนด URL หลักของระบบเพื่อใช้ในการสร้าง QR Code")
        base_url = st.text_input("Base URL", value=config.get('base_url', 'http://localhost:8501'))
        if st.form_submit_button("💾 บันทึก", type="primary"):
            if base_url.endswith('/'): base_url = base_url[:-1]
            save_config({"base_url": base_url})
            st.success("บันทึกเรียบร้อย")
            time.sleep(1)
            st.rerun()

def render_media_gallery():
    st.markdown("## 🖼️ คลังรูปภาพ")
    
    # Upload
    with st.expander("📤 อัพโหลดรูปภาพใหม่", expanded=True):
        uploaded_files = st.file_uploader("เลือกรูปภาพ", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if uploaded_files and st.button(f"บันทึก {len(uploaded_files)} รูป"):
            os.makedirs("static/uploads", exist_ok=True)
            for up in uploaded_files:
                ext = up.name.split('.')[-1]
                stem = "".join([c for c in up.name.rsplit('.',1)[0] if c.isalnum()]).lower() or "img"
                fname = f"{stem}_{int(time.time())}.{ext}"
                with open(f"static/uploads/{fname}", "wb") as f: f.write(up.getbuffer())
            st.success("✅ อัพโหลดสำเร็จ")
            st.rerun()
            
    # Gallery
    st.markdown("### 📂 รูปภาพทั้งหมด")
    images = get_image_options() # returns paths
    if not images:
        st.info("ว่างเปล่า")
        return
        
    cols = 4
    for i in range(0, len(images), cols):
        c = st.columns(cols)
        for j in range(cols):
            if i+j < len(images):
                with c[j]:
                    st.image(images[i+j], use_container_width=True)
                    st.text_input("Path", value=images[i+j], key=f"img_{i+j}", label_visibility="collapsed")

# --- Campaign Detail Views ---
def render_question_builder(campaign_id):
    # State for Editing
    if 'edit_q_id' not in st.session_state: st.session_state.edit_q_id = None
    
    # 1. Prepare Data for Form (Default or Edit Mode)
    form_title = "➕ เพิ่มคำถามใหม่"
    btn_text = "เพิ่มคำถาม"
    current_q = None
    
    # Defaults
    d_text = ""
    d_type = "single"
    d_max = 1
    d_adv = False
    d_opts_simple = ""
    d_opts_adv = [{"text": f"ตัวเลือก {i}", "image_url": None, "bg_color": "#ffffff"} for i in range(1,3)]

    # If Editing, Load Data
    if st.session_state.edit_q_id:
        qs = get_questions(campaign_id)
        current_q = next((q for q in qs if q['id'] == st.session_state.edit_q_id), None)
        if current_q:
            form_title = f"✏️ แก้ไขคำถาม: {current_q['question_text']}"
            btn_text = "บันทึกการแก้ไข"
            d_text = current_q['question_text']
            d_type = current_q['question_type']
            d_max = current_q['max_selections']
            
            # Map Options
            # We assume if ANY option has image/color, it's Advanced Mode
            is_adv = any(o.get('image_url') or o.get('bg_color') for o in current_q['options'])
            d_adv = is_adv
            
            if is_adv:
                d_opts_adv = []
                for o in current_q['options']:
                    d_opts_adv.append({
                        "text": o['option_text'],
                        "image_url": o.get('image_url'),
                        "bg_color": o.get('bg_color') or "#ffffff"
                    })
            else:
                d_opts_simple = "\n".join([o['option_text'] for o in current_q['options']])

    st.markdown(f"### {form_title}")
    

    # Toggle Advanced Mode (Pre-set if editing)
    adv_mode = st.toggle("โหมดขั้นสูง (ใส่รูป/สี)", value=d_adv, key="adv_mode_toggle")
    
    # --- NO FORM WRAPPER (To allow real-time image preview) ---
    
    q_text = st.text_input("คำถาม *", value=d_text)
    c1, c2 = st.columns(2)
    q_type = c1.selectbox("ประเภท", ["single", "multi"], index=0 if d_type=="single" else 1)
    max_sel = c2.number_input("จำนวนที่เลือกได้สูงสุด", 1, 10, d_max, disabled=q_type=='single')
    
    final_opts_data = [] # To store result dicts
    
    if not adv_mode:
        # Simple Mode
        s_text = st.text_area("ตัวเลือก (บรรทัดละ 1 ข้อ)", value=d_opts_simple, placeholder="A\nB\nC", height=150)
        # Parse immediately
        lines = [l.strip() for l in s_text.split('\n') if l.strip()]
        for l in lines: final_opts_data.append({'text': l})
        
    else:
        # Advanced Mode - Dynamic Rows
        st.info("💡 สามารถเลือกรูปภาพและสีพื้นหลังได้")
        
        # State to track number of rows (init with existing or 2)
        if 'adv_rows_count' not in st.session_state: 
            st.session_state.adv_rows_count = len(d_opts_adv) if d_opts_adv else 2

        # Initialize list in session state if not exists specifically for inputs
        # (This helps keep values during reruns)
        
        img_options = [""] + get_image_options() # Add empty option
        
        for i in range(st.session_state.adv_rows_count):
            st.markdown(f"**ตัวเลือกที่ {i+1}**")
            r1, r2, r3 = st.columns([3, 2, 1])
            
            # Default values for this row
            def_txt = d_opts_adv[i]['text'] if i < len(d_opts_adv) else ""
            def_img = d_opts_adv[i].get('image_url') if i < len(d_opts_adv) else None
            def_col = d_opts_adv[i].get('bg_color', '#ffffff') if i < len(d_opts_adv) else "#ffffff"
            
            # Text Input
            txt = r1.text_input(f"ข้อความ", value=def_txt, key=f"opt_txt_{i}", label_visibility="collapsed", placeholder=f"ข้อความตัวเลือก {i+1}")
            
            # Image Select & Preview
            img = r2.selectbox(f"รูปภาพ", img_options, index=img_options.index(def_img) if def_img in img_options else 0, key=f"opt_img_{i}", label_visibility="collapsed")
            
            # Color
            col = r3.color_picker(f"สี", value=def_col, key=f"opt_col_{i}", label_visibility="collapsed")
            
            # Show Preview Row
            if img:
                with r2:
                    st.image(img, width=100)

            final_opts_data.append({
                "text": txt,
                "image_url": img if img else None,
                "bg_color": col
            })
            st.markdown("---")
            
        # Add/Remove Row Buttons
        b1, b2 = st.columns(2)
        if b1.button("➕ เพิ่มตัวเลือก"):
            st.session_state.adv_rows_count += 1
            d_opts_adv.append({"text": "", "image_url": None, "bg_color": "#ffffff"}) # Push empty template
            st.rerun()
        if b2.button("➖ ลดตัวเลือก") and st.session_state.adv_rows_count > 2:
            st.session_state.adv_rows_count -= 1
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c_submit, c_cancel = st.columns([1, 4])
    
    submit = False
    with c_submit:
        submit = st.button(btn_text, type="primary", use_container_width=True)
    
    with c_cancel:
        if st.session_state.edit_q_id:
            if st.button("ยกเลิก", use_container_width=True):
                st.session_state.edit_q_id = None
                if 'adv_rows_count' in st.session_state: del st.session_state.adv_rows_count
                st.rerun()

    if submit:
        # Validate
        valid_opts = [o for o in final_opts_data if o.get('text')]
        
        if q_text and len(valid_opts) >= 2:
            if st.session_state.edit_q_id:
                # UPDATE
                update_question(st.session_state.edit_q_id, q_text, q_type, valid_opts)
                st.session_state.edit_q_id = None
                if 'adv_rows_count' in st.session_state: del st.session_state.adv_rows_count
                st.toast("✅ แก้ไขเรียบร้อย")
            else:
                # CREATE
                create_question(campaign_id, q_text, q_type, max_sel if q_type=='multi' else 1, valid_opts)
                st.toast("✅ เพิ่มคำถามแล้ว")
            
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("ข้อมูลไม่ครบถ้วน (ต้องมีชื่อคำถาม และอย่างน้อย 2 ตัวเลือกที่มีข้อความ)")
                
    # List Questions
    qs = get_questions(campaign_id)
    if qs:
        st.markdown("---")
        st.markdown("#### 📋 รายการคำถามที่มี")
        for q in qs:
            with st.container():
                # Highlight row if editing
                bg = "background-color: #f0f9ff; border-radius: 8px; padding: 10px;" if q['id'] == st.session_state.edit_q_id else ""
                
                c1, c2, c3 = st.columns([6,1,1])
                c1.markdown(f"**{q['question_text']}** <span style='color:grey; font-size:0.8em'>({q['question_type']})</span>", unsafe_allow_html=True)
                
                # Show simple preview
                opt_str = ", ".join([o['option_text'] for o in q['options']])
                if len(opt_str) > 50: opt_str = opt_str[:50] + "..."
                c1.caption(f"ตัวเลือก: {opt_str}")

                if c2.button("✏️", key=f"edit_{q['id']}", help="แก้ไข"):
                    st.session_state.edit_q_id = q['id']
                    st.rerun()
                
                if c3.button("🗑️", key=f"del_{q['id']}", help="ลบ"):
                    delete_question(q['id'])
                    # If deleted the one being edited, clear state
                    if st.session_state.edit_q_id == q['id']:
                        st.session_state.edit_q_id = None
                    st.rerun()
                
                st.markdown("---")

def render_results(campaign_id):
    count = get_response_count(campaign_id)
    st.markdown(create_live_counter(count), unsafe_allow_html=True)
    
    stats = get_vote_statistics(campaign_id)
    if not stats['questions']: return

    for q in stats['questions']:
        st.markdown(f"### {q['text']}")
        st.plotly_chart(create_bar_chart(q['text'], q['options']), use_container_width=True)

    st.markdown("---")
    with st.expander("🚨 โซนอันตราย (Danger Zone)"):
        st.warning("การล้างข้อมูลจะลบผลโหวตทั้งหมดของแคมเปญนี้ และไม่สามารถย้อนกลับได้")
        confirm = st.checkbox("ยืนยันว่าต้องการลบข้อมูลทั้งหมด")
        if st.button("🔥 ล้างข้อมูลและเริ่มเก็บใหม่", type="primary", disabled=not confirm):
            reset_responses(campaign_id)
            st.toast("✅ ล้างข้อมูลเรียบร้อยแล้ว")
            time.sleep(1)
            st.rerun()

def render_campaign_detail(campaign_id):
    camp = get_campaign(campaign_id)
    if not camp: return
    
    st.markdown(f"## 📊 {camp['title']}")
    
    # Actions
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🔴 ปิดรับ" if camp['is_active'] else "🟢 เปิดรับ", use_container_width=True):
            toggle_campaign_status(campaign_id)
            st.rerun()
    with c2:
        if st.button("🔗 แชร์", use_container_width=True):
            st.session_state.show_share = True
    with c3:
        if st.button("📥 CSV", use_container_width=True):
            data = export_responses_data(campaign_id)
            if data:
                df = pd.DataFrame(data)
                st.download_button("Download", df.to_csv(index=False).encode('utf-8-sig'), "data.csv", "text/csv")
    with c4:
        if st.button("⬅️ กลับ", use_container_width=True):
            st.query_params.clear()
            st.rerun()
            
    # Share Section
    if st.session_state.get('show_share'):
        st.info("Share Link")
        cfg = load_config()
        url = f"{cfg.get('base_url')}/?poll={campaign_id}"
        st.code(url)
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}", width=150)
        if st.button("ปิด"):
            st.session_state.show_share = False
            st.rerun()
        st.markdown("---")

    t1, t2 = st.tabs(["📝 คำถาม", "📊 ผลลัพธ์"])
    with t1: render_question_builder(campaign_id)
    with t2: render_results(campaign_id)

# --- Main Admin Page ---
def render_login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Login")
        pwd = st.text_input("Password", type="password")
        rem = st.checkbox("Remember Me")
        if st.button("Login", type="primary", use_container_width=True):
            if login_user(pwd, rem): st.rerun()
            else: st.error("Wrong password")

def render_admin_page():
    if not check_login():
        render_login_page()
        return
        
    with st.sidebar:
        st.success("Logged In")
        if st.button("Logout"):
            logout_user()
            st.rerun()
    
    # Router
    params = st.query_params
    if params.get('campaign_id'):
        render_campaign_detail(int(params.get('campaign_id')))
        return
        
    # Dashboard
    view = st.sidebar.radio("Menu", ["polls", "media", "settings"], 
         format_func=lambda x: {"polls":"📊 Polls", "media":"🖼️ Media", "settings":"⚙️ Settings"}[x])
         
    if view == "polls":
        # Create
        with st.expander("✨ New Poll"):
            with st.form("new_poll"):
                t = st.text_input("Title")
                d = st.text_area("Desc")
                if st.form_submit_button("Create") and t:
                    create_campaign(t, d)
                    st.rerun()
        
        # List
        camps = get_all_campaigns()
        for c in camps:
            with st.container():
                st.markdown(f"### {c['title']}")
                c1, c2 = st.columns([1,4])
                if c1.button("Manage", key=f"m_{c['id']}"):
                    st.query_params['campaign_id'] = c['id']
                    st.rerun()
            st.divider()

    elif view == "media":
        render_media_gallery()
    elif view == "settings":
        render_settings()

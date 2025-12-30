import streamlit as st
import time
import base64
import os
from core.database import get_campaign, get_questions, submit_response

def load_css():
    with open('assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def get_img_base64(path):
    """Convert local image to base64 string for embedding"""
    if not os.path.exists(path): return ""
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    # Determine mime type
    ext = path.split('.')[-1].lower()
    mime = "image/jpeg" if ext in ['jpg', 'jpeg'] else "image/png"
    return f"data:{mime};base64,{encoded_string}"

def render_finished():
    st.balloons()
    st.success("✅ บันทึกคะแนนโหวตเรียบร้อยแล้ว!")
    st.info("ขอบคุณที่ร่วมแสดงความคิดเห็น")
    if st.button("<< โหวตใหม่อีกครั้ง"):
        st.rerun()

def render_card_html(opt, is_selected, q_type):
    """Render HTML for Option Card"""
    
    # Styles config
    border = "3px solid #22c55e" if is_selected else "1px solid #e2e8f0"
    shadow = "0 10px 15px -3px rgba(0,0,0,0.1)" if is_selected else "0 1px 3px 0 rgba(0,0,0,0.1)"
    transform = "transform: scale(1.02);" if is_selected else ""
    
    # Check if candidate card (has image)
    raw_img = opt.get('image_url')
    has_image = bool(raw_img)
    bg_style = f"background: {opt.get('bg_color', '#ffffff')};" if opt.get('bg_color') else "background: white;"
    
    # Check text color (simple logic: dark bg -> white text)
    is_dark_bg = (opt.get('bg_color') or '').startswith('#') and opt.get('bg_color') != '#ffffff'
    text_color = "white" if is_dark_bg else "#0f172a"
    sub_text_color = "rgba(255,255,255,0.8)" if is_dark_bg else "#64748b"

    # Convert Image to Base64
    img_src = ""
    if has_image:
        img_src = get_img_base64(raw_img)

    # Prepare Indicator
    indicator = ""
    if is_selected:
        indicator = f"""
        <div style="
            background: #22c55e; color: white; width: 28px; height: 28px; 
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">✓</div>
        """

    html_content = ""
    card_key = ""

    if has_image and img_src:
        # --- CANDIDATE CARD (LARGE) ---
        html_content = f"""
        <div style="
            {bg_style} border-radius: 16px; padding: 16px; margin-bottom: 0px;
            display: flex; align-items: center; gap: 16px; position: relative;
            border: {border}; box-shadow: {shadow}; {transform} transition: all 0.2s;
            height: 100px;
        ">
            <div style="
                width: 70px; height: 70px; border-radius: 50%; 
                background-image: url('{img_src}'); background-size: cover; background-position: center;
                border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex-shrink: 0;
            "></div>
            
            <div style="flex: 1; min-width: 0;">
                <div style="
                    font-weight: 700; font-size: 1rem; color: {text_color}; 
                    line-height: 1.3;
                    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
                    overflow: hidden; white-space: normal;
                ">{opt['option_text']}</div>
            </div>
            
            <div style="flex-shrink: 0;">{indicator}</div>
        </div>
        """
        card_key = "large"
    else:
        # --- SIMPLE CARD (SMALL) ---
        html_content = f"""
        <div style="
            background: white; border-radius: 12px; padding: 12px 16px; margin-bottom: 0px;
            display: flex; align-items: center; gap: 12px; position: relative;
            border: {border}; box-shadow: {shadow}; {transform} transition: all 0.2s;
            min-height: 48px; /* Changed to min-height */
        ">
            <div style="
                flex: 1; font-weight: 500; color: #334155;
                font-size: 1rem; line-height: 1.3;
                word-wrap: break-word;
            ">{opt['option_text']}</div>
            <div style="flex-shrink: 0;">{indicator}</div>
        </div>
        """
        card_key = "small"

    # CRITICAL: Minify HTML to prevent Markdown code block interpretation
    return html_content.replace('\n', ' ').replace('    ', ' ').strip(), card_key

def render_voter_app(campaign_id):
    load_css()
    
    # State management
    if 'responses' not in st.session_state: st.session_state.responses = {}
    if 'current_step' not in st.session_state: st.session_state.current_step = 0
    
    campaign = get_campaign(campaign_id)
    if not campaign or not campaign['is_active']:
        st.error("⚠️ ไม่พบแบบสอบถาม หรือ ปิดรับความคิดเห็นแล้ว")
        return

    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="margin:0;">{campaign['title']}</h2>
        <p style="color: #64748b;">{campaign.get('description', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    questions = get_questions(campaign_id)
    
    # Process Questions
    # REMOVED FORM - Interactive Mode
    for q in questions:
        st.markdown(f"#### {q['question_text']}")
        if q['question_type'] == 'multi':
            st.caption(f"(เลือกได้สูงสุด {q['max_selections']} ข้อ)")
        
        selected_opts = st.session_state.responses.get(q['id'], [])
        if not isinstance(selected_opts, list): selected_opts = [selected_opts]

        for opt in q['options']:
            is_selected = opt['id'] in selected_opts
            
            # HTML Card
            html, card_type = render_card_html(opt, is_selected, q['question_type'])
            st.markdown(html, unsafe_allow_html=True)
            
            # Invisible Button Overlay - MARKER METHOD
            # 1. Place a marker div that CSS can target as "Next Sibling is my Button"
            marker_class = "btn-marker-large" if card_type == "large" else "btn-marker-small"
            st.markdown(f'<div class="{marker_class}"></div>', unsafe_allow_html=True)
            
            # 2. The Button (Will be moved UP by CSS to cover the card above)
            if st.button("Select", key=f"btn_{opt['id']}", use_container_width=True):
                # Toggle Logic
                if q['question_type'] == 'single':
                        st.session_state.responses[q['id']] = [opt['id']]
                else:
                        if opt['id'] in selected_opts:
                            selected_opts.remove(opt['id'])
                        else:
                            if len(selected_opts) < q['max_selections']:
                                selected_opts.append(opt['id'])
                        st.session_state.responses[q['id']] = selected_opts
                st.rerun()
            
        st.markdown("---")
    
    # Submit Button (Standard button now)
    if st.button("ส่งคำตอบ", type="primary", use_container_width=True):
        # Validate
        if len(st.session_state.responses) < len(questions):
            st.error("กรุณาตอบคำถามให้ครบทุกข้อ")
        else:
            submit_response(campaign_id, {}, st.session_state.responses)
            st.session_state.responses = {} # Reset
            st.session_state.finished = True
            st.rerun()

    if st.session_state.get('finished'):
        render_finished()
